from functools import reduce

from django.db import models

from accounting.models import Account, Journal, JournalEntry


class OrderReturn(models.Model):
    """A document sent by a business to a supplier notifying them
    that inventory has been returned for some reason. Linked to Orders. Stores a list of products returned.
    
    properties
    -----------
    returned_items - returns a queryset of all returned products for an invoice
    returned_total - returns the numerical value of the products returned.
    
    methods
    -----------
    create_entry - creates a journal entry in the accounting system."""
    
    date = models.DateField()
    order = models.ForeignKey('inventory.Order', on_delete=models.SET_NULL, 
        null=True)
    comments = models.TextField()#never allow blank comments

    @property
    def returned_items(self):
        return self.order.orderline_set.filter(returned=True)
        
    @property
    def returned_total(self):
        return reduce(lambda x, y: x + y, [i.returned_value for i in self.returned_products], 0)

    def create_entry(self):
        
        j = JournalEntry.objects.create(
            memo="Auto generated journal entry from credit note",
            date=self.date,
            journal=Journal.objects.get(pk=3),
            draft=False,
            created_by = self.invoice.salesperson.employee.user
        )
        j.simple_entry(
            self.returned_total,
            self.invoice.customer.account,
            Account.objects.get(pk=4002))# sales returns 

        