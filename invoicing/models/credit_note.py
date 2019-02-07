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
    invoice = models.ForeignKey('invoicing.SalesInvoice', on_delete=models.SET_NULL, null=True)
    comments = models.TextField()#never allow blank comments

    @property
    def returned_products(self):
        return self.invoice.salesinvoiceline_set.filter(returned=True)
        
    @property
    def returned_total(self):
        return sum([i.returned_value for i in self.returned_products])

    @property
    def tax_credit(self):
        if not self.invoice.tax:
            return 0
        return D(self.invoice.tax.rate / 100.0) * self.returned_total
        
    @property
    def returned_total_with_tax(self):
        return self.returned_total + self.tax_credit

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

        