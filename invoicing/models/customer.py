
from decimal import Decimal as D

from django.db import models
from django.db.models import Q
from accounting.models import Account
import inventory
from .invoices import AbstractSale

class Customer(models.Model):
    '''The customer model represents business clients to whom products are 
    sold. Customers are typically businesses and the fields reflect that 
    likelihood. Individuals however can also be represented.
    Customers can have accounts if store credit is extended to them.'''
    #make sure it can only be one or the other not both
    organization = models.OneToOneField('common_data.Organization', null=True,  
        on_delete=models.CASCADE, blank=True, unique=True)
    individual = models.OneToOneField('common_data.Individual', null=True,
        on_delete=models.CASCADE, blank=True,)    
    billing_address = models.TextField(default= "", blank=True)
    banking_details = models.TextField(default= "", blank=True)
    active = models.BooleanField(default=True)
    account = models.ForeignKey('accounting.Account', on_delete=models.CASCADE,
        null=True)#created in save method

    @property
    def invoices(self):
        return AbstractSale.abstract_filter(Q(customer=self))
    
    @property
    def name(self):
        if self.organization:
            return self.organization.legal_name
        else:
            return str(self.individual)
            
    @property
    def customer_email(self):
        if self.is_organization:
            return self.organization.email
        else:
            return self.individual.email

    @property
    def is_organization(self):
        return self.organization != None

    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is None:
            n_customers = Customer.objects.all().count() + 1
            self.account = Account.objects.create(
                name= "Customer: %s" % self.name,
                balance =0,
                id= 1100 + n_customers,
                type = 'asset',
                description = 'Account which represents credit extended to a customer',
                balance_sheet_category='current-assets'
            )
        super(Customer, self).save(*args, **kwargs)

    @property
    def credit_invoices(self):
        return [i for i in self.invoices \
            if i.status == 'sent']
        
    @property
    def age_list(self):
        #returns a 7 element tuple that enumerates the number of invoices 
        # that are, current 0-7 overude 8-14 days and so forth
        
        age_list = [0, 0, 0, 0, 0, 0]
        for inv in self.credit_invoices:
            if inv.overdue == 0:
                age_list[0] += 1
            elif inv.overdue < 8:
                age_list[1] += 1 
            elif inv.overdue < 15:
                age_list[2] += 1
            elif inv.overdue < 31:
                age_list[3] += 1 
            elif inv.overdue < 61:
                age_list[4] += 1
            else:
                age_list[5] += 1
        
        return age_list