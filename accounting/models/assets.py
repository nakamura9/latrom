import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone
import accounting


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
    credit_account = models.ForeignKey('accounting.Account', 
        on_delete=models.SET_DEFAULT, default=1000)
    depreciation_period = models.IntegerField()#years
    init_date = models.DateField()
    depreciation_method = models.IntegerField(choices=DEPRECIATION_METHOD)
    salvage_value = models.DecimalField(max_digits=9, decimal_places=2)
    created_by = models.ForeignKey('auth.user', default=1, on_delete=models.SET_NULL, null=True)

    def create_entry(self):
        '''debits the debit account and credits the appropriate asset account'''
        #verified
    
        j = accounting.models.transactions.JournalEntry.objects.create(
            date = datetime.date.today(),
            memo =  "Asset added. Name: %s. Description: %s " % (
                self.name, self.description
            
            ),
            created_by = self.created_by,# not ideal general journal
            journal = accounting.models.books.Journal.objects.get(pk=5)
        )
        j.simple_entry(self.initial_value, 
            self.credit_account,# defaults to cash account
            self.account)# asset account
        
    @property
    def account(self):
        '''maps an asset choice to an asset account from the chart of accounts'''
        mapping = {
            0: 1005,
            1: 1006,
            3: 1008,
            2: 1009,
            4: 1011,
            5: 1013,
        }
        return accounting.models.accounts.Account.objects.get(pk=mapping[self.category])


    def __str__(self):
        return self.name
        
    @property
    def salvage_date(self):
        return self.init_date + datetime.timedelta(
            days=365 * self.depreciation_period)

    def salvage(self):
        #removes asset from the books and credits the appropriate account
        pass

    @property 
    def _timedelta(self):
        '''returns the duration since the asset was created in years'''
        return int((datetime.date.today() - self.init_date).days / 365)

    @property
    def category_string(self):
        return dict(ASSET_CHOICES)[self.category]

    @property
    def total_depreciation(self):
        depreciable_value = self.initial_value - self.salvage_value
        dep_per_year = depreciable_value / self.depreciation_period
        return self._timedelta * dep_per_year

    @property
    def current_value(self):
        return self.initial_value - self.total_depreciation

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        #check if the item exists before trying to save it
        flag = self.pk
        super(Asset, self).save(*args, **kwargs)
        if flag is None:
            self.create_entry()
