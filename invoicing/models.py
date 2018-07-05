# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person
from accounting.models import Account, Journal
from common_data.utilities import load_config
from accounting.models import Employee, JournalEntry, Tax, Debit, Credit

class Customer(models.Model):
    name = models.CharField(max_length=64, default="")
    tax_clearance = models.CharField(max_length=64, default="", blank=True)
    business_address = models.TextField(default= "", blank=True)
    billing_address = models.TextField(default= "", blank=True)
    banking_details = models.TextField(default= "", blank=True)
    contact_person = models.ForeignKey('invoicing.ContactPerson', null=True, blank=True)
    active = models.BooleanField(default=True)
    website = models.CharField(default= "",max_length=64, blank=True)
    email=models.CharField(default= "",max_length=64, blank=True)
    phone = models.CharField(default= "",max_length=64, blank=True)
    account = models.ForeignKey('accounting.Account', null=True, blank=True)
    
    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.name    

class ContactPerson(Person):
    '''inherits from the base person class in common data
    represents clients of the business with entry specific details.
    the customer can also have an account with the business for credit 
    purposes
    A customer may be a stand alone individual or part of a business organization.
    '''
    phone_two = models.CharField(max_length = 16,blank=True , default="")
    other_details = models.TextField(blank=True, default="")
    
    def delete(self):
        self.active = False
        self.save()

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
        default=load_config().get('default_invoice_comments', ""))

    number = models.AutoField(primary_key = True)
    tax = models.ForeignKey('accounting.Tax', null=True)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative', null=True)
    active = models.BooleanField(default=True)
    purchase_order_number = models.CharField(blank=True, max_length=32)
    
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
        return self.subtotal * decimal.Decimal((self.tax.rate / 100.0))
    
    def __str__(self):
        if self.type_of_invoice == "cash":
            return 'CINV' + str(self.pk)
        else: 
            return 'DINV' + str(self.pk)

    def save(self, *args, **kwargs):
        if self.type_of_invoice == "credit" and self.customer.account == None:
            raise ValueError('You cannot create a credit invoice for customers without an account with the organization')
        else:
            super(Invoice, self).save(*args, **kwargs)
    
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
    
    def create_entry(self):
        config = load_config()
        if self.type_of_invoice == "cash":
            t = JournalEntry.objects.create(
                reference='INV' + str(self.pk),
                memo= 'Auto generated Entry from cash invoice.',
                date=self.date_issued,
                journal =Journal.objects.get(pk=3)#Sales Journal
            )
            Debit.objects.create(
                amount = self.total,
                entry= t,
                account = self.customer.account \
                    if self.customer.account else \
                        Account.objects.get(pk=4000),
            )
            # current account
            Credit.objects.create(
                amount = self.subtotal,
                entry= t,
                account=Account.objects.get(pk=1000),
            )
            #credit tax to tax account 
            Credit.objects.create(
                amount = self.tax_amount,
                entry= t,
                account= Account.objects.get(pk=2001),
            )
            return t
        else:
            raise ValueError('Only cash based invoices generate entries')

    def update_inventory(self):
        for item in self.invoiceitem_set.all():
            item.item.decrement(item.quantity)
             

class InvoiceItem(models.Model):
    '''Items listed as part of an invoice'''
    invoice = models.ForeignKey('invoicing.Invoice', null=True)
    item = models.ForeignKey("inventory.Item", null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    returned_quantity = models.FloatField(default=0.0)
    returned = models.BooleanField(default=False)

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

    def _return(self, quantity):
        self.returned_quantity  = float(quantity)
        if self.returned_quantity > 0:
            self.returned =True
        self.save()

    @property
    def returned_value(self):
        return self.price * decimal.Decimal(self.returned_quantity)

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
    amount = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=32, choices=[("cash", "Cash" ),
                                        ("transfer", "Transfer"),
                                        ("debit card", "Debit Card"),
                                        ("ecocash", "EcoCash")],
                                        default='transfer')
    reference_number = models.AutoField(primary_key=True)
    sales_rep = models.ForeignKey("invoicing.SalesRepresentative", null=True)
    comments = models.TextField(default="Thank you for your business")
    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount

    def create_receipt(self):
        r = Receipt.objects.create(payment=self,
            comments='Auto generated receipt from a payment object')
        return r

    def delete(self):
        self.active = False
        self.save()

    def save(self, *args, **kwargs):
        if self.invoice.type_of_invoice == "cash":
            raise ValueError('Only Credit Invoices can create payments')
        else:
            super(Payment, self).save(*args, **kwargs)
            config = load_config()
            j = JournalEntry.objects.create(
                reference='PAY' + str(self.pk),
                memo= 'Auto generated journal entry from payment.',
                date=self.date,
                journal =Journal.objects.get(pk=3)
            )
            #3 args
            j.simple_entry(
                self.amount,
                Account.objects.get(
                    pk=1000),
                self.invoice.customer.account
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
        return self.subtotal * decimal.Decimal(self.tax.rate /100.0)

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
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        super(QuoteItem, self).save(*args, **kwargs)
        if not self.price:
            self.price = self.item.unit_sales_price
            self.save()
    
    @property
    def total_without_discount(self):
        return self.price * decimal.Decimal(self.quantity)
    
    @property
    def subtotal(self):
        return self.total_without_discount - \
            (self.total_without_discount * decimal.Decimal((self.discount / decimal.Decimal(100.0))))

    def update_price(self):
        self.price = self.item.unit_sales_price
        self.save()


class CreditNote(models.Model):
    """A document sent by a seller to a customer notifying them
    that a credit has been made to their account against goods returned
    by the buyer. Linked to invoices. Stores a list of items returned."""
    date = models.DateField()
    invoice = models.ForeignKey('invoicing.Invoice')
    comments = models.TextField()

    @property
    def returned_items(self):
        return self.invoice.invoiceitem_set.filter(returned=True)
        
    @property
    def returned_total(self):
        return reduce(lambda x, y: x + y, [i.returned_value for i in self.returned_items], 0)

    def create_entry(self):
        j = JournalEntry.objects.create(
            reference = 'CN' + str(self.pk),
            memo="Auto generated journal entry from credit note",
            date=self.date,
            journal=Journal.objects.get(pk=3)
        )
        j.simple_entry(
            self.returned_total,
            self.invoice.customer.account,
            Account.objects.get(pk=4002))

    def save(self, *args, **kwargs):
        super(CreditNote, self).save(*args, **kwargs)
        self.create_entry()