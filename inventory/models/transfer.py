from django.db import models 
import inventory
from django.shortcuts import reverse
class TransferOrder(models.Model):
    date = models.DateField()
    expected_completion_date = models.DateField()
    issuing_inventory_controller = models.ForeignKey('inventory.InventoryController',
        related_name='issuing_inventory_controller', 
        on_delete=models.SET_NULL, null=True)
    receiving_inventory_controller = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, null=True)
    source_warehouse = models.ForeignKey('inventory.WareHouse',
        related_name='source_warehouse', on_delete=models.SET_NULL, null=True,)
    receiving_warehouse = models.ForeignKey('inventory.WareHouse', 
        on_delete=models.SET_NULL, null=True,)
    order_issuing_notes = models.TextField(blank=True)
    
    @property
    def completed(self):
        lines = TransferOrderLine.objects.filter(transfer_order=self)
        completed = True
        for line in lines:
            if not line.completed:
                completed = False

        return completed 

    def get_absolute_url(self):
        return reverse('inventory:transfer-order-detail', kwargs={
            'pk': self.pk
        })

    @property
    def completed_date(self):
        if self.completed:
            receipts = \
                inventory.models.stock_receipt.StockReceipt.objects.filter(
                    transfer=self)

            if receipts.count() > 0:
                return receipts.latest('pk').receive_date
        
        return None


class TransferOrderLine(models.Model):
    item = models.ForeignKey('inventory.inventoryitem', 
        on_delete=models.SET_NULL, 
        null=True)
    quantity = models.FloatField()
    transfer_order = models.ForeignKey('inventory.TransferOrder', 
        on_delete=models.SET_NULL, null=True)
    
    @property
    def moved_quantity(self):
        return sum([
            i.quantity for i in \
                inventory.models.stock_dispatch.DispatchLine.objects.filter(
                    transfer_line=self)])

    @property
    def received_quantity(self):
        return sum([
            i.quantity for i in \
                inventory.models.stock_receipt.StockReceiptLine.objects.filter(
                    transfer_line=self)], 0)

    def move(self, quantity, location=None):
        '''performs the actual transfer of the item between warehouses'''
        self.transfer_order.source_warehouse.decrement_item(
            self.item, quantity)
        self.transfer_order.receiving_warehouse.add_item(
            self.item, quantity, location=location)
        self.moved=quantity
        self.save()
        self.transfer_order.update_completed_status()

    @property
    def completed(self):
        return self.received_quantity >= self.quantity
