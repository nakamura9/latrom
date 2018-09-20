from django.db import models

from accounting.models import Account, Journal, JournalEntry


class Payment(models.Model):
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
    PAYMENT_FOR_CHOICES = [
        (0, 'Sales'),
        (1, 'Service'),
        (2, 'Bill'),
        (3, 'Combined')
    ]
    PAYMENT_METHODS = [("cash", "Cash" ),
                        ("transfer", "Transfer"),
                        ("debit card", "Debit Card"),
                        ("ecocash", "EcoCash")]
    payment_for = models.PositiveSmallIntegerField(
        choices = PAYMENT_FOR_CHOICES
        )
    #only one of the four is selected
    sales_invoice = models.ForeignKey("invoicing.SalesInvoice", 
        on_delete=models.CASCADE, null=True)
    service_invoice = models.ForeignKey("invoicing.ServiceInvoice", 
        on_delete=models.CASCADE,null=True)
    bill = models.ForeignKey("invoicing.Bill", on_delete=models.CASCADE,
        null=True)
    combined_invoice = models.ForeignKey("invoicing.CombinedInvoice", 
        on_delete=models.CASCADE,null=True)
    amount = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField()
    method = models.CharField(
        max_length=32, 
        choices=PAYMENT_METHODS,
        default='transfer')
    reference_number = models.AutoField(primary_key=True)
    sales_rep = models.ForeignKey("invoicing.SalesRepresentative", 
        on_delete=None,)
    comments = models.TextField(default="Thank you for your business")

    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount


    def delete(self):
        self.active = False
        self.save()
    
    @property
    def invoice(self):
        options = {
            0: self.sales_invoice,
            1: self.service_invoice,
            2: self.bill,
            3: self.combined_invoice
        }
        return options[self.payment_for]

    def create_entry(self):
        '''payment entries credit the customer account and debits the cash book'''
        j = JournalEntry.objects.create(
                reference='PMT' + str(self.pk),
                memo= 'Auto generated journal entry from payment.',
                date=self.date,
                journal =Journal.objects.get(pk=3)
            )
        
        # split into sales tax and sales
        if not self.invoice.tax:
            j.simple_entry(
                self.amount,
                self.invoice.customer.account,
                Account.objects.get(
                    pk=4000),#sales account
            )
        else:
            # will now work for partial payments
            j.debit(self.amount, self.invoice.customer.account)
            # calculate tax as a proportion of the amount paid
            tax_amount = self.amount * D(self.invoice.tax.rate / 100.0)
            # sales account
            j.credit(self.amount - tax_amount, Account.objects.get(pk=4000))
            # tax
            j.credit(tax_amount, Account.objects.get(pk=2001))
        
        #change invoice status if  fully paid
        if self.invoice.total_due == 0:
            self.invoice.status = "paid"
            self.invoice.save()
