# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person
from accounting.models import Account, Journal
from common_data.utilities import load_config
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
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

#add support for credit notes
class Invoice(models.Model):
    '''base model handles both cash and credit based invoices '''
    type_of_invoice = models.CharField(max_length=12, choices=[
        ('cash', 'Cash Invoice'),
        ('credit', 'Credit Based')], 
            default='cash')
    customer = models.ForeignKey("invoicing.Customer", null=True)
    date_issued = models.DateField( default=timezone.now)
    due_date = models.DateField( default=timezone.now)
    terms = models.CharField(max_length = 64, 
        default=load_config()['default_terms'])# give finite choices
    comments = models.TextField(blank=True, 
        default=load_config()['default_invoice_comments'])
    number = models.AutoField(primary_key = True)
    tax = models.ForeignKey('accounting.Tax', null=True)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative', null=True)
    account = models.ForeignKey("accounting.Account", null=True, blank=True)
    active = models.BooleanField(default=True)
    
    def delete(self):
        self.active = False
        self.save()

    @property
    def subtotal(self):
        return reduce(lambda x, y: x+ y, 
            [i.subtotal for i in self.invoiceitem_set.all()], 0)
       
    @property
    def total(self):
        return self.subtotal + self.tax_amount


    @property
    def tax_amount(self):
        return self.subtotal * (self.tax.rate / 100.0)
    
    def __str__(self):
        if self.type_of_invoice == "cash":
            return 'CINV' + str(self.pk)
        else: 
            return 'DINV' + str(self.pk)
    
    def create_payment(self):
        if self.type_of_invoice == 'credit':
            pmt = Payment.objects.create(invoice=self,
                amount=self.total,
                date=self.date_issued,
                sales_rep = self.salesperson,
            )
            return pmt
        else:
            raise ValueError('The invoice Type specified cannot have' + 
                'separate payments, change to "credit" instead.')
    
    def create_transaction(self):
        config = load_config()
        if self.type_of_invoice == "cash":
            t = Transaction.objects.create(
                reference='INV' + str(self.pk),
                memo= 'Auto generated transaction from cash invoice.',
                date=self.date_issued,
                time='00:00',
                amount = self.subtotal, #might change to total
                credit = self.account if self.account else \
                    Account.objects.get(pk=config['invoice_account']),
                debit=self.customer.account \
                    if self.customer.account else \
                        Account.objects.get(pk=config['sales_account']),
                Journal =Journal.objects.get(pk=config['journal'])
            )
            return t
        else:
            raise ValueError('Only cash based invoices generate transactions')

    def update_inventory(self):
        for item in self.invoiceitem_set.all():
            item.item.decrement(item.quantity)
             

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
    employee = models.OneToOneField('accounting.Employee', null=True)
    number = models.AutoField(primary_key=True)
    active = models.BooleanField(default=True)

    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.employee.first_name + ' ' + self.employee.last_name

    def sales(self, start, end):
        invoices = Invoice.objects.filter(Q(salesperson=self) \
            & (Q(due_date__lt=end) \
            | Q(due_date__gte=start)))

        return reduce(lambda x, y: x + y, [i.subtotal for i in invoices], 0)

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
    
    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount

    def create_receipt(self):
        r = Receipt.objects.create(payment=self,
            comments='Auto generated receipt from a payment object')

        return r

    def save(self, *args, **kwargs):
        if self.invoice.type_of_invoice == "cash":
            raise ValueError('Only Credit Invoices can create payments')
        else:
            super(Payment, self).save(*args, **kwargs)
            config = load_config()
            Transaction.objects.create(
                reference='PAY' + str(self.pk),
                memo= 'Auto generated transaction from payment.',
                date=self.date,
                amount = self.amount, #might change to total
                credit = Account.objects.get(
                    pk=config['invoice_account']),
                debit=self.invoice.customer.account \
                    if self.invoice.customer.account else \
                        Account.objects.get(pk=config['sales_account']),
                Journal =Journal.objects.get(pk=config['journal'])
            )
        


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
        return self.subtotal * (self.tax.rate / 100.0)

    @property
    def subtotal(self):
        return reduce((lambda x,y: x + y), 
            [i.subtotal for i in self.quoteitem_set.all()])

    def __str__(self):
        return 'QUO' + str(self.number)

    def create_invoice(self):
        if not self.invoiced:
            Invoice.objects.create(
                customer=self.customer,
                date_issued=self.date,
                comments = self.comments,
                tax=self.tax,
                salesperson=self.salesperson
            )
            inv = Invoice.objects.latest('pk')
            for item in self.quoteitem_set.all():
                inv.invoiceitem_set.create(
                    item=item.item,
                    quantity=item.quantity,
                    price=item.price,# set this way to ensure invoice price matches quote price
                    discount=item.discount
                )
            self.invoiced = True
            self.save()
            return inv

class QuoteItem(models.Model):
    quote = models.ForeignKey('invoicing.Quote', null=True)
    item = models.ForeignKey('inventory.Item', null=True)
    quantity = models.FloatField()
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
            (self.total_without_discount * (self.discount / 100.0))

    def update_price(self):
        self.price = self.item.unit_sales_price
        self.save()

class Receipt(models.Model):
    #make sure one of the two options is selected
    payment = models.OneToOneField('invoicing.Payment', null=True)
    comments = models.TextField()
    
    def __str__(self):
        return 'RPT' + str(self.pk)