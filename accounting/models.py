# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
import datetime
from common_data.models import Person
from django.utils import timezone
from common_data.utilities import income_tax_calculator

class Debit(models.Model):
    account = models.ForeignKey('accounting.Account')
    amount =models.DecimalField(max_digits=6, decimal_places=2)
    entry = models.ForeignKey('accounting.JournalEntry')

    def save(self, *args, **kwargs):
        super(Debit, self).save(*args, **kwargs)
        self.account.balance -= self.amount
        self.account.save()


class Credit(models.Model):
    account = models.ForeignKey('accounting.Account')
    amount =models.DecimalField(max_digits=6,decimal_places=2)
    entry = models.ForeignKey('accounting.JournalEntry')

    def save(self, *args, **kwargs):
        super(Credit, self).save(*args, **kwargs)
        self.account.balance += self.amount
        self.account.save()

class JournalEntry(models.Model):
    reference = models.CharField(max_length=128, default="")
    date = models.DateField(default=datetime.date.today)
    memo = models.TextField()
    journal = models.ForeignKey('accounting.Journal')

    @property
    def total(self):
        return reduce(lambda x, y: x + y,[d.amount for d in self.debit_set.all()], 0)


    def simple_entry(self, amount, credit_acc, debit_acc):
        Credit.objects.create(
            entry=self,
            account = credit_acc,
            amount = amount
        )
        Debit.objects.create(
            entry=self,
            account = debit_acc,
            amount = amount
        )

class Account(models.Model):
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=32, choices=[
        ('expense', 'Expense'), 
        ('asset', 'Asset'), 
        ('liability', 'Liability'), 
        ('equity', 'Equity'), 
        ('income', 'Income'),
        ('cost-of-sales', 'Cost of Sales')])
    description = models.TextField()
    balance_sheet_category = models.CharField(max_length=16, choices=[
        ('current-assets', 'Current Assets'),
        ('long-term-assets', 'Long Term Assets'),
        ('current-liabilites', 'Current Liabilites'),
        ('expense', 'Expense'),
        ('current-assets', 'Current Assets'),\
        ("not-included", "Not Included")
    ], default='current-assets')
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.pk) + "-" + self.name

    def increment(self, amount):
        self.balance += float(amount)
        self.save()
        return self.balance

    def decrement(self, amount):
        self.balance -= float(amount)
        self.save()
        return self.balance
    
    def list_transactions(self):
        debits = self.debit_set.all()
        credits = self.credit_set.all()
    
class Ledger(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name 


class Journal(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    start_period = models.DateField(null=True)
    end_period = models.DateField(null=True)
    
    @property
    def is_open(self):
        return datetime.date.today() < self.end_period

    def __str__(self):
        return self.name 

class Tax(models.Model):
    name = models.CharField(max_length=64)
    rate = models.FloatField()

    def __str__(self):
        return self.name
    
class WorkBook(models.Model):
    name = models.CharField(max_length=64)
    #all adjustments are added to a workbook 

class Adjustmet(models.Model):
    id = models.AutoField(primary_key=True)
    entry = models.ForeignKey('accounting.JournalEntry', null=True)
    workbook = models.ForeignKey('accounting.WorkBook', null=True)
    description = models.TextField()

#payroll models 
class Employee(Person):
    employee_number = models.AutoField(primary_key=True)
    hire_date = models.DateField()
    title = models.CharField(max_length=32)
    pay_grade = models.ForeignKey('accounting.PayGrade', null=True)
    leave_days = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.first_name + " " + self.last_name

    def payslips_YTD(self):
        curr_year = datetime.date.today().year
        start = datetime.date(curr_year, 1, 1)
        end = datetime.date(curr_year,12,31)
        
        return Payslip.objects.filter(Q(employee=self) \
            & Q(start_period__gte=start) \
            & Q(end_period__lte=end)) 
    
    @property
    def deductions_YTD(self):
        slips = self.payslips_YTD()
        return reduce(lambda x, y: x + y, [i.total_deductions \
             for i in slips], 0)

    @property
    def earnings_YTD(self):
        slips = self.payslips_YTD()
        return reduce(lambda x, y: x + y, [i.gross_pay \
             for i in slips], 0)    
    
    
class Allowance(models.Model):
    name = models.CharField(max_length = 32)
    amount = models.FloatField()
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class Deduction(models.Model):
    name = models.CharField(max_length=32)
    method = models.IntegerField(choices=((0, 'Rated'), (1, 'Fixed')))
    rate = models.FloatField(default=0)
    amount = models.FloatField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def deduct(self, salary=0):
        if self.method == 0:
            return (self.rate / 100) * salary
        else:
            return self.amount

class CommissionRule(models.Model):
    name = models.CharField(max_length=32)
    min_sales = models.FloatField()
    rate = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PayGrade(models.Model):
    name = models.CharField(max_length=16)
    monthly_salary = models.FloatField(default=0)
    monthly_leave_days = models.FloatField(default=0)
    hourly_rate = models.FloatField(default=0)
    overtime_rate = models.FloatField(default=0)
    overtime_two_rate = models.FloatField(default=0)
    commission = models.ForeignKey('accounting.CommissionRule', null=True, blank=True)
    allowances = models.ManyToManyField('accounting.Allowance', blank=True)
    deductions = models.ManyToManyField('accounting.Deduction', blank=True)

    def __str__(self):
        return self.name

    @property
    def total_allowances(self):
        return reduce((lambda x, y: x + y), [a.amount for a in self.allowances.all()], 0)


    @property
    def total_deductions(self):
        return reduce((lambda x, y: x + y), [d.amount \
            for d in self.deductions.all() if d.method == 1] + \
            [d.deduct(self.monthly_salary) \
             for d in self.deductions.all() if d.method ==0] , 0)
    
class Payslip(models.Model):
    start_period = models.DateField()
    end_period = models.DateField()
    employee = models.ForeignKey('accounting.Employee', null=True)
    normal_hours = models.FloatField()
    overtime_one_hours = models.FloatField()
    overtime_two_hours = models.FloatField()
    
    pay_roll_id = models.IntegerField()

    def __str__(self):
        return str(self.employee) 
    
    def save(self, *args, **kwargs):
        super(Payslip, self).save(*args, **kwargs)
        #add leave for each month fix this
        self.employee.leave_days += self.employee.pay_grade.monthly_leave_days
        self.employee.save()

    @property
    def commission_pay(self):
        if not self.employee.pay_grade.commission:
            return 0
        
        elif not hasattr(self.employee, 'salesrepresentative'):
            return 0
        else:
            total_sales = \
                self.employee.salesrepresentative.sales(self.start_period, 
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
    def income_tax(self):
        return income_tax_calculator(self.gross_pay)


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
    def total_deductions(self):
        return self.income_tax + self.employee.pay_grade.total_deductions

    @property
    def net_pay(self):
        return self.gross_pay - self.total_deductions