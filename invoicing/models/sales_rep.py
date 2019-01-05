from functools import reduce

from django.db import models
from django.db.models import Q

from .invoices.abstract import AbstractSale
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
        invoices = AbstractSale.abstract_filter(Q(status="paid") & Q(salesperson=self) \
            & (Q(due__lt=end) \
            | Q(due__gte=start)))
        #should i filter for paid invoices?

        #exclude tax in the calculation
        return reduce(lambda x, y: x + y, [i.subtotal for i in invoices], 0)
