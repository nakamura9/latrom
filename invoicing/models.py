# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone

from common_data.models import Person
from accounting.models import Employee, Transaction, Tax


class Customer(Person):
    '''inherits from the base person class in common data
    represents clients of the business with transactional specific details.
    the customer can also have an account with the business for credit 
    purposes'''

    billing_address = models.CharField(max_length =128,blank=True , default="")
    phone_two = models.CharField(max_length = 16,blank=True , default="")
    account_number = models.CharField(max_length= 16,blank=True , default="") #change
    other_details = models.TextField(blank=True, default="")
    account = models.ForeignKey('accounting.Account', null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

#add support for credit notes
class Invoice(models.Model):
    '''base model handles both cash and credit based invoices '''
    type_of_invoice = models.CharField(max_length=12, choices=[('cash', 'Cash Invoice'),('credit', 'Credit Based')], default='cash')
    customer = models.ForeignKey("invoicing.Customer", null=True)
    date_issued = models.DateField( default=timezone.now)
    due_date = models.DateField( default=timezone.now)
    terms = models.CharField(max_length = 64, default='Payment strictly in 7 days')# give finite choices
    comments = models.TextField(blank=True)
    number = models.AutoField(primary_key = True)
    tax = models.ForeignKey('accounting.Tax', null=True)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative', null=True)
    account = models.ForeignKey("accounting.Account", null=True)#provide a default

    @property
    def subtotal(self):
        total = 0
        for item in self.invoiceitem_set.all():
            total += item.subtotal
        return total

    @property
    def total(self):
        return self.subtotal + self.tax_amount


    @property
    def tax_amount(self):
        return self.subtotal * (self.tax.rate / 100)
    
    def __str__(self):
        if self.type_of_invoice == "cash":
            return 'CINV' + str(self.pk)
        else: 
            return 'DINV' + str(self.pk)
    
    def create_payment(self):
        Payment(invoice=self,
            amount=self.total,
            date=self.date_issued,
            sales_rep = self.salesperson,
            ).save()

    def save(self, *args, **kwargs):
        super(Invoice, self).save(*args, **kwargs)
        #make sure updates dont do this again
        for item in self.invoiceitem_set.all():
            item.item.quantity -= item.quantity
        

class InvoiceItem(models.Model):
    '''Items listed as part of an invoice'''
    invoice = models.ForeignKey('invoicing.Invoice', null=True)
    item = models.ForeignKey("inventory.Item", null=True)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    discount = models.FloatField(default=0)

    def __str__(self):
        return self.item.item_name + " * " + str(self.quantity)

    @property
    def total_without_discount(self):
        return self.quantity * self.price

    @property
    def subtotal(self):
        return self.total_without_discount - \
            (self.total_without_discount * (self.discount / 100))

    def save(self, *args, **kwargs):
        super(InvoiceItem, self).save(*args, **kwargs)
        # the idea is to save a snapshot of the price the moment
        # the invoice was created
        if not self.price:
            self.price = self.item.unit_sales_price
            self.save()

    def update_price(self):
        self.price = self.item.unit_sales_price
        self.save()


class SalesRepresentative(models.Model):
    employee = models.ForeignKey('accounting.Employee', null=True)
    number = models.AutoField(primary_key=True)

    def __str__(self):
        return self.employee.first_name + ' ' + self.employee.last_name

class Payment(models.Model):
    invoice = models.OneToOneField("invoicing.Invoice", null=True)
    amount = models.FloatField()
    date = models.DateField()
    method = models.CharField(max_length=32, choices=[("cash", "Cash" ),
                                        ("transfer", "Transfer"),
                                        ("debit card", "Debit Card"),
                                        ("ecocash", "EcoCash")],
                                        default='transfer')
    reference_number = models.AutoField(primary_key=True)
    sales_rep = models.ForeignKey("invoicing.SalesRepresentative", null=True)
    account = models.ForeignKey("accounting.Account", null=True)

    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount

    def create_receipt(self):
        Receipt(payment=self,
            comments='Auto generated receipt from a payment object').save()

class Quote(models.Model):
    date = models.DateField(default=datetime.date.today)
    customer = models.ForeignKey('invoicing.Customer', null=True)
    number = models.AutoField(primary_key = True)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative', null=True)
    comments = models.TextField(null = True, blank=True)
    tax = models.ForeignKey('accounting.Tax', null=True)
    invoiced = models.BooleanField(default=False)
    

    @property
    def total(self):
        return self.subtotal + self.tax_amount 

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax.rate / 100)

    @property
    def subtotal(self):
        return reduce((lambda x,y: x + y), 
            [i.price * i.quantity for i in self.quoteitem_set.all()])

    def __str__(self):
        return 'QUO' + str(self.number)

    def create_invoice(self):
        if not self.invoiced:
            Invoice(
                customer=self.customer,
                date_issued=self.date,
                comments = self.comments,
                tax=self.tax,
                salesperson=self.salesperson
            ).save()
            inv = Invoice.objects.latest('pk')
            for item in self.quoteitem_set.all():
                inv.invoiceitem_set.create(
                    item=item.item,
                    quantity=item.quantity,
                    price=item.price,
                    discount=item.discount
                )
            self.invoiced = True

class QuoteItem(models.Model):
    quote = models.ForeignKey('invoicing.Quote', null=True)
    item = models.ForeignKey('inventory.Item', null=True)
    quantity = models.IntegerField()
    price = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        super(QuoteItem, self).save(*args, **kwargs)
        if not self.price:
            self.price = self.item.unit_sales_price
            self.save()
    
    @property
    def total_without_discount(self):
        return self.price * self.quantity
    
    @property
    def subtotal(self):
        return self.total_without_discount - \
            (self.total_without_discount * (self.discount / 100))

    def update_price(self):
        self.price = self.item.unit_sales_price
        self.save()

class Receipt(models.Model):
    #make sure one of the two options is selected
    payment = models.OneToOneField('invoicing.Payment', null=True)
    comments = models.TextField()
    
    def __str__(self):
        return 'RPT' + str(self.pk)