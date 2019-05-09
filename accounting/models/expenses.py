import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone
import accounting
from django.shortcuts import reverse


expense_choices = [
    'Advertising', 
    'Bank Service Charges', 
    'Equipment Rental', 
    'Dues and Subscriptions', 
    'Telephone', 
    'Vehicles', 
    'Travel and Expenses',
    'Rent', 
    'Payroll Taxes', 
    'Insurance', 
    'Office Expenses',
    'Carriage Outwards', 
    'Other']

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
    debit_account = models.ForeignKey('accounting.Account', 
        on_delete=models.SET_NULL, null=True, limit_choices_to=Q(type="asset"))
    recorded_by = models.ForeignKey('auth.user', default=1, 
        on_delete=models.SET_NULL, null=True)
    reference = models.CharField(max_length=32, blank=True, default="")
    entry= models.ForeignKey('accounting.journalentry', 
        on_delete=models.SET_NULL,
        blank=True, 
        null=True)
    
    class Meta:
        abstract = True

    @property
    def category_string(self):
        return dict(EXPENSE_CHOICES)[self.category]
   
    @property
    def expense_account(self):
        mapping = {
            0: 5000,
            1: 5001,
            2: 5003,
            3: 5002,
            4: 5004,
            5: 5005,
            6: 5006,
            7: 5007,
            8: 5009,
            9: 50010,
            10: 5012,
            11: 5013,
            12: 5014,
            13: 5015
       }
        return accounting.models.accounts.Account.objects.get(pk=mapping[self.category])


class Expense(AbstractExpense):
    date = models.DateField()
    billable = models.BooleanField(default=False)
    customer = models.ForeignKey('invoicing.Customer', on_delete=models.SET_NULL, null=True,
        blank=True)
    
    def __str__(self):
        return f"{self.date}: {self.reference}"

    def create_entry(self):
        if self.entry:
            return
        j = accounting.models.transactions.JournalEntry.objects.create(
            date = self.date,
            memo =  "Expense recorded. Category: %s." % self.category,
            journal = accounting.models.books.Journal.objects.get(pk=2),# cash disbursements
            created_by=self.recorded_by,
            draft= False
        )
        #credit cash and debit expense account
        j.credit(self.amount,accounting.models.accounts.Account.objects.get(pk=1000))
        j.debit(self.amount,self.expense_account)
        
        #only create accounts payable after billing the customer
        self.entry = j
        self.save()
       

    def save(self, *args, **kwargs):
        flag = self.pk
        if self.billable and self.customer == None:
            raise ValueError('A billable expense needs a customer')
        
        super(Expense, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''Create a reversing entry for expenses'''
        j = accounting.models.transactions.JournalEntry.objects.create(
            date=self.date,
            memo=f"Reversing transaction for expense with id {self.pk}",
            journal=accounting.models.books.Journal.objects.get(pk=2),# cash disbursements
            created_by=self.recorded_by,
            draft= False
        )

        j.credit(self.amount, self.expense_account)
        j.debit(self.amount, 
            accounting.models.accounts.Account.objects.get(pk=1000))

        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("accounting:expense-detail", kwargs={"pk": self.pk})


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
    start_date = models.DateField(default=datetime.date.today)
    last_created_date = models.DateField(null=True, blank=True)

    @property
    def cycle_string(self):
        return dict(self.EXPENSE_CYCLE_CHOICES)[self.cycle]
    
    @property
    def is_current(self):
        return datetime.date.today() < self.expiration_date

    def create_standalone_expense(self):
        self.last_created_date = datetime.date.today()
        self.save()

        return Expense.objects.create(
            reference=self.pk,
            date=datetime.date.today(),
            description=self.description,
            category=self.category,
            amount=self.amount,
            debit_account=self.debit_account,
            recorded_by=self.recorded_by
        )
        
    @property
    def related_payments(self):
        return Expense.objects.filter(reference=self.pk)

    def __str__(self):
        return "{} - {} Expense".format(self.pk, self.category_string)

    def get_absolute_url(self):
        return reverse("accounting:recurring-expense-detail", kwargs={"pk": self.pk})
    