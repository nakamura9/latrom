import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone
from common_data.models import SoftDeletionModel

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


class AbstractAccount(SoftDeletionModel):
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
    '''
    name = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    description = models.TextField()
    bank_account = models.BooleanField(default=False)
    control_account = models.BooleanField(default=False)
    parent_account = models.ForeignKey('accounting.account', blank=True, 
        null=True, on_delete=models.SET_NULL)
    balance_sheet_category = models.CharField(max_length=16, 
        choices=BALANCE_SHEET_CATEGORIES, default='current-assets')
    
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
  
    @property
    def balance_type(self):
        # TODO test
        if self.type in ['asset', 'expense', 'cost-of-sales']:
            return 'debit'
        else: #income, liability, equity
            return 'credit'
    @property
    def children(self):
        return Account.objects.filter(parent_account=self)

    @property
    def control_balance(self):
        
        total = self.balance 
        for acc in self.children:
            total += acc.balance

        return total
        
    class Meta:
        abstract = True

class Account(AbstractAccount):
    '''
    balance- mutable(not directly)
    '''
    @staticmethod
    def total_debit():
        '''returns the total amount debited to the accounting system
        may need to limit scope to a period
        '''
        return reduce(lambda x, y: x + y.debit, 
            Account.objects.all().exclude(balance=0), D(0.0))


    @staticmethod
    def total_credit():
        '''returns the total amount credited to the accounting system
        may need to limit scope to a period'''
        return reduce(lambda x, y: x + y.credit, 
            Account.objects.all().exclude(balance=0), D(0.0))


    @property
    def credit(self):
        '''status of the account'''
        if self.balance_type == "credit":
            return self.balance
        
        return D('0.00')
        


    @property
    def debit(self):
        '''status of account'''
        if self.balance_type == "debit":
            return self.balance

        return D('0.00')
    
    def convert_to_interest_bearing_account(self):
        # create an instance of InterestBearingAccount 
        # and delete this account
        pass
    

class InterestBearingAccount(AbstractAccount):
    '''
    mutable 
    '''
    interest_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    interest_interval = models.IntegerField(choices = [(0, 'monthly'), (1, 'annually')], default=1)
    interest_method = models.IntegerField(choices = [(0, 'Simple')], default=0)
    date_account_opened = models.DateField(default=datetime.date.today)
    last_interest_earned_date = models.DateField(null=True, blank=True)

    def convert_to_current_account(self):
        '''remove the interest related features of the account'''
        pass

    @property
    def interest_per_interval(self):
        return self.balance * D(self.interest_rate / D(100.0))

    def add_interest(self):
        self.balance += self.interest_per_interval
        self.save()

    @property
    def _interest_interval_days(self):
        mapping = {
            0: 30,
            1: 365
        }
        return mapping[self.interest_interval]

    def should_receive_interest(self, date):
        if self.last_interest_earned_date:
            return date > self.last_interest_earned_date + \
                datetime.timedelta(days=self._interest_interval_days)
        return date > self.date_account_opened + \
            datetime.timedelta(days=self._interest_interval_days)
