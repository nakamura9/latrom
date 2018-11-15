# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel
import planner



class EmployeesSettings(SingletonModel):
    PAYROLL_DATE_CHOICES = [(i, i) for i in range(28, 1)]
    PAYROLL_CYCLE_CHOICES = [
        ('weekly', 'Weekly'), 
        ('bi-monthly', 'Bi-monthly'), 
        ('monthly', 'Monthly')
        ]
    payroll_date_one = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES
        )
    payroll_date_two = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES
    )
    payroll_date_three = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES
    )
    payroll_date_four = models.PositiveSmallIntegerField(
        choices = PAYROLL_DATE_CHOICES
    )
    last_payroll_date = models.DateField(blank=True, null=True)
    payroll_cycle = models.CharField(
        max_length=12, 
        choices = PAYROLL_CYCLE_CHOICES
        )
    automate_payroll_for = models.ManyToManyField('employees.Employee', blank=True)
    require_verification_before_posting_payslips = models.BooleanField(
        default=True
        )
    salary_follows_profits = models.BooleanField(default=True)
    payroll_officer = models.ForeignKey("employees.Employee", 
        on_delete=None,
        related_name="payroll_officer",
        blank=True, 
        null=True
    )
    payroll_counter = models.IntegerField(default=0)
    

    

class EmployeeTimeSheet(models.Model):
    MONTH_CHOICES = [
        (i, i) for i in range(0, 13)
    ] 
    YEAR_CHOICES = [
        (i, i) for i in range(2000, 2051)
    ] 
    employee = models.ForeignKey('employees.employee', on_delete=None, related_name='target')
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES)
    recorded_by = models.ForeignKey('employees.employee', on_delete=None, related_name='recorder', null=True)
    complete=models.BooleanField(default=False, blank=True)

    @property
    def normal_hours(self):
        total = datetime.timedelta(seconds=0)
        for line in self.attendanceline_set.all():
            total += line.normal_time

        return total

    @property
    def overtime(self):
        total = datetime.timedelta(seconds=0)
        for line in self.attendanceline_set.all():
            total += line.overtime

        return total


class AttendanceLine(models.Model):
    timesheet = models.ForeignKey('employees.EmployeeTimeSheet', on_delete=None)
    date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    lunch_duration = models.DurationField(null=True, blank=True)

    def to_datetime(self, time):
        return datetime.datetime.combine(self.date, time)
    @property
    def total_time(self):
        return self.to_datetime(self.time_out) - self.to_datetime(self.time_in)
    
    @property
    def working_time(self):
        return self.total_time - self.lunch_duration

    @property
    def normal_time(self):
        if (self.working_time.seconds / 3600) > 8:
            return datetime.timedelta(hours=8)
        
        return self.working_time

    @property
    def overtime(self):
        if (self.working_time.seconds / 3600) > 8:
            return self.working_time - datetime.timedelta(hours=8)
        
        return datetime.timedelta(seconds=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.lunch_duration is None:
            self.lunch_duration = self.timesheet.employee.pay_grade.lunch_duration
            self.save()

class Employee(Person):
    '''
    Represents an individual employee of the business. Records their personal 
    details as well as their title, pay grade and leave days.

    properties
    ------------
    deductions_YTD - a field that calculates all the deductions throughout the 
    year. 
        Used in payslips
    allowances_YTD - a field that calculates all the allowances earned 
    throughout the year. 
        Used in payslips
    earnings_YTD - a field that calculates all the  earnings throughout the 
    year. 
        Used in payslips
    is_<role> - checks the instance for evidence that an employee has been 
    assigned a certain role within the system.
    '''
    employee_number = models.AutoField(primary_key=True)
    hire_date = models.DateField()
    title = models.CharField(max_length=32)
    pay_grade = models.ForeignKey('employees.PayGrade', 
        on_delete=models.CASCADE,default=1)
    leave_days = models.FloatField(default=0)
    uses_timesheet = models.BooleanField(default=False, blank=True)
    user = models.OneToOneField('auth.User', null=True,
         on_delete=models.CASCADE)#not all are users
    active = models.BooleanField(default=True)
    pin = models.PositiveSmallIntegerField(default=1000)
    
    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def _payslips_YTD(self):
        '''internal abstract method used in the following properties'''
        curr_year = datetime.date.today().year
        start = datetime.date(curr_year, 1, 1)
        end = datetime.date(curr_year,12,31)
        
        return Payslip.objects.filter(Q(employee=self) \
            & Q(start_period__gte=start) \
            & Q(end_period__lte=end)) 
    
    @property
    def deductions_YTD(self):
        slips = self._payslips_YTD
        return reduce(lambda x, y: x + y, [i.total_deductions \
             for i in slips], 0)

    @property
    def earnings_YTD(self):
        slips = self._payslips_YTD
        return reduce(lambda x, y: x + y, [i.gross_pay \
             for i in slips], 0)    

    @property
    def is_sales_rep(self):
        return hasattr(self, 'salesrepresentative')

    @property
    def is_inventory_controller(self):
        return hasattr(self, 'inventorycontroller')

    @property
    def is_bookkeeper(self):
        return hasattr(self, 'bookkeeper')

    @property
    def is_payroll_officer(self):
        return hasattr(self, 'payroll_officer')


    @property
    def is_serviceperson(self):
        return hasattr(self, 'serviceperson')

    @property
    def agenda_items(self):
        #check participants as well
        return planner.models.Event.objects.filter(
            Q(Q(completed=False) & Q(date__gte=datetime.date.today())) &
            Q(owner=self.user)).count()


#Change to benefits 
class Allowance(models.Model):
    '''simple object that tracks a fixed benefit or allowance granted as 
    part of a pay grade'''
    name = models.CharField(max_length = 32)
    amount = models.FloatField()
    active = models.BooleanField(default=True)
    taxable = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
    def delete(self):
        '''prevents deletion of objects'''
        self.active = False
        self.save()

class Deduction(models.Model):
    '''
    Many deductions are complex and this model reflects those features.
    For simple deductions a fixed amount can be applied.
    For more complex deductions percentage rating and variable triggers are supported
    So far implemented are deductions based on 
    1. All income
    2. Taxable income
    3. Tax

    methods
    -----------
    deduct - takes a payslip as a argument and returns the value of the deduction 
    based on the rules defined in the model. 

    '''
    DEDUCTION_METHODS = ((0, 'Rated'), (1, 'Fixed'))
    DEDUCTION_TRIGGERS = (
        (0, 'All Income'), 
        (1, 'Taxable Income'), 
        (2, 'Tax')
    )
    name = models.CharField(max_length=32)
    method = models.IntegerField(choices=DEDUCTION_METHODS)
    trigger = models.IntegerField(choices = DEDUCTION_TRIGGERS,
        default=0)
    rate = models.FloatField(default=0)
    amount = models.FloatField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def deduct(self, payslip):
        if self.method == 0:
            if self.trigger == 0:
                #all income
                return (self.rate / 100) * payslip.gross_pay
            elif self.trigger == 1:
                #taxable income
                return (self.rate / 100) * (payslip.gross_pay - 300)
            elif self.trigger == 2:
                # % PAYE
                return (self.rate / 100) * payslip.income_tax
            else:
                return 0
        else:
            return self.amount

    def delete(self):
        '''prevents deletion of objects as they may remain part of legacy
        objects'''
        self.active = False
        self.save()


class PayrollOfficer(models.Model):
    employee = models.OneToOneField('employees.Employee', on_delete=None)
    can_log_timesheets = models.BooleanField(default=False, blank=True)
    can_run_payroll = models.BooleanField(default=False, blank=True)
    can_create_payroll_elements = models.BooleanField(default=False, blank=True)
    can_register_new_employees = models.BooleanField(default=False, blank=True)

class CommissionRule(models.Model):
    '''simple model for giving sales representatives commission based on 
    the product they sell. Given a sales target and a percentage, the commission can
    be calculated.'''
    name = models.CharField(max_length=32)
    min_sales = models.FloatField()
    rate = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def delete(self):
        self.active=False
        self.save()

    
class PayGrade(models.Model):
    '''
    This model describes the common pay features applied to a group of employees.
    It outlines their benefits such as leave days, salary, hourly rates and 
    allowances and their obligations such as their deductions.
    Commission, Allowances and Deductions are aggregate objects of this data model.

    properties
    -----------
    total_allowances - returns the numerical total of the applied allowance for 
    a particular employee
    
    '''
    LUNCH_CHOICES = [
        (datetime.timedelta(minutes=15), '15 min.'),
        (datetime.timedelta(minutes=30), '30 min.'),
        (datetime.timedelta(minutes=45), '45 min.'),
        (datetime.timedelta(hours=1), '1 hr.')

    ]
    name = models.CharField(max_length=16)
    monthly_salary = models.FloatField(default=0)
    monthly_leave_days = models.FloatField(default=0)
    hourly_rate = models.FloatField(default=0)
    overtime_rate = models.FloatField(default=0)
    overtime_two_rate = models.FloatField(default=0)
    commission = models.ForeignKey('employees.CommissionRule', on_delete=None,
        null=True, blank=True)
    allowances = models.ManyToManyField('employees.Allowance', blank=True)
    deductions = models.ManyToManyField('employees.Deduction', blank=True)
    payroll_taxes = models.ManyToManyField('employees.PayrollTax', blank=True)
    subtract_lunch_time_from_working_hours = models.BooleanField(default=False)
    lunch_duration = models.DurationField(
        choices=LUNCH_CHOICES,
        default=datetime.timedelta(hours=1)
        )

    def __str__(self):
        return self.name

    @property
    def tax_free_benefits(self):
        return reduce((lambda x, y: x + y), [a.amount for a in self.allowances.filter(taxable=False)], 0)

    @property
    def total_allowances(self):
        return reduce((lambda x, y: x + y), [a.amount for a in self.allowances.all()], 0)

    
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
    _deductions - returns the sum of the money deducted from the Deduct objects as 
        part of a pay grade
     total_deductions - returns sum of PAYE and _deductions
     net_pay returns the difference between gross_pay and total_deductions
    '''
    start_period = models.DateField()
    end_period = models.DateField()
    employee = models.ForeignKey('employees.Employee', on_delete=None)
    normal_hours = models.FloatField()
    overtime_one_hours = models.FloatField()
    overtime_two_hours = models.FloatField()
    pay_roll_id = models.IntegerField()

    def __str__(self):
        return str(self.employee) 
    
    def save(self, *args, **kwargs):
        super(Payslip, self).save(*args, **kwargs)
        #add leave for each month
        self.employee.leave_days += self.employee.pay_grade.monthly_leave_days
        self.employee.save()

    @property
    def commission_pay(self):
        if not self.employee.pay_grade.commission:
            return 0
        
        elif not hasattr(self.employee, 'salesrepresentative'):
            return 0
        else:
            total_sales = self.employee.salesrepresentative.sales(
                self.start_period, 
                self.end_period)
            commissionable_sales = total_sales - self.commission.min_sales
            return self.employee.pay_grade.commission.rate * \
                commissionable_sales

    @property 
    def normal_pay(self):
        return self.employee.pay_grade.hourly_rate * self.normal_hours

    @property
    def overtime_one_pay(self):
        return self.employee.pay_grade.overtime_rate * self.overtime_one_hours


    @property
    def overtime_two_pay(self):
        return self.employee.pay_grade.overtime_two_rate * self.overtime_two_hours

    @property
    def overtime_pay(self):
        return self.overtime_one_pay + self.overtime_two_pay

    '''
    #Deprecate
    @property
    def calculated_payroll_taxes_list(self):
        return [{
            'name': tax.name,
            'amount': tax.tax(self.taxable_gross_pay)} \
                for tax in self.employee.pay_grade.payroll_taxes.all()]
    '''


    @property
    def gross_pay(self):
        gross = self.employee.pay_grade.monthly_salary
        gross += self.normal_pay
        gross += self.overtime_one_pay
        gross += self.overtime_two_pay
        gross += self.employee.pay_grade.total_allowances
        gross += self.commission_pay
        return gross

    @property 
    def taxable_gross_pay(self):
        return self.gross_pay - self.employee.pay_grade.tax_free_benefits


    @property
    def _deductions(self):
        return reduce(lambda x, y: x + y, 
            [d.deduct(self) \
                for d in self.employee.pay_grade.deductions.all()], 0)

    @property
    def total_payroll_taxes(self):
        return reduce(lambda x, y: x + y, 
            [t.tax(self.gross_pay) \
                for t in self.employee.pay_grade.payroll_taxes.all()], 0)

    @property
    def total_deductions(self):
        return self.total_payroll_taxes + D(self._deductions)

    @property
    def net_pay(self):
        return D(self.gross_pay) - D(self.total_deductions)


class PayrollTax(models.Model):
    name = models.CharField(max_length=64)
    paid_by = models.IntegerField(choices=[(0, 'Employees'), (1, 'Employer')])

    @property
    def paid_by_string(self):
        return ['Employees', 'Employer'][self.paid_by]

    def tax(self, gross):
        bracket = self.get_bracket(gross)
        if bracket:
            return (D(gross) * (bracket.rate / D(100.0))) - bracket.deduction 
        return 0

    def get_bracket(self, gross):
        for bracket in self.taxbracket_set.all():
            if bracket.lower_boundary <= gross and \
                    bracket.upper_boundary >= gross:
                return bracket
        return None


    def __str__(self):
        return self.name 
        
    def add_bracket(self, lower, upper, rate, deduction):
        #insert code to prevent overlap
        TaxBracket.objects.create(payroll_tax=self,
            lower_boundary=lower, 
            upper_boundary=upper,
            rate=rate,
            deduction=deduction)

    def delete_bracket(self, bracket_id):
        TaxBracket.objects.get(pk=bracket_id).delete()

    def update_bracket(self, bracket_id, lower, upper, rate, deduction):
        tb = TaxBracket.objects.get(pk=bracket_id)
        tb.lower = lower
        tb.upper = upper
        tb.rate = rate
        tb.deduction = deduction
        tb.save()

    def list_brackets(self):
        return TaxBracket.objects.filter(payroll_tax =self).order_by('upper_boundary')

class TaxBracket(models.Model):
    payroll_tax = models.ForeignKey('employees.PayrollTax', on_delete=None)
    lower_boundary = models.DecimalField(max_digits=9, decimal_places=2)
    upper_boundary = models.DecimalField(max_digits=9, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    deduction = models.DecimalField(max_digits=9, decimal_places=2)
