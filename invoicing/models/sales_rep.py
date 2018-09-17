from django.db import models
from functools import reduce
from .invoices.abstract import AbstractSale
from django.db.models import Q

class SalesRepresentative(models.Model):
    '''Really just a dummy class that points to an employee. 
    allows sales and commission to be tracked.
    
    methods
    ---------
    sales - takes two dates as arguments and returns the 
    amount sold exclusive of tax. Used in commission calculation
    '''
    employee = models.OneToOneField('employees.Employee', on_delete=None,)
    number = models.AutoField(primary_key=True)
    active = models.BooleanField(default=True)
    can_reverse_invoices = models.BooleanField(default=True)
    can_offer_discounts = models.BooleanField(default=True)

    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.employee.first_name + ' ' + self.employee.last_name

    def sales(self, start, end):
        invoices = AbstractSale.abstract_filter(Q(salesperson=self) \
            & (Q(due__lt=end) \
            | Q(due__gte=start)))
        #should i filter for paid invoices?

        #exclude tax in the calculation
        return reduce(lambda x, y: x + y, [i.subtotal for i in invoices], 0)

