from functools import reduce

from django.db import models
from decimal import Decimal as D

from accounting.models import Account, Journal, JournalEntry


class CreditNote(models.Model):
    """A document sent by a seller to a customer notifying them
    that a credit has been made to their account against goods returned
    by the buyer. Linked to invoices. Stores a list of products returned.
    
    properties
    -----------
    returned_products - returns a queryset of all returned products for an invoice
    returned_total - returns the numerical value of the products returned.
    
    methods
    -----------
    create_entry - creates a journal entry in the accounting system where
        the customer account is credited and sales returns is debitted. NB 
        futher transactions will have to be made if the returned goods 
        are to be written off."""
    
    date = models.DateField()
    invoice = models.ForeignKey('invoicing.Invoice', 
            on_delete=models.SET_NULL, null=True)
    comments = models.TextField()#never allow blank comments

    @property
    def returned_products(self):
        return self.creditnoteline_set.all()
        
    @property
    def returned_total(self):
        return sum([i.returned_value for i in self.returned_products])

    @property
    def tax_credit(self):
        return sum([(i.line.tax.rate * i.quantity) \
            for i in self.creditnoteline_set.all() if i.line.tax] ,D(0))
        
    @property
    def returned_total_with_tax(self):
        return self.returned_total + self.tax_credit

    @property
    def total(self):
        return self.returned_total_with_tax

    @property
    def subtotal(self):
        return self.returned_total

    @property
    def tax_amount(self):
        return self.tax_credit

    def create_entry(self):
        j = JournalEntry.objects.create(
            memo="Auto generated journal entry from credit note",
            date=self.date,
            journal=Journal.objects.get(pk=3),
            draft=False,
            created_by = self.invoice.salesperson.employee.user
        )
        j.simple_entry(
            self.returned_total_with_tax,
            self.invoice.customer.account,
            Account.objects.get(pk=4002))# sales returns 

#TODO test
class CreditNoteLine(models.Model):
    note = models.ForeignKey('invoicing.CreditNote', null=True, 
            on_delete=models.SET_NULL)
    line = models.ForeignKey('invoicing.InvoiceLine', null=True,
            on_delete=models.SET_NULL)
    quantity = models.FloatField()

    def __str__(self):
        return "{}".format((str(self.line)))

    @property
    def returned_value(self):
        '''Factors for line by line discount'''
        discount =  self.line.product.nominal_price * \
            (self.line.discount / D(100))
        discounted_price = self.line.product.nominal_price - discount
        return D(self.quantity) * discounted_price
