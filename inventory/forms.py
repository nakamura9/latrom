
from django import forms
import models
from accounting.models import Account
from common_data.forms import BootstrapMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import TabHolder, Tab
from django.contrib.auth import authenticate
from employees.models import Employee

#models ommitted UnitOfMeasure OrderItem Category
VALUATION_OPTIONS = [
        ('fifo', 'First In First Out'),
        ('lifo', 'Last In First Out'),
        ('averaging', 'Averaging'),
        ('lcm', 'Lower of Cost or Market'),
    ]
class ConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.InventorySettings


class SupplierForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account']
        model = models.Supplier
        
class ItemForm(forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'item_name',
                    'description',),
                Tab('Stock Info',
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Pricing', 
                    'unit',
                    'unit_purchase_price',
                    'pricing_method',
                    'markup',
                    'margin',
                    'direct_price'),
                Tab('Categories', 
                    'category', 
                    'sub_category'),
                Tab('Image', 'image'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        exclude = 'quantity',
        model = models.Item

        
class ItemUpdateForm(forms.ModelForm, BootstrapMixin):
    '''identical to the other form except for not allowing quantity to be changed'''
    def __init__(self, *args, **kwargs):
        super(ItemUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'item_name',
                    'description',),
                Tab('Stock Info', 
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Pricing', 
                    'unit',
                    'unit_purchase_price',
                    'pricing_method',
                    'markup',
                    'margin',
                    'direct_price'),
                Tab('Categories', 
                    'category', 
                    'sub_category'),
                Tab('Image', 'image'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))
    
    class Meta:
        fields = '__all__'
        model = models.Item

class OrderForm(forms.ModelForm, BootstrapMixin): 
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic', 
                    'issue_date',
                    'expected_receipt_date',
                    'supplier',
                    'status'
                    ),
                Tab('Payment',
                'tax',
                'type_of_order',
                'deferred_date'),
                Tab('Shipping and Notes', 
                    'bill_to', 
                    'ship_to',
                    'tracking_number',
                    'supplier_invoice_number',

                    'notes'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))
    class Meta:
        exclude = ["items", "received_to_date"]
        model = models.Order
        
        
class StockReceiptForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'fully_received',
        model= models.StockReceipt


class UnitForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models. UnitOfMeasure


class QuickItemForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields =  ['item_name', 'direct_price', 'pricing_method','unit_purchase_price', 'unit']
        model = models.Item

class CategoryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Category
        
class WareHouseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = '__all__'
        model = models.WareHouse

class InventoryCheckForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.InventoryCheck

class TransferOrderForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['actual_completion_date', 'receive_notes', 'completed']
        model = models.TransferOrder


class TransferReceiptForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ['actual_completion_date', 'receive_notes', 'receiving_inventory_controller']
        model = models.TransferOrder


class InventoryControllerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.InventoryController