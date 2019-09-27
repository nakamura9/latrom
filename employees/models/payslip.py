
import random
import datetime
from decimal import Decimal as D
from functools import reduce
from django.db import models
from django.db.models import Q
import reversion
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
    pay_grade = models.ForeignKey('employees.paygrade', 
        on_delete=models.SET_NULL, 
        null=True, 
        default=1)
    created = models.DateTimeField(auto_now=True)
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
        '''versions of the model are stored in a queryset with the most recent first. e.g. [version 3, version 2, version 1]. On the other hand each payslip is assigned to a version number which is the number of versions of the. reversion returns a version queryset with limited slicing functionality that is why it is converted to a list first. '''

        all_versions = list(reversion.models.Version.objects.get_for_object(
            self.pay_grade))
        try:
            return all_versions[-self.pay_grade_version].field_dict
        except IndexError:
            return None 
        
    def __str__(self):
        return f'Payslip #{self.pk} for {self.employee}' 
    
    

    @property
    def commission_pay(self):
        if not self.paygrade_['commission_id']:
            return 0
        commission = CommissionRule.objects.get(
            pk=self.paygrade_['commission_id'])
        
        
        if not invoicing.models.SalesRepresentative.objects.filter(
                employee=self.employee).exists():
            return 0
        
        else:
            rep = invoicing.models.SalesRepresentative.objects.get(
                employee=self.employee)
            # sales only count for paid invoices
            total_sales = rep.sales(
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
    def tax_deductable_deductions(self):
        total = 0
        for deduction in self.deductions:
            if deduction.tax_deductable:
                total += deduction.deduct(self)

        return total

    @property
    def gross_pay(self):
        gross = self.paygrade_['salary']
        gross += self.normal_pay
        gross += self.overtime_one_pay
        gross += self.overtime_two_pay
        gross += self.total_allowances
        gross += self.commission_pay
        return gross

    @property 
    def taxable_gross_pay(self):
        '''
        Taxable gross income consists of gross earnings minus the 
        income from tax free benefits like some bonuses minus 
        deductions that are removed from income before the calculation of PAYE
        '''
        return self.gross_pay - self.tax_free_benefits - \
             self.tax_deductable_deductions


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
    def aids_levy(self):
        d = Deduction.objects.get(pk=3)
        return d.deduct(self)

    @property
    def aids_levy_and_taxes(self):
        return D(self.aids_levy) + self.total_payroll_taxes

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
    def calculated_deductions(self):
        return [{'name': d.name, 'amount': d.deduct(self)} for d in self.deductions]

    @property
    def calculated_payroll_taxes(self):
        taxes = [
            PayrollTax.objects.get(pk=pk) \
                for pk in self.paygrade_['payroll_taxes']
            ]
        return [
            {
                'name': tax.name,
                'amount': tax.tax(self.taxable_gross_pay)
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
            
            #make sure not paygrade is created without a revision
            revision_count = 0
            while True:
                revision_count = len(
                    reversion.models.Version.objects.get_for_object(
                        self.pay_grade)
                        )
                if revision_count < 1:
                    with reversion.create_revision():
                        self.pay_grade.save()
                else:
                    break 
            
            self.pay_grade_version = revision_count
            self.save()

    def create_verified_entry(self):
        '''
        A verified payslip sets up all the liabilites the company has towards its employees.
        When the payslip, only the salaries liability is removed, the ones to 
        ZIMRA NSSA etc remain.
        Each is settled separately
        '''
        settings = EmployeesSettings.objects.first()
        
        
        j = accounting.models.JournalEntry.objects.create(
                memo= f'Auto generated entry to verify '
                      f'payslip #{self.pk}.',
                date=datetime.date.today(),
                journal =accounting.models.Journal.objects.get(
                    pk=5),#General
                created_by = settings.payroll_officer.employee.user,
                draft=False
        )
        
        deduction_total = 0
        total_employer_deductions = 0
        total_employee_deductions = 0
        for pk in self.paygrade_['deductions']:
            deduction = Deduction.objects.get(pk=pk)
            employer_deduction = deduction.employer_deduction(self)
            employee_deduction = deduction.deduct(self)
            amount = employee_deduction + employer_deduction
            total_employee_deductions += employee_deduction
            total_employer_deductions += employer_deduction
            deduction_total += amount

            j.debit(amount, deduction.account_paid_into)
            j.credit(amount, deduction.liability_account)
        
        j.debit(self.net_pay, 
            accounting.models.Account.objects.get(pk=5008))#salaries EXPENSE
        j.credit(self.net_pay, 
            accounting.models.Account.objects.get(pk=2010))#salaries Liability
        j.debit(self.total_payroll_taxes, 
            accounting.models.Account.objects.get(
                pk=2002))#payroll taxes LIABILITY
        j.credit(self.total_payroll_taxes, 
            accounting.models.Account.objects.get(
                pk=5010))#payroll taxes EXPENSE

        self.entry = j
        self.status = 'verified'
        self.save()

    def create_entry(self):
        '''
        This method updates the accounting system for payroll actions
        the selected account from settings is deducted for all payments.
        Deductions with specific accounts deposit into those accounts, if an 
        employer has a contribution to deductions, their contribution is 
        factored in. 
        Payroll taxes deposit into their own account.
        Net income is deposited into account 5008.
        '''
        settings = EmployeesSettings.objects.first()
        if settings.require_verification_before_posting_payslips and \
                self.status != 'verified':
            #only work on verified payslips
            return
        
        j = accounting.models.JournalEntry.objects.create(
                memo= f'Auto generated entry from verified payslip #{self.pk}.',
                date=datetime.date.today(),
                journal =accounting.models.Journal.objects.get(
                    pk=2),#Cash disbursements Journal
                created_by = settings.payroll_officer.employee.user,
                draft=False
        )
            
        j.debit(self.net_pay, 
            accounting.models.Account.objects.get(pk=2010))#payroll taxes
        
        j.credit(self.net_pay, settings.payroll_account)#default cash account

        self.entry = j
        self.status = 'paid'
        self.save()