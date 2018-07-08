# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone
from common_data.models import Person


class Transaction(models.Model):
    '''
    Transaction
    ===========

    An abstract base class for all debits and credits.
    Does not create a table on the database.
    Is an aggregate component of a JournalEntry
    '''
    account = models.ForeignKey('accounting.Account')
    amount =models.DecimalField(max_digits=9, decimal_places=2)
    entry = models.ForeignKey('accounting.JournalEntry')
    class Meta:
        abstract =True


    def __lt__(self, other):
        '''for comparing transactions when listing them in an account'''
        return self.entry.date < other.entry.date


class Debit(Transaction):
    '''
    Debit
    ==========
    Inherits from transaction, is an aggregate part of a JournalEntry
    and subtracts from the account when saved.
    '''
    def __str__(self):
        return "Debit"

    def save(self, *args, **kwargs):
        super(Debit, self).save(*args, **kwargs)
        self.account.decrement(self.amount)


class Credit(Transaction):
    '''
    Debit
    ==========
    Inherits from transaction, is an aggregate part of a JournalEntry
    and adds to the account when saved.
    '''
    def __str__(self):
        return "Credit"

        
    def save(self, *args, **kwargs):
        super(Credit, self).save(*args, **kwargs)
        self.account.increment(self.amount)

class JournalEntry(models.Model):
    '''
    JournalEntry
    ============
    Represents a single entry in a journal and can consist of multiple debits and credits
    in any configuration.
    Includes a reference for identification and a memo to describe the entry.
    It is an aggregate component of a journal object.
    
    properties
    ------------
    total - returns a tuple the total amount on each side of the transaction, (debit, credit)
    total_debits - returns a decimal of the total amount credited in the entry
    total_credits -returns a decimal of the total amount debited in the entry
    balanced -returns a boolean of whether the entry is balanced
    
    methods
    ----------
    simple_entry() - takes 3 args, an amount, a credit account and a debit account and 
    creates the appropriate debit and credit transactions of an equal amount.
    '''
    reference = models.CharField(max_length=128, default="")
    date = models.DateField(default=datetime.date.today)
    memo = models.TextField()
    journal = models.ForeignKey('accounting.Journal')

    @property
    def total_debits(self):
        return reduce(lambda x, y: x + y,
            [d.amount for d in self.debit_set.all()], 0)
    
    @property
    def total_credits(self):
        return reduce(lambda x, y: x + y,
            [d.amount for d in self.credit_set.all()], 0)
    
    @property
    def balanced(self):
        return (self.total_credits - self.total_debits) == 0
    
    @property
    def total(self):
        return (self.total_debits, self.total_credits)


    def simple_entry(self, amount, credit_acc, debit_acc):
        self.credit(amount, credit_acc)
        self.debit(amount, debit_acc)
        
    def credit(self, amount, account):
        Credit.objects.create(
            entry=self,
            account = account,
            amount = amount
        )

    def debit(self, amount, account):
        Debit.objects.create(
            entry=self,
            account = account,
            amount = amount
        )

        
class Journal(models.Model):
    '''
    Represents the document of first entry for all transactions
    Each journal is made up of multiple entries
    They have a name and description
    
    methods
    --------
    get_entries_over_period - takes a start and end date and returns the 
    entries that belong to this journal between these dates

    '''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name 

    def delete(self):
        self.active = False
        self.save()

    def get_entries_over_period(self, start, end):
        return JournalEntry.objects.filter(Q(journal=self) 
            & Q(date__gte=start)
            & Q(date__lte=end))

#Choices for the account model
TYPE_CHOICES = [
        ('expense', 'Expense'), 
        ('asset', 'Asset'), 
        ('liability', 'Liability'), 
        ('equity', 'Equity'), 
        ('income', 'Income'),
        ('cost-of-sales', 'Cost of Sales')]

BALANCE_SHEET_CATEGORIES = [
        ('current-assets', 'Current Assets'),
        ('long-term-assets', 'Long Term Assets'),
        ('current-liabilites', 'Current Liabilites'),
        ('expense', 'Expense'),
        ('current-assets', 'Current Assets'),\
        ("not-included", "Not Included")
    ]
class Account(models.Model):
    '''
    The representation of the record of all financial expenditures and receipts
    associated with a particular purpose.
    The key features are its name, balance and its type.

    methods
    ----------
    increment - increases the balance of the account by the provided amount
    decrement - decreases the balance of the account by the provided amount

    properties
    ------------
    transaction_list - returns an ordered list of transactions on the account
    '''
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    description = models.TextField()
    balance_sheet_category = models.CharField(max_length=16, 
        choices=BALANCE_SHEET_CATEGORIES, default='current-assets')
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.pk) + "-" + self.name

    def increment(self, amount):
        self.balance += decimal.Decimal(amount)
        self.save()
        return self.balance

    def decrement(self, amount):
        self.balance -= decimal.Decimal(amount)
        self.save()
        return self.balance

    def delete(self):
        self.active = False
        self.save()
    
    @property
    def transaction_list(self):
        #might need to stream this when the transactions become numerous
        debits = list(self.debit_set.all())
        credits = list(self.credit_set.all())
        return sorted(debits + credits)
    

class Ledger(models.Model):
    '''
    Summarizes the accounts and journal entries
    Not yet implemented
    '''
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name 



class Tax(models.Model):
    '''
    Used in invoices and payroll, tax is a cost incurred as a
     percentage of income. Will implement more complex tax features as required
    '''
    name = models.CharField(max_length=64)
    rate = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def delete(self):
        self.active = False
        self.save()

class WorkBook(models.Model):
    '''
    The workbook is an object is used to store all the adjustments 
    of an account either during reconcilliation or when a trial balance
    fails.
    Not yet implemented
    '''
    name = models.CharField(max_length=64)

class Adjustmet(models.Model):
    '''
    An adjustment records the necessary changes to journal entries that 
    will balance the books. In this way, the journal entries become immutable.
    Not yet implemented
    '''
    entry = models.ForeignKey('accounting.JournalEntry', null=True)
    workbook = models.ForeignKey('accounting.WorkBook', null=True)
    description = models.TextField()

#payroll models -might spin this off into its own module.
class Employee(Person):
    '''
    Represents an individual employee of the business. Records their personal details as 
    well as their title, pay grade and leave days.

    properties
    ------------
    deductions_YTD - a field that calculates all the deductions throughout the year. 
        Used in payslips
    allowances_YTD - a field that calculates all the allowances earned throughout the year. 
        Used in payslips
    '''
    employee_number = models.AutoField(primary_key=True)
    hire_date = models.DateField()
    title = models.CharField(max_length=32)
    pay_grade = models.ForeignKey('accounting.PayGrade', null=True)
    leave_days = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    
    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.first_name + " " + self.last_name

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
        slips = self._payslips_YTD()
        return reduce(lambda x, y: x + y, [i.total_deductions \
             for i in slips], 0)

    @property
    def earnings_YTD(self):
        slips = self._payslips_YTD()
        return reduce(lambda x, y: x + y, [i.gross_pay \
             for i in slips], 0)    
    
    
class Allowance(models.Model):
    '''simple object that tracks a fixed allowance as part of a pay
    grade'''
    name = models.CharField(max_length = 32)
    amount = models.FloatField()
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
    def delete(self):
        '''prevents deletion of objects'''
        self.active = False
        self.save()

# for model Deduction
DEDUCTION_METHODS = ((0, 'Rated'), (1, 'Fixed'))
DEDUCTION_TRIGGERS = ((0, 'All Income'), 
    (1, 'Taxable Income'), 
    (2, 'Tax'))

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
    total_allowances - returns the numerical total of the applied allowance for a 
        particular employee
    
    '''
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
    PAYE - returns the amount of PAYE earned based on gross earnings and where
        these fall in the pay bracket structure at  ZIMRA
    gross_pay - returns the sum total of all the money earned from basic salaries,
        allowances and hourly pay
    _deductions - returns the sum of the money deducted from the Deduct objects as 
        part of a pay grade
     total_deductions - returns sum of PAYE and _deductions
     net_pay returns the difference between gross_pay and total_deductions
    '''
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
    def PAYE(self):
        upper_limits = [0, 300, 1500, 3000, 5000, 10000, 15000, 20000]
        rates = {
            (0,300) : (0, 0),
            (300,1500) : (20, 60),
            (1500,3000) : (25, 135),
            (3000,5000) : (30, 285),
            (5000,10000) : (35, 535),
            (10000,15000) : (40, 1035),
            (15000,20000) : (45, 1785),
        }
        count = 0
        for limit in upper_limits:
            if self.gross_pay >= limit:
                count += 1 
            else:
                bracket = (upper_limits[count -1], limit)
                break
    
        return ((self.gross_pay * rates[bracket][0])/100) - rates[bracket][1]

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
    def _deductions(self):
        return reduce(lambda x, y: x + y, 
            [d.deduct(self) \
                for d in self.employee.pay_grade.deductions.all()], 0)

    @property
    def total_deductions(self):
        return self.PAYE + self._deductions

    @property
    def net_pay(self):
        return self.gross_pay - self.total_deductions

DEPRECIATION_METHOD = [
    (0, 'Straight Line'),
    (1, 'Sum of years digits'),
    (2, 'Double Declining balance')
]
asset_choices = ['Land', 'Buildings', 'Vehicles', 'LeaseHold Improvements',
    'Furniture and Fixtures', 'Equipment']
ASSET_CHOICES = [(asset_choices.index(i), i) for i in asset_choices]


class Asset(models.Model):
    '''Represents a resource controlled by the organization from which 
    a future financial benefit is expected.
    Data regarding the value and depreciation techniques employed on the 
    asset are stored in this model.
    The corresponding journal entry is supplied on creation.
    '''
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    category = models.IntegerField(choices=ASSET_CHOICES)
    initial_value  = models.DecimalField(max_digits=9, decimal_places=2)
    account = models.ForeignKey('accounting.Account', 
        limit_choices_to=Q(type='asset'))
    depreciation_period = models.IntegerField()
    init_date = models.DateField()
    depreciation_method = models.IntegerField(choices=DEPRECIATION_METHOD)
    salvage_value = models.DecimalField(max_digits=9, decimal_places=2)

    def create_entry(self):
        j = JournalEntry.objects.create(
            reference = "Asset. ID: " + str(self.pk),
            date = datetime.date.today(),
            memo =  "Asset added. Name: %s. Description: %s " % (
                self.name, self.description
            ),
            journal = Journal.objects.get(pk=5)# not ideal
        )
        j.simple_entry(self.initial_value, 
        Account.objects.get(name=asset_choices[self.category]), 
        self.account)

    def depreciate(self):
        pass

    @property
    def current_value(self):
        pass

    def _str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Asset, self).save(*args, **kwargs)
        self.create_entry()


expense_choices = ['Advertising', 'Bank Service Charges', 'Equipment Rental', 
    'Dues and Subscriptions', 'Telephone', 'Vehicles', 'Travel and Expenses',
        'Suppliers', 'Rent', 'Payroll Expenses', 'Insurance', 'Office Expenses',
        'Postage', 'Other']
EXPENSE_CHOICES = [(expense_choices.index(i), i) for i in expense_choices]

class Expense(models.Model):
    '''A representation of the costs incurred by an organization 
    in an effort to generate revenue.
    Related information about the cost category, date amounts and 
    whether or not the expense can be billed to customers is also 
    recorded. Creates a journal entry when intialized.'''
    date = models.DateField()
    description = models.TextField()
    category = models.IntegerField(choices=EXPENSE_CHOICES)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    billable = models.BooleanField(default=False)
    customer = models.ForeignKey('invoicing.Customer')
    account = models.ForeignKey('accounting.Account')
    
    def create_entry(self):
        j = JournalEntry.objects.create(
            reference = "Expense. ID: " + str(self.pk),
            date = self.date,
            memo =  "Expense recorded. Category: %s." % self.category,
            journal = Journal.objects.get(pk=2)# cash disbursements
        )
        j.simple_entry(self.amount, 
        Account.objects.get(name=expense_choices[self.category]), 
        self.customer.account \
        if billable \
        else self.account)

    def save(self, *args, **kwargs):
        super(Expense, self).save(*args, **kwargs)
        self.create_entry()
