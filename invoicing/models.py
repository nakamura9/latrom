# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person
from services.models import Service
from accounting.models import Account, Journal, JournalEntry, Tax, Expense
from employees.models import Employee
from common_data.models import SingletonModel
import inventory
import itertools

class SalesConfig(SingletonModel):
    DOCUMENT_THEME_CHOICES = [
        (1, 'Simple'),
        (2, 'Blue'),
        (3, 'Steel'),
        (4, 'Verdant'),
        (5, 'Warm')
    ]
    CURRENCY_CHOICES = [('$', 'Dollars($)'), ('R', 'Rand')]
    default_invoice_comments = models.TextField(blank=True)
    default_quotation_comments = models.TextField(blank=True)
    default_credit_note_comments = models.TextField(blank=True)
    default_terms = models.TextField(blank=True)
    sales_tax = models.ForeignKey('accounting.Tax', null=True, blank="True")
    include_shipping_address = models.BooleanField(default=False)
    business_address = models.TextField(blank=True)
    logo = models.ImageField(null=True,upload_to="logo/")
    document_theme = models.IntegerField(choices= DOCUMENT_THEME_CHOICES)
    currency = models.CharField(max_length=1, choices=CURRENCY_CHOICES)
    apply_price_multiplier = models.BooleanField(default=False)
    price_multiplier =models.FloatField(default=0.0)
    business_name = models.CharField(max_length=255)
    payment_details = models.TextField(blank=True)
    contact_details = models.TextField(blank=True)
    include_tax_in_invoice = models.BooleanField(default=True)
    include_units_in_sales_invoice = models.BooleanField(default=True)
    business_registration_number = models.CharField(max_length=32,blank=True)

    @classmethod
    def get_config_dict(cls):
        d = cls.objects.first().__dict__
        del d['_state']
        return d

    @classmethod
    def logo_url(cls):
        conf = cls.objects.first()
        if conf.logo:
            return conf.logo.url
        return ""


class Customer(models.Model):
    '''The customer model represents business clients to whom products are 
    sold. Customers are typically businesses and the fields reflect that 
    likelihood. Individuals however can also be represented.
    Customers can have accounts if store credit is extended to them.'''
    #make sure it can only be one or the other not both
    organization = models.OneToOneField('common_data.Organization', null=True,
        blank=True, unique=True)
    individual = models.OneToOneField('common_data.Individual', null=True,
        blank=True,)    
    billing_address = models.TextField(default= "", blank=True)
    banking_details = models.TextField(default= "", blank=True)
    active = models.BooleanField(default=True)
    account = models.ForeignKey('accounting.Account', null=True)#created in save method

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

#change 
INVOICE_TYPES = [
    ('cash', 'Cash Invoice'),
    ('credit', 'Credit Based')
    ]

DEFAULT_TAX = 1
DEFAULT_SALES_REP = 1
DEFAULT_CUSTOMER = 1

class AbstractSale(models.Model):
    SALE_STATUS = [
        ('quotation', 'Quotation'),
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid In Full'),
        ('paid-partially', 'Paid Partially'),
        ('reversed', 'Reversed'),
    ]
    status = models.CharField(max_length=16, choices=SALE_STATUS)
    customer = models.ForeignKey("invoicing.Customer", default=DEFAULT_CUSTOMER)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative', 
        default=DEFAULT_SALES_REP)
    active = models.BooleanField(default=True)
    due= models.DateField( default=timezone.now)
    date= models.DateField(default=timezone.now)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    tax = models.ForeignKey('accounting.Tax', blank=True, null=True)
    terms = models.CharField(max_length = 128, blank=True)
    comments = models.TextField(blank=True)
    
    @property
    def overdue(self):
        TODAY = timezone.now().date()
        if self.due < TODAY:
            return (self.due - TODAY).days
        return 0
        
    @staticmethod
    def abstract_filter(filter):
        '''wrap all filters in one Q object and pass it to this function'''
        sales = SalesInvoice.objects.filter(filter)
        service = ServiceInvoice.objects.filter(filter)
        bill = Bill.objects.filter(filter)
        combined = CombinedInvoice.objects.filter(filter)
        invoices = itertools.chain(sales, service, bill, combined)

        return invoices

    def delete(self):
        self.active = False
        self.save()
    
    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def total_paid(self):
        return reduce(lambda x,y: x + y, 
            [p.amount for p in self.payment_set.all()], 0)

    def total_due(self):
        return self.total - self.total_paid

    @property
    def tax_amount(self):
        if self.tax:
            return self.subtotal * D((self.tax.rate / 100.0))
        return 0

    @property
    def subtotal(self):
        raise NotImplementedError()

    def __str__(self):
        return 'SINV' + str(self.pk)

    def save(self, *args, **kwargs):
        super(AbstractSale, self).save(*args, **kwargs)
        config = SalesConfig.objects.first()
        if self.tax is None and config.sales_tax is not None:
            self.tax = config.sales_tax
            self.save() 
        
    

class SalesInvoice(AbstractSale):
    '''used to charge for finished products'''
    DEFAULT_WAREHOUSE = 1 #make fixture
    purchase_order_number = models.CharField(blank=True, max_length=32)
    #add has returns field
    ship_from = models.ForeignKey('inventory.WareHouse',
         default=DEFAULT_WAREHOUSE)

    def add_product(self, product, quantity):
        self.salesinvoiceline_set.create(
            product=product, 
            quantity=quantity,
            price=product.unit_sales_price,
            invoice=self
        )

    @property
    def returned_total(self):
        return reduce(lambda x,y: x + y, 
            [i.returned_total for i in self.creditnote_set.all()], 0)

    @property
    def subtotal(self):
        return reduce(lambda x, y: x+ y, 
            [i.subtotal for i in self.salesinvoiceline_set.all()], 0)

    def update_inventory(self):
        #called in views.py
        for line in self.salesinvoiceline_set.all():
            #check if ship_from has the product in sufficient quantity
             self.ship_from.decrement_product(line.product, line.quantity)

    def create_cash_entry(self):
        j = JournalEntry.objects.create(
                reference='INV' + str(self.pk),
                memo= 'Auto generated Entry from sales invoice.',
                date=self.date,
                journal =Journal.objects.get(pk=1)#Sales Journal
            )
        j.credit(self.total, Account.objects.get(pk=4009))#inventory
        j.debit(self.subtotal, Account.objects.get(pk=4000))#sales
        if self.tax_amount > D(0):
            j.debit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

            return j

    def create_credit_entry(self):
        j = JournalEntry.objects.create(
            reference='INV' + str(self.pk),
            memo= 'Auto generated Entry from sales invoice on credit.',
            date=self.date,
            journal =Journal.objects.get(pk=3)#Sales Journal
        )
            
        j.credit(self.total, Account.objects.get(pk=4009))#inventory
        j.debit(self.total, self.customer.account)#customer account
            
        return j

class SalesInvoiceLine(models.Model):
    invoice = models.ForeignKey('invoicing.SalesInvoice')
    product = models.ForeignKey("inventory.Product")
    quantity = models.FloatField(default=0.0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    returned_quantity = models.FloatField(default=0.0)
    returned = models.BooleanField(default=False)#why???

    @property
    def subtotal(self):
        return D(self.quantity) * self.price

    def _return(self, quantity):
        self.returned_quantity += float(quantity)
        self.returned = True #why???
        self.save()

    @property
    def returned_value(self):
        if self.price == D(0.0):
            return self.product.unit_sales_price * D(self.returned_quantity)
        return self.price * D(self.returned_quantity)

    def save(self, *args, **kwargs):
        super(SalesInvoiceLine, self).save(*args, **kwargs)
        if self.price == 0.0 and self.product.unit_sales_price != D(0.0):
            self.price = self.product.unit_sales_price
            self.save()

    
class ServiceInvoice(AbstractSale):
    '''Used to charge clients for a service'''

    def add_line(self, service_id, hours):
        service = Service.objects.get(pk=service_id)
        self.serviceinvoiceline_set.create(
            service=service,
            hours=hours)

    @property
    def subtotal(self):
        return reduce(lambda x,y: x + y, 
            [i.total for i in self.serviceinvoiceline_set.all() ], 0)

class ServiceInvoiceLine(models.Model):
    invoice = models.ForeignKey('invoicing.ServiceInvoice')
    service = models.ForeignKey('services.Service')
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    
    @property
    def total(self):
        return self.service.flat_fee + (self.service.hourly_rate * self.hours)

class Bill(AbstractSale):
    '''Used to recover billable expenses'''
    customer_reference = models.CharField(max_length=255, blank=True)
    def get_billable_expenses(self):
        return self.customer.expense_set.filter(bill__isnull=True)

    def add_line(self, expense_id):
        expense = Expense.objects.get(pk=expense_id)
        self.billline_set.create(
            expense=expense
        )
    @property
    def subtotal(self):
        return reduce(lambda x, y: x + y, 
            [e.expense.amount for e in self.billline_set.all()], 0)
    
    def create_cash_entry(self):
        j = JournalEntry.objects.create(
                reference='BILL' + str(self.pk),
                memo= 'Auto generated Entry from Bill to customer.',
                date=self.date,
                journal =Journal.objects.get(pk=1)#Sales Journal
            )
            #check these accounts
        j.credit(self.total, Account.objects.get(pk=4009))#inventory
        j.debit(self.subtotal, Account.objects.get(pk=4000))#sales
        if self.tax_amount > D(0):
            j.debit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

            return j

    def create_credit_entry(self):
        j = JournalEntry.objects.create(
            reference='INV' + str(self.pk),
            memo= 'Auto generated Entry from unpaid bill from customer.',
            date=self.date,
            journal =Journal.objects.get(pk=3)#Sales Journal
        )
                #check these accounts
        j.credit(self.total, Account.objects.get(pk=4009))#inventory
        j.debit(self.total, self.customer.account)#customer account
            
        return j
            
class BillLine(models.Model):
    bill = models.ForeignKey('invoicing.Bill')
    expense = models.ForeignKey('accounting.Expense')

class CombinedInvoice(AbstractSale):
    '''Basic Invoice format with description and amount fields 
    that combines the features of sales, services and bills'''
    def add_line(self, data):
        if data['lineType'] == 'sale':
            pk, name = data['data']['product'].split('-')
            product = inventory.models.Product.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=1,#product
                quantity_or_hours= data['data']['quantity'],
                product=product
            )
        
        elif data['lineType'] == 'service':
            pk, name = data['data']['service'].split('-')
            service = Service.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=2,#service
                quantity_or_hours= data['data']['hours'],
                service=service
            )

        elif data['lineType'] == 'billable':
            pk, name = data['data']['billable'].split('-')
            expense = Expense.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=3,#expense
                expense=expense
            )

    @property
    def subtotal(self):
        return reduce(lambda x, y: x + y,
            [i.subtotal for i in self.combinedinvoiceline_set.all()], 0)

class CombinedInvoiceLine(models.Model):
    LINE_CHOICES = [
        (1, 'product'),
        (2, 'service'),
        (3, 'expense'),
    ]
    invoice = models.ForeignKey('invoicing.CombinedInvoice', default=1)
    expense = models.ForeignKey('accounting.Expense', null=True)
    service = models.ForeignKey('services.Service', null=True)
    product = models.ForeignKey("inventory.Product", null=True)
    line_type = models.PositiveSmallIntegerField(choices=LINE_CHOICES)
    quantity_or_hours = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    def __str__(self):
        if self.line_type == 1:
            return '[ITEM] {} x {} @ ${}{}'.format(
                self.quantity_or_hours,
                str(self.product).split('-')[1],
                self.product.unit_sales_price,
                self.product.unit
            )
        elif self.line_type == 2:
            return '[SERVICE] {} Flat fee: ${} + {}Hrs @ ${}/Hr'.format(
                self.service.name,
                self.service.flat_fee,
                self.quantity_or_hours,
                self.service.hourly_rate
            )
        elif self.line_type ==3:
            return '[BILLABE EXPENSE] %s' % self.expense.description

    @property
    def subtotal(self):
        if self.line_type == 1:
            return self.product.unit_sales_price * self.quantity_or_hours
        elif self.line_type == 2:
            return self.service.flat_fee + \
                 (self.service.hourly_rate * self.quantity_or_hours)
        elif self.line_type ==3:
            return self.expense.amount

        return 0


class SalesRepresentative(models.Model):
    '''Really just a dummy class that points to an employee. 
    allows sales and commission to be tracked.
    
    methods
    ---------
    sales - takes two dates as arguments and returns the 
    amount sold exclusive of tax. Used in commission calculation
    '''
    employee = models.OneToOneField('employees.Employee')
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
        invoices = Invoice.objects.filter(Q(salesperson=self) \
            & (Q(due_date__lt=end) \
            | Q(due_date__gte=start)))

        return reduce(lambda x, y: x + y, [i.subtotal for i in invoices], 0)

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
    invoice = models.ForeignKey('invoicing.SalesInvoice')
    comments = models.TextField()

    @property
    def returned_products(self):
        return self.invoice.salesinvoiceline_set.filter(returned=True)
        
    @property
    def returned_total(self):
        return reduce(lambda x, y: x + y, [i.returned_value for i in self.returned_products], 0)

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
    PAYMENT_FOR_CHOICES = [
        (0, 'Sales'),
        (1, 'Service'),
        (2, 'Bill'),
        (3, 'Combined')
    ]
    payment_for = models.PositiveSmallIntegerField(
        choices = PAYMENT_FOR_CHOICES
        )
    #only one of the four is selected
    sales_invoice = models.ForeignKey("invoicing.SalesInvoice", null=True)
    service_invoice = models.ForeignKey("invoicing.ServiceInvoice", null=True)
    bill = models.ForeignKey("invoicing.Bill", null=True)
    combined_invoice = models.ForeignKey("invoicing.CombinedInvoice", null=True)
    amount = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=32, choices=[("cash", "Cash" ),
                                        ("transfer", "Transfer"),
                                        ("debit card", "Debit Card"),
                                        ("ecocash", "EcoCash")],
                                        default='transfer')
    reference_number = models.AutoField(primary_key=True)
    sales_rep = models.ForeignKey("invoicing.SalesRepresentative")
    comments = models.TextField(default="Thank you for your business")

    def __str__(self):
        return 'PMT' + str(self.pk)

    @property
    def due(self):
        return self.invoice.total - self.amount


    def delete(self):
        self.active = False
        self.save()
    
    @property
    def invoice(self):
        options = dict(self.PAYMENT_FOR_CHOICES)
        return options[self.payment_for]

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
            tax_amount = self.amount * D(self.invoice.tax.rate / 100.0)
            # sales account
            j.credit(self.amount - tax_amount, Account.objects.get(pk=4000))
            # tax
            j.credit(tax_amount, Account.objects.get(pk=2001))
            
