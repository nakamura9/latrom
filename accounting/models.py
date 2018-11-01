# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel


class AccountingSettings(SingletonModel):
    start_of_financial_year = models.DateField()
    use_default_chart_of_accounts = models.BooleanField(default=True)

class Bookkeeper(models.Model):
    '''Model that gives employees access to the bookkeeping function of the 
    software such as order creation and the like.'''
    employee = models.OneToOneField('employees.Employee', 
        on_delete=None, default=1, limit_choices_to=Q(user__isnull=False))
    can_create_journals = models.BooleanField(default=False, blank=True)
    can_create_orders_and_invoices = models.BooleanField(default=False, blank=True)
    can_record_expenses = models.BooleanField(default=False, blank=True)
    can_record_assets = models.BooleanField(default=False, blank=True)
    active = models.BooleanField(default=True)

    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.employee.full_name
    
class Transaction(models.Model):
    '''
    Transaction
    ===========

    An abstract base class for all debits and credits.
    Does not create a table on the database.
    Is an aggregate component of a JournalEntry
    '''
    account = models.ForeignKey('accounting.Account', on_delete=None)
    amount =models.DecimalField(max_digits=9, decimal_places=2)
    entry = models.ForeignKey('accounting.JournalEntry', on_delete=models.CASCADE)
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
    Credit
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
    journal = models.ForeignKey('accounting.Journal', on_delete=None)
    posted_to_general_ledger = models.BooleanField(default=False)
    adjusted = models.BooleanField(default=False)
    created_by = models.ForeignKey('auth.user', default=1, on_delete=None)

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

    @property
    def str_total(self):
        return "DR:{};  CR{}".format(self.total_debits, self.total_credits)


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
        ('long-term-liabilites', 'Long Term Liabilites'),
        ('expense', 'Expense'),
        ('current-assets', 'Current Assets'),
        ("not-included", "Not Included")
    ]

class AbstractAccount(models.Model):
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
        self.balance += D(amount)
        self.save()
        return self.balance

    def decrement(self, amount):
        self.balance -= D(amount)
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

    @property
    def recent_entries(self):
        return [i.entry for i in self.transaction_list[:5]]
        

    class Meta:
        abstract = True

class Account(AbstractAccount):
    
    def convert_to_interest_bearing_account(self):
        # create an instance of InterestBearingAccount 
        # and delete this account
        pass
    

class InterestBearingAccount(AbstractAccount):
    interest_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    interest_interval = models.IntegerField(choices = [(0, 'monthly'), (1, 'annually')], default=1)
    interest_method = models.IntegerField(choices = [(0, 'Simple'), 
        (1, 'Commpound')], default=0)

    def convert_to_current_account(self):
        '''remove the interest related features of the account'''
        pass

class Ledger(models.Model):
    '''
    Summarizes the accounts and journal entries
    Not yet implemented -might make a singleton model
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
    entry = models.ForeignKey('accounting.JournalEntry', on_delete=models.CASCADE, null=True)
    workbook = models.ForeignKey('accounting.WorkBook', on_delete=models.CASCADE,null=True)
    description = models.TextField()

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
    debit_account = models.ForeignKey('accounting.Account', on_delete=models.CASCADE,null=True)
    depreciation_period = models.IntegerField()#years
    init_date = models.DateField()
    depreciation_method = models.IntegerField(choices=DEPRECIATION_METHOD)
    salvage_value = models.DecimalField(max_digits=9, decimal_places=2)
    created_by = models.ForeignKey('auth.user', default=1, on_delete=None)

    def create_entry(self):
        '''debits the debit account and credits the appropriate asset account'''
        #verified
        try:
            j = JournalEntry.objects.create(
                reference = "Asset. ID: " + str(self.pk),
                date = datetime.date.today(),
                memo =  "Asset added. Name: %s. Description: %s " % (
                    self.name, self.description
                
                ),
                created_by = self.created_by,
                journal = Journal.objects.get(pk=5)# not ideal general journal
            )
            j.simple_entry(self.initial_value, 
            Account.objects.get(name=asset_choices[self.category]),
            self.debit_account)
        except:
            pass

    def depreciate(self):
        pass

    def salvage(self):
        #removes asset from the books and credits the appropriate account
        pass

    @property
    def current_value(self):
        pass

    def _str__(self):
        return self.name

    def save(self, *args, **kwargs):
        #check if the item exists before trying to save it
        flag = self.pk
        super(Asset, self).save(*args, **kwargs)
        if flag is None:
            self.create_entry()


expense_choices = ['Advertising', 'Bank Service Charges', 'Equipment Rental', 
    'Dues and Subscriptions', 'Telephone', 'Vehicles', 'Travel and Expenses',
        'Suppliers', 'Rent', 'Payroll Expenses', 'Insurance', 'Office Expenses',
        'Postage', 'Other']
EXPENSE_CHOICES = [(expense_choices.index(i), i) for i in expense_choices]


class AbstractExpense(models.Model):
    '''A representation of the costs incurred by an organization 
    in an effort to generate revenue.
    Related information about the cost category, date amounts and 
    whether or not the expense can be billed to customers is also 
    recorded. Creates a journal entry when intialized.'''
    description = models.TextField()
    category = models.PositiveSmallIntegerField(choices=EXPENSE_CHOICES)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    debit_account = models.ForeignKey('accounting.Account', on_delete=None)
    recorded_by = models.ForeignKey('auth.user', default=1, on_delete=None)

    class Meta:
        abstract = True

    @property
    def expense_account(self):
        global EXPENSE_CHOICES
        name = EXPENSE_CHOICES[self.category][1]
        return Account.objects.get(name=name)

class Expense(AbstractExpense):
    date = models.DateField()
    billable = models.BooleanField(default=False)
    customer = models.ForeignKey('invoicing.Customer', on_delete=None,null=True)
    

    def create_entry(self):
        #verified
        j = JournalEntry.objects.create(
            reference = "Expense. ID: " + str(self.pk),
            date = self.date,
            memo =  "Expense recorded. Category: %s." % self.category,
            journal = Journal.objects.get(pk=2),# cash disbursements
            created_by=self.recorded_by
        )
        #debits increase expenses credits decrease assets so...
        j.simple_entry(self.amount, 
        self.customer.account \
        if self.billable \
        else Account.objects.get(pk=1000),#cash account
        Account.objects.get(name=expense_choices[self.category]), )
       

    def save(self, *args, **kwargs):
        flag = self.pk
        if self.billable and self.customer == None:
            raise ValueError('A billable expense needs a customer')
        super(Expense, self).save(*args, **kwargs)
        if flag is None:
            self.create_entry()


class RecurringExpense(AbstractExpense):
    EXPENSE_CYCLE_CHOICES = [
        (1, 'Daily'), 
        (7, 'Weekly'), 
        (14, 'Bi- Monthly'), 
        (30, 'Monthly'), 
        (90, 'Quarterly'), 
        (182, 'Bi-Annually'), 
        (365, 'Annually')]
    cycle = models.IntegerField(choices=EXPENSE_CYCLE_CHOICES, default=30)
    expiration_date = models.DateField(null=True)
    start_date = models.DateField(null=True)
    last_created_date = models.DateField(null=True)

    @property
    def is_current(self):
        return datetime.date.today() < self.expiration_date

    def create_entry(self):
        #verified
        j = JournalEntry.objects.create(
            reference = "Expense. ID: {}".format(self.pk),
            date = datetime.date.today(),
            memo =  "Recurrent Expense recorded. Category: {}".format(self.category),
            journal = Journal.objects.get(pk=2),# cash disbursements
            created_by = self.recorded_by
        )
        j.simple_entry(self.amount, 
        Account.objects.get(name=expense_choices[self.category]), 
        self.debit_account)
        return j
