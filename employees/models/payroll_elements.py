
import random
import datetime
from decimal import Decimal as D
from functools import reduce
from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel, SoftDeletionModel
import planner
import accounting
import invoicing
from django.shortcuts import reverse

class Allowance(SoftDeletionModel):
    '''simple object that tracks a fixed benefit or allowance granted as 
    part of a pay grade'''
    name = models.CharField(max_length = 32)
    amount = models.FloatField()
    taxable = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    #no detail view

class Deduction(SoftDeletionModel):
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
    account_paid_into = models.ForeignKey(
        'accounting.account',
        on_delete=models.SET_DEFAULT,
        default=5008)# salaries 

    def __str__(self):
        return self.name
    
    def deduct(self, payslip):
        if self.method == 0:
            if self.trigger == 0:
                #all income
                return (self.rate / 100) * payslip.gross_pay
            elif self.trigger == 1:
                #taxable income
                return (self.rate / 100) * (payslip.taxable_gross_pay)
            elif self.trigger == 2:
                # % PAYE
                return (self.rate / 100) * float(payslip.total_payroll_taxes)
            else:
                return 0
        else:
            return self.amount

    #no detail view


class CommissionRule(SoftDeletionModel):
    '''simple model for giving sales representatives commission based on 
    the product they sell. Given a sales target and a percentage, the commission can
    be calculated.'''
    name = models.CharField(max_length=32)
    min_sales = models.FloatField()
    rate = models.FloatField()

    def __str__(self):
        return self.name

    #no detail view


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


    @property
    def list_brackets(self):
        return TaxBracket.objects.filter(payroll_tax =self).order_by('upper_boundary')

    #no detail view


class TaxBracket(models.Model):
    payroll_tax = models.ForeignKey('employees.PayrollTax', on_delete=models.SET_NULL, null=True)
    lower_boundary = models.DecimalField(max_digits=9, decimal_places=2)
    upper_boundary = models.DecimalField(max_digits=9, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    deduction = models.DecimalField(max_digits=9, decimal_places=2)



class PayrollSchedule(SingletonModel):
    '''A container for payroll dates'''
    name = models.CharField(max_length=255)


class PayrollDate(models.Model):
    '''Represents a date in the month when payroll is run. On each such date all employees in the relevant grades, departments or employee list have paychecks created.'''
    PAYROLL_DATE_CHOICES = [(i, i) for i in range(1, 29)]
    
    date = models.PositiveSmallIntegerField(choices = PAYROLL_DATE_CHOICES)
    employees = models.ManyToManyField('employees.employee')
    departments = models.ManyToManyField('employees.department')
    pay_grades = models.ManyToManyField('employees.paygrade')
    schedule = models.ForeignKey('employees.payrollschedule', default=1, 
        on_delete=models.SET_DEFAULT)

    def __str__(self):
        return f"{self.schedule.name}: {self.date}"

    @property 
    def number_of_employees(self):
        return len(self.all_employees)

    @property
    def all_employees(self):
        employees = list(self.employees.all())

        for department in self.departments.all():
            employees += [employee for employee in department.employees.all() \
                if employee not in employees]

        for grade in self.pay_grades.all():
            employees += [employee for employee in grade.employee_set.all() \
                if employee not in employees]

        return employees

    @property
    def date_suffix(self):
        suffices = ['st', 'nd', 'rd'] + ['th' for i in range(3, 29)]
        return suffices[self.date -1]

    def get_absolute_url(self):
        return reverse("employees:payroll-date-detail", kwargs={"pk": self.pk})
    