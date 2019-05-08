import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone
import accounting
from common_data.models import SoftDeletionModel
from django.shortcuts import reverse

class Journal(SoftDeletionModel):
    '''
    name - immutable
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
    
    def __str__(self):
        return self.name 

    
    def get_entries_over_period(self, start, end):
        return accounting.models.transactions.JournalEntry.objects.filter(Q(journal=self) 
            & Q(date__gte=start)
            & Q(date__lte=end))

    def get_absolute_url(self):
        return reverse("accounting:journal-detail", kwargs={"pk": self.pk})
    



class Ledger(models.Model):
    '''
    Summarizes the accounts and contains the control accounts
    all posts to the ledger must balance 
    '''
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Post(models.Model):
    '''Moving transactions from journals to the ledger, from books of primary 
    entry to books of final entry.'''
    entry = models.ForeignKey('accounting.JournalEntry', 
        on_delete=models.SET_NULL, null=True)
    debit = models.ForeignKey('accounting.Debit', 
        on_delete=models.SET_NULL, null=True)
    credit =  models.ForeignKey('accounting.Credit',
        on_delete=models.SET_NULL, null=True)
    ledger = models.ForeignKey('accounting.Ledger',
        on_delete=models.SET_NULL, null=True)


class WorkBook(models.Model):
    '''
    The workbook is an object is used to store all the adjustments 
    of an account either during reconcilliation or when a trial balance
    fails.
    Not yet implemented
    '''
    name = models.CharField(max_length=64)


class Adjustment(models.Model):
    '''
    An adjustment records the necessary changes to journal entries that 
    will balance the books. In this way, the journal entries become immutable.
    
    the form for this model will have journal entry which will be a hidden input. The adjusting entry is another journal entry created to make changes to the affected entry. 
    '''
    entry = models.ForeignKey('accounting.JournalEntry', 
        on_delete=models.CASCADE, null=True, related_name='entry')
    adjusting_entry = models.ForeignKey('accounting.JournalEntry', 
        on_delete=models.CASCADE, null=True, related_name='adjusting_entry')
    workbook = models.ForeignKey('accounting.WorkBook', 
        on_delete=models.CASCADE,null=True)
    description = models.TextField()
    created_by = models.ForeignKey('accounting.bookkeeper', 
        on_delete=models.SET_NULL, null=True,
        default=1)
    date_created = models.DateField(default=datetime.date.today)

