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
    customer = models.ForeignKey("invoicing.Customer", default=1)
    date_issued = models.DateField( default=timezone.now)
    due_date = models.DateField( default=timezone.now)
    date_paid = models.DateField(default=timezone.now)
    ship_from = models.ForeignKey('inventory.WareHouse')
    terms = models.CharField(max_length = 128, blank=True)
    comments = models.TextField(blank=True)
    number = models.AutoField(primary_key = True)
    tax = models.ForeignKey('accounting.Tax', null=True, blank="True")
    salesperson = models.ForeignKey('invoicing.SalesRepresentative')
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

    def add_item(self, item, quantity, discount):
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
            return self.subtotal * D((self.tax.rate / 100.0))
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
    invoice = models.ForeignKey('invoicing.Invoice')
    item = models.ForeignKey("inventory.Item")
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
        return self.price * D(self.returned_quantity)


