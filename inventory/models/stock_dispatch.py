from django.db import models

class DispatchRequest(models.Model):
    type = models.PositiveSmallIntegerField(choices=[
        (0, 'Invoice'),
        (1, 'Transfer'),
        (2, 'Debit Note'),
    ])
    invoice = models.ForeignKey('invoicing.Invoice', 
        null=True, on_delete=models.SET_NULL)
    transfer_order = models.ForeignKey('inventory.TransferOrder', 
        null=True, on_delete=models.SET_NULL)
    debit_note = models.ForeignKey('inventory.DebitNote', null=True,
        on_delete=models.SET_NULL)
    status = models.PositiveSmallIntegerField(choices=[
        (0, 'Request'),
        (1, 'In Progress'),
        (2, 'Completed'),
    ])

class StockDispatch(models.Model):
    '''
    Part of the inventory workflow.
    When an invoice is generated this object is created to record
    the movement of inventory out of the warehouse to fulfill the invoice
    of items and comment on the condition of the 
    products.
    It also is used to send inventory back to a supplier by
    linking with a debit note 
    And is used to initiate transfers from transfer orders

    methods
    ---------
    create_entry - method only called for instances where inventory 
    is paid for on receipt as per order terms.
    '''
    request = models.ForeignKey('inventory.DispatchRequest', 
        on_delete=models.CASCADE)
    dispatched_by = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, 
        null=True,
        default=1)
    dispatch_date = models.DateField()
    note =models.TextField(blank=True, default="")
    dispatch_complete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.receive_date)


class DispatchLine(models.Model):
    dispatch = models.ForeignKey('inventory.StockDispatch'
        ,on_delete=models.CASCADE)
    debit_line = models.ForeignKey('inventory.DebitNoteLine', 
        null=True, on_delete=models.SET_NULL)
    transfer_line = models.ForeignKey('inventory.TransferOrderLine', 
        null=True, on_delete=models.SET_NULL)
    invoice_line  = models.ForeignKey('invoicing.InvoiceLine', 
        null=True, on_delete=models.SET_NULL)
    quantity = models.FloatField(default=0.0)

