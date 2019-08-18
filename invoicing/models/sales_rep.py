from functools import reduce

from django.db import models
from django.db.models import Q

from invoicing.models.invoice import Invoice
from common_data.models import SoftDeletionModel

class SalesRepresentative(SoftDeletionModel):
    '''Really just a dummy class that points to an employee. 
    allows sales and commission to be tracked.
    
    methods
    ---------
    sales - takes two dates as arguments and returns the 
    amount sold exclusive of tax. Used in commission calculation
    '''
    employee = models.OneToOneField('employees.Employee', on_delete=models.SET_NULL, null=True,)
    number = models.AutoField(primary_key=True)
    can_reverse_invoices = models.BooleanField(default=True)
    can_offer_discounts = models.BooleanField(default=True)


    def __str__(self):
        return self.employee.first_name + ' ' + self.employee.last_name

    def sales(self, start, end):
        '''
        Sales only count for paid invoices
        '''
        invoices = Invoice.objects.filter(Q(status="paid") & 
            Q(salesperson=self) 
            & (Q(due__lt=end) 
            | Q(due__gte=start)))

        #exclude tax in the calculation
        return sum([i.subtotal for i in invoices])
