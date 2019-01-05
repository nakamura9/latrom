
import random
import datetime
from decimal import Decimal as D
from functools import reduce
import reversion
from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel, SoftDeletionModel
import planner
import accounting
import invoicing
from employees.models.misc import EmployeesSettings
from employees.models.payroll_elements import (CommissionRule, 
                                                Allowance, 
                                                Deduction,
                                                PayrollTax)

class Payslip(models.Model):
    '''A model that defines the necessary features of a payslip
    handed to an employee at the end of each pay cycle.
    it is linked to hours worked and a particular employee and 
    is able to derive all the relevant pay information.

    properties
    -------------
    commission_pay - the amount paid out to an employee as commission for sales
    normal_pay - returns the income earned on the hourly rate of normal pay
    overtime_one_pay - returns total money earned in the first bracket of overtime
    overtime_two_pay - returns the total money earned in the second bracket of overtime
    
    gross_pay - returns the sum total of all the money earned from basic salaries,
        allowances and hourly pay
    non_tax_deductions - returns the sum of the money deducted from the Deduct objects as 
        part of a pay grade
     total_deductions - returns sum of PAYE and non_tax_deductions
     net_pay returns the difference between gross_pay and total_deductions
    '''
    start_period = models.DateField()
    end_period = models.DateField()
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)
    normal_hours = models.FloatField()
    overtime_one_hours = models.FloatField()
    overtime_two_hours = models.FloatField()
    pay_roll_id = models.IntegerField()
    pay_grade = models.ForeignKey('employees.paygrade', on_delete=models.SET_NULL, null=True, 
        default=1)
    pay_grade_version = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(choices=[
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('paid', 'Paid'),
        ], max_length=16,
        default='draft')
    entry = models.ForeignKey('accounting.journalentry', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True)

    @property 
    def paygrade_(self):
        all_versions = reversion.models.Version.objects.get_for_object(
            self.pay_grade)
        version =len(all_versions) -self.pay_grade_version
        
        return all_versions[version].field_dict
    
    def __str__(self):
        return str(self.employee) 
    

    @property
    def commission_pay(self):
        if not self.paygrade_['commission_id']:
            return 0
        commission = CommissionRule.objects.get(
            pk=self.paygrade_['commission_id'])
        if not commission:
            return 0
        
        elif not hasattr(self.employee, 'salesrepresentative'):
            return 0
        else:
            total_sales = self.employee.salesrepresentative.sales(
                self.start_period, 
                self.end_period)
            if total_sales < commission.min_sales:
                return 0

            commissionable_sales = total_sales - D(commission.min_sales)
  
            return (float(commission.rate) / 100.0) * float(commissionable_sales)

    @property 
    def normal_pay(self):
        return self.paygrade_['hourly_rate'] * self.normal_hours

    @property
    def overtime_one_pay(self):
        return self.paygrade_['overtime_rate'] * self.overtime_one_hours


    @property
    def overtime_two_pay(self):
        return self.paygrade_['overtime_two_rate'] * self.overtime_two_hours

    @property
    def overtime_pay(self):
        return self.overtime_one_pay + self.overtime_two_pay

    @property
    def total_allowances(self):
        total = 0
        for pk in self.paygrade_['allowances']:
            total += Allowance.objects.get(pk=pk).amount

        return total


    @property
    def tax_free_benefits(self):
        total = 0
        for pk in self.paygrade_['allowances']:
            allowance = Allowance.objects.get(pk=pk)
            if not allowance.taxable:
                total += allowance.amount

        return total

    @property
    def gross_pay(self):
        gross = self.paygrade_['monthly_salary']
        gross += self.normal_pay
        gross += self.overtime_one_pay
        gross += self.overtime_two_pay
        gross += self.total_allowances
        gross += self.commission_pay
        return gross

    @property 
    def taxable_gross_pay(self):
        return self.gross_pay - self.tax_free_benefits


    @property
    def non_tax_deductions(self):
        total = 0
        for pk in self.paygrade_['deductions']:
            deduction = Deduction.objects.get(pk=pk)
            total += deduction.deduct(self)
        
        return total

    @property
    def total_payroll_taxes(self):
        total = 0
        for pk in self.paygrade_['payroll_taxes']:
            tax = PayrollTax.objects.get(pk=pk)
            total += tax.tax(self.taxable_gross_pay)
        
        return total

    @property
    def allowances(self):
       return [
           Allowance.objects.get(pk=pk) for pk in self.paygrade_['allowances']
            ]

    
    @property
    def deductions(self):
        return [
         Deduction.objects.get(pk=pk) for pk in self.paygrade_['deductions']
            ]

    @property
    def calculated_payroll_taxes(self):
        taxes = [
            PayrollTax.objects.get(pk=pk) \
                for pk in self.paygrade_['payroll_taxes']
            ]
        return [
            {
                'name': tax.name,
                'amount': tax.tax(self.gross_pay)
            } for tax in taxes
        ]
            

    @property
    def total_deductions(self):
        return self.total_payroll_taxes + D(self.non_tax_deductions)

    @property
    def net_pay(self):
        return D(self.gross_pay) - D(self.total_deductions)

    def save(self, *args, **kwargs):
        is_new = self.pk is  None
        if not is_new:
            self.employee.leave_days += \
                self.paygrade_['monthly_leave_days']
            self.employee.save()
        
        super().save(*args, **kwargs)
        if self.pay_grade != self.employee.pay_grade \
                or is_new:
            self.pay_grade = self.employee.pay_grade
            revision_count = len(
                reversion.models.Version.objects.get_for_object(
                    self.pay_grade)
                    )
            self.pay_grade_version = revision_count
            self.save()

    def create_entry(self):
        '''This method updates the accounting system for payroll actions
        the selected account from settingsis deducted for all payments.
        deductions with specific accounts deposit into those accounts 
        payroll taxes deposit into their own account
        net income is deposited into account 5008
        '''
        settings = EmployeesSettings.objects.first()
        if settings.require_verification_before_posting_payslips and \
                self.status != 'verified':
            #only work on verified payslips
            return

        j = accounting.models.JournalEntry.objects.create(
                reference='PAYSLIP' + str(self.pk),
                memo= 'Auto generated entry from verified payslip.',
                date=datetime.date.today(),
                journal =accounting.models.Journal.objects.get(
                    pk=2),#Cash disbursements Journal
                created_by = settings.payroll_officer.user
        )
        j.debit(self.gross_pay, settings.payroll_account)
        j.credit(self.net_pay, 
            accounting.models.Account.objects.get(pk=5008))#salaries
        j.credit(self.total_payroll_taxes, 
            accounting.models.Account.objects.get(pk=5010))#payroll taxes
        
        for pk in self.paygrade_['deductions']:
            deduction = Deduction.objects.get(pk=pk)
            j.credit(deduction.deduct(self), deduction.account_paid_into)

        self.entry = j
        self.status = 'paid'
        self.save()