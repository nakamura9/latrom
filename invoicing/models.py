# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person
from common_data.utilities import load_config
from accounting.models import Account, Journal, JournalEntry, Tax, Debit, Credit
from employees.models import Employee


# used in default fields for invoices
def get_default_comments():
    load_config().get('default_invoice_comments', "")
    
def get_default_terms():
    load_config().get('default_terms', "")

class Customer(models.Model):
    '''The customer model represents business clients to whom products are 
    sold. Customers are typically businesses and the fields reflect that 
    likelihood. Individuals however can also be represented.
    Customers can have accounts if store credit is extended to them.'''
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

    def save(self, *args, **kwargs):
        if self.pk is None:
            n_customers = Customer.objects.all().count()
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
        return [i for i in Invoice.objects.filter(
            Q(type_of_invoice='credit') & Q(customer=self)) \
            if not i.paid_in_full]
        
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

INVOICE_TYPES = [
    ('cash', 'Cash Invoice'),
    ('credit', 'Credit Based')
    ]

class Invoice(models.Model):
    '''Represents the document sent by a selling party to a buyer.
    It outlines the items purchased, their cost and other features
    such as the seller's information and the buyers information.
    An aggregate relationship with the InvoiceItem class. 
    
    methods
    ----------
    create_payment - used only for credit invoices creates a complete
        payment for the invoice object.
    create_entry - journal entry created where the sales and tax accounts are 
        credited and the inventory account is debited
    update_inventory - decrements each item in the inventory

    properties
    ------------
    subtotal - returns the sale value of the invoice
    total - returns the price inclusive of tax
    tax_amount - returns the amount of tax due on an invoice
    
    '''
    type_of_invoice = models.CharField(max_length=12, 
        choices=INVOICE_TYPES, default='cash')
    customer = models.ForeignKey("invoicing.Customer", null=True)
    date_issued = models.DateField( default=timezone.now)
    due_date = models.DateField( default=timezone.now)
    date_paid = models.DateField(default=timezone.now)
    ship_from = models.ForeignKey('inventory.WareHouse', null=True)
    terms = models.CharField(max_length = 128, blank=True, null=True, 
        default=get_default_terms)
    comments = models.TextField(blank=True, null=True, 
        default=get_default_comments)
    number = models.AutoField(primary_key = True)
    tax = models.ForeignKey('accounting.Tax', null=True)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative', null=True)
    active = models.BooleanField(default=True)
    purchase_order_number = models.CharField(blank=True, max_length=32)
    
    @property
    def paid_in_full(self):
        payments = Payment.objects.filter(invoice=self)
        return reduce(lambda x, y:x + y, [p.amount for p in payments], 0) == \
            self.total

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

    def add_item(self, item, quantity,discount):
        self.invoiceitem_set.create(
            item=item, 
            quantity=quantity,
            discount=discount
        )
    def remove_item(self, item_pk):
        # remove an item from an invoice
        pass

    @property
    def tax_amount(self):
        if self.tax:
            return self.subtotal * decimal.Decimal((self.tax.rate / 100.0))
        return 0

    def __str__(self):
        if self.type_of_invoice == "cash":
            return 'CINV' + str(self.pk)
        else: 
            return 'DINV' + str(self.pk)
        
    @property
    def overdue(self):
        if self.paid_in_full:
            return 0
        today = datetime.date.today()
        if today < self.due_date:
            return 0
        else:
            delta = today- self.due_date
        return delta.days
    
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
        if self.type_of_invoice == "cash":
            j = JournalEntry.objects.create(
                reference='INV' + str(self.pk),
                memo= 'Auto generated Entry from cash invoice.',
                date=self.date_issued,
                journal =Journal.objects.get(pk=1)#Sales Journal
            )
            j.credit(self.total, Account.objects.get(pk=4009))#inventory
            j.debit(self.subtotal, Account.objects.get(pk=4000))#sales
            j.debit(self.tax_amount,Account.objects.get(pk=2001))#sales tax

            return j
        else:
            j = JournalEntry.objects.create(
                reference='INV' + str(self.pk),
                memo= 'Auto generated Entry from cash invoice.',
                date=self.date_issued,
                journal =Journal.objects.get(pk=3)#Sales Journal
            )
            j.credit(self.total, Account.objects.get(pk=4009))#inventory
            j.debit(self.total, self.customer.account)#sales
            
            return j

    def update_inventory(self):
        #called in views.py
        for item in self.invoiceitem_set.all():
            #check if ship_from has the item in sufficient quantity
             self.ship_from.decrement_item(item.item, item.quantity)

class InvoiceItem(models.Model):
    '''Items listed as part of an invoice. Records the price for that 
    particular invoice and the discount offered as well as the quantity
    returned to the business.Part of an aggregate with invoice.

    methods
    -----------
    update_price - can be used to reflect the new unit sales 
        price when a change happens in inventory as a result of
        an order
    _return - returns some or all of the ordered quantity to the business
        as a result of some error or shortcoming in the product.
    
    properties
    -----------
    total_without_discount - the value of the ordered items without 
        a discount applied
    subtotal - value inclusive of discount
    returned_value - value of goods returned to store
    
    '''
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
    '''Really just a dummy class that points to an employee. 
    allows sales and commission to be tracked.
    
    methods
    ---------
    sales - takes two dates as arguments and returns the 
    amount sold exclusive of tax. Used in commission calculation
    '''
    employee = models.OneToOneField('employees.Employee', null=True)
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
    '''Model represents payments made by credit customers only!
    These transactions are currently implemented to require full payment 
    of each invoice. Support for multiple payments for a single invoice
    may be considered as required by clients.
    Information stored include data about the invoice, the amount paid 
    and other notable comments
    
    methods
    ---------
    create_entry - returns the journal entry that debits the customer account
        and credits the sales account. Should also impact tax accounts'''
    invoice = models.ForeignKey("invoicing.Invoice", null=True)
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


    def delete(self):
        self.active = False
        self.save()

    def create_entry(self):
        j = JournalEntry.objects.create(
                reference='PMT' + str(self.pk),
                memo= 'Auto generated journal entry from payment.',
                date=self.date,
                journal =Journal.objects.get(pk=3)
            )
        
        # split into sales tax and sales
        if not self.invoice.tax:
            j.simple_entry(
                self.amount,
                self.invoice.customer.account,
                Account.objects.get(
                    pk=4000),#sales account
            )
        else:
            # will now work for partial payments
            j.debit(self.amount, self.invoice.customer.account)
            # calculate tax as a proportion of the amount paid
            tax_amount = self.amount * decimal.Decimal(self.invoice.tax.rate / 100.0)
            # sales account
            j.credit(self.amount - tax_amount, Account.objects.get(pk=4000))
            # tax
            j.credit(tax_amount, Account.objects.get(pk=2001))
            

    def save(self, *args, **kwargs):
        flag = self.pk
        if self.invoice.type_of_invoice == "cash":
            raise ValueError('Only Credit Invoices can create payments')
        else:
            # to prevent a transaction during an update
            super(Payment, self).save(*args, **kwargs)
            if flag is None:
                self.create_entry()

class Quote(models.Model):
    '''Model that represents a quotation set to a client for 
    some product. This model is similar in structure to an invoice 
    the difference being it does not affect the chart of accounts or
    the inventory. Forms an aggregate with QuoteItem
    
    methods
    ----------
    create_invoice - uses the data from the quotation to create an invoice
        based on the quote including the quoted prices!
    
    properties
    -----------
    total - returns the sale value and the tax 
    subtotal - returns the sale value of the quoted items
    tax_amount -returns the amount of tax due for the quoted items.

    '''
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

    def add_item(self, item, quantity, discount):
        self.quoteitem_set.create(
                quantity=quantity,
                item=item,
                discount=discount)

    def create_invoice(self):
        if not self.invoiced:
            #only one should exist
            Invoice.objects.create(
                customer=self.customer,
                date_issued=self.date,
                comments = self.comments,
                tax=self.tax,
                salesperson=self.salesperson,
                terms = "Please contact the supplier for details regarding payment terms.",
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
    '''Part of Quotations in aggregate form. similar to invoice item 
    in that it maintains a link to an invoice item and maintains its own price
    and discount values.
    
    properties
    -----------
    total_without_discount - returns the full value of quoted item.
    subtotal - includes the discount subtracted from the full value.
    
    methods
    -----------
    update_price - changes the price of the product based on the value
    stored in the inventory.
    '''
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
    by the buyer. Linked to invoices. Stores a list of items returned.
    
    properties
    -----------
    returned_items - returns a queryset of all returned items for an invoice
    returned_total - returns the numerical value of the items returned.
    
    methods
    -----------
    create_entry - creates a journal entry in the accounting system where
        the customer account is credited and sales returns is debitted. NB 
        futher transactions will have to be made if the returned goods 
        are to be written off."""
    
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
            Account.objects.get(pk=4002))# sales returns 

    def save(self, *args, **kwargs):
        super(CreditNote, self).save(*args, **kwargs)
        # to prevent a transaction during an update
        if not self.pk is None:
            return
        self.create_entry()