from django.db import models
from django.shortcuts import reverse 

class StockReceipt(models.Model):
    '''
    Part of the inventory ordering workflow.
    When an order is generated this object is created to verify 
    the receipt of items and comment on the condition of the 
    products.
    It also is used to receive inventory returned from customers by
    linking with a credit note 
    And is used to receive transfers from transfer orders

    methods
    ---------
    create_entry - method only called for instances where inventory 
    is paid for on receipt as per order terms.
    '''
    order = models.ForeignKey('inventory.Order', on_delete=models.SET_NULL, 
        null=True)
    credit_note = models.ForeignKey('invoicing.CreditNote', 
        on_delete=models.SET_NULL, 
        null=True)
    transfer = models.ForeignKey('inventory.TransferORder', 
        on_delete=models.SET_NULL, 
        null=True)
    received_by = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, 
        null=True,
        default=1)
    receive_date = models.DateField()
    note =models.TextField(blank=True, default="")
    fully_received = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.receive_date)

    def get_absolute_url(self):
        return reverse("inventory:goods-received", kwargs={"pk": self.pk})
    



class StockReceiptLine(models.Model):
    receipt = models.ForeignKey('inventory.StockReceipt'
        ,on_delete=models.CASCADE)
    order_line = models.ForeignKey('inventory.OrderItem', 
        null=True, on_delete=models.SET_NULL)
    transfer_line = models.ForeignKey('inventory.TransferOrderLine', 
        null=True, on_delete=models.SET_NULL)
    credit_note_line  = models.ForeignKey('invoicing.CreditNoteLine', 
        null=True, on_delete=models.SET_NULL)
    quantity = models.FloatField(default=0.0)
    location = models.ForeignKey('inventory.storagemedia', null=True, 
        blank=True, on_delete=models.SET_NULL)


    @property
    def line(self):
        if self.order_line:
            return self.order_line.item
        elif self.transfer_line:
            return self.transfer_line.item

        elif self.credit_note_line:
            return self.credit_note_line.line.product.product

        else:
            raise Exception('No line has been specified.')

    @property
    def expected_quantity(self):
        if self.order_line:
            return self.order_line.quantity
        elif self.transfer_line:
            return self.transfer_line.quantity
        else:
            return self.credit_note_line.quantity