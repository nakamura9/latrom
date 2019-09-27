from django.db import models

from accounting.models import Account, Journal, JournalEntry
from decimal import Decimal as D
from common_data.models import SoftDeletionModel

class Payment(SoftDeletionModel):
    '''Model represents payments made by credit customers only!
    These transactions are currently implemented to require full payment 
    of each invoice. Support for multiple payments for a single invoice
    may be considered as required by clients.
    Information stored include data about the invoice, the amount paid 
    and other notable comments
    
    methods
    ---------
    create_entry - returns the journal entry that debits the customer account
        and credits the sales account. Should also impact tax accounts'''
    PAYMENT_METHODS = [("cash", "Cash" ),
                        ("transfer", "Transfer"),
                        ("debit card", "Debit Card"),
                        ("ecocash", "EcoCash")]
    invoice = models.ForeignKey("invoicing.Invoice", 
        on_delete=models.SET_NULL, 
        null=True)
    amount = models.DecimalField(max_digits=16,decimal_places=2)
    date = models.DateField()
    method = models.CharField(
        max_length=32, 
        choices=PAYMENT_METHODS,
        default='transfer')
    reference_number = models.AutoField(primary_key=True)
    sales_rep = models.ForeignKey("invoicing.SalesRepresentative", 
        on_delete=models.SET_NULL, null=True,)
    comments = models.TextField(default="Thank you for your business")
    entry = models.ForeignKey('accounting.JournalEntry', null=True, blank=True, 
        on_delete=models.SET_NULL)
    
    
    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount

    def create_entry(self):
        '''payment entries credit the customer account and debits the cash book'''
        if self.entry:
            return 
        j = JournalEntry.objects.create(
                memo= f'Journal entry for payment #{self.pk} from invoice #{self.invoice.invoice_number}.',
                date=self.date,
                journal =Journal.objects.get(pk=3),
                created_by = self.sales_rep.employee.user,
                draft=False
            )
        
        # split into sales tax and sales
        
        j.simple_entry(
            self.amount,
            self.invoice.customer.account,
            Account.objects.get(
                pk=1000),#cash in checking account
        )
        #change invoice status if  fully paid
        if self.invoice.total_due <= 0:
            self.invoice.status = "paid"
        else:
            self.invoice.status = "paid-partially"
        self.entry = j
        self.save()
        self.invoice.save()

    