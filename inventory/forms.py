
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, HTML
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from accounting.models import Account, Expense, Tax
from common_data.forms import BootstrapMixin
from employees.models import Employee

from . import models

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Inventory Settings',
                    'inventory_check_date',
                    'inventory_check_frequency',
                    'order_template_theme',
                    'product_sales_pricing_method',
                    'inventory_valuation_method',
                    ),
                Tab('WareHousing Settings',
                    'use_warehousing_model',
                    'use_storage_media_model'),
                Tab('Inventory Types',
                    'use_product_inventory',
                    'use_equipment_inventory',
                    'use_consumables_inventory',
                    'use_raw_materials_inventory')
            )
        )
        
        self.helper.add_input(Submit('submit', 'Submit'))
    


class IndividualSupplierForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account', 'organization']
        model = models.Supplier

class OrganizationSupplierForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account', 'individual']
        model = models.Supplier


class SupplierUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account']
        model = models.Supplier

class ItemInitialMixin(forms.Form):
    initial_quantity = forms.CharField(widget=forms.NumberInput, initial=0)
    warehouse = forms.ModelChoiceField(
        models.WareHouse.objects.all(), required=False)

    def save(self):
        obj = super().save()
        if float(self.cleaned_data['initial_quantity']) > 0 and \
            self.cleaned_data['warehouse'] is not None:
            wh = self.cleaned_data['warehouse']
            wh.add_item(self.instance, self.cleaned_data['initial_quantity'])
        
        return obj

class ProductForm(ItemInitialMixin, forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'unit_purchase_price',
                    'description',
                    ),
                Tab('Pricing', 
                    'unit',
                    HTML("<div id='pricing-widget'></div>")
                    ),
                Tab('Stocking Information',
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Categories', 
                    'category'),
                Tab('Dimensions', 
                    'length', 
                    'width',
                    'height'),
                Tab('Initial Inventory', 
                    'initial_quantity', 
                    'warehouse',
                    ),
                Tab('Image', 'image'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        exclude = 'quantity',
        model = models.Product

    

class EquipmentForm(ItemInitialMixin, forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'description',
                    'condition',
                    'unit_purchase_price',
                    ),
                Tab('Ordering Information',
                    'supplier'),
                Tab('Purchase Information', 
                    'unit',
                    'asset_data'),
                Tab('Categories', 
                    'category'),
                Tab('Dimensions', 
                    'length', 
                    'width',
                    'height'),
                Tab('Initial Inventory', 
                    'initial_quantity', 
                    'warehouse',
                    ),
                Tab('Image', 'image'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        fields = "__all__"
        model = models.Equipment

class ConsumableForm(ItemInitialMixin, forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        super(ConsumableForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'description',
                    'unit_purchase_price',),
                Tab('Ordering Information',
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Purchase Information', 
                    'unit',
                    ),
                Tab('Categories', 
                    'category'),
                Tab('Dimensions', 
                    'length', 
                    'width',
                    'height'),
                Tab('Initial Inventory', 
                    'initial_quantity', 
                    'warehouse',
                    ),
                Tab('Image', 'image'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        exclude = 'quantity',
        model = models.Consumable

class ProductUpdateForm(forms.ModelForm, BootstrapMixin):
    '''identical to the other form except for not allowing quantity to be changed'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'unit_purchase_price',
                    'description',
                    ),
                Tab('Pricing', 
                    'unit',
                    HTML("<div id='pricing-widget'></div>")
                ),
                Tab('Stock Info',
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Dimensions', 
                    'length', 
                    'width',
                    'height'),
                Tab('Categories', 
                    'category'),
                Tab('Image', 'image'),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))
    
    class Meta:
        fields = '__all__'
        model = models.Product

class OrderForm(forms.ModelForm, BootstrapMixin):
    tax=forms.ModelChoiceField(
        Tax.objects.all(),
        widget=forms.HiddenInput
    )
    make_payment= forms.BooleanField(initial=False, required=False)
    status = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic',
                    'date',
                    'expected_receipt_date',
                    'supplier',
                    'ship_to',
                    'issuing_inventory_controller'
                    ),
                Tab('Payment',
                        'tax',
                        'make_payment',
                        'due'
                    ),
                Tab('Shipping and Notes', 
                    'bill_to', 
                    'tracking_number',
                    'supplier_invoice_number',
                    'notes'),
            ),
            HTML("""
                <div class="dropdown open">
                        <button class="btn btn-info dropdown-toggle" type="button" id="triggerId" data-toggle="dropdown" >
                                    Submit as...
                                </button>
                        <div class="dropdown-menu" aria-labelledby="triggerId">
                            <input class="dropdown-item" 
                                type="submit"
                                name="status"
                                value="draft">
                            <input class="dropdown-item" 
                                type="submit"
                                name="status"
                                value="order">                           
                        </div>
            """)
            )
    class Meta:
        exclude = ["entry", "received_to_date",]
        model = models.Order
        

class OrderUpdateForm(forms.ModelForm, BootstrapMixin):
    tax=forms.ModelChoiceField(
        Tax.objects.all(),
        widget=forms.HiddenInput
    )
    class Meta:
        model = models.Order
        fields = ['date', 'expected_receipt_date', 
             'due', 'supplier', 'bill_to',
            'notes', 'tax']
        

class OrderPaymentForm(forms.ModelForm, BootstrapMixin):
    order = forms.ModelChoiceField(
        models.Order.objects.all(), widget=forms.HiddenInput)
    class Meta:
        exclude = "entry",
        model = models.OrderPayment
        
class StockReceiptForm(forms.ModelForm, BootstrapMixin):
    order = forms.ModelChoiceField(models.Order.objects.all(),     
        widget=forms.HiddenInput)
    warehouse = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = 'fully_received',
        model= models.StockReceipt


class UnitForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active",
        model = models. UnitOfMeasure


class QuickProductForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields =  ['name', 'direct_price', 'pricing_method','unit_purchase_price', 'unit']
        model = models.Product

class CategoryForm(forms.ModelForm, BootstrapMixin):
    parent = forms.ModelChoiceField(models.Category.objects.all(), widget=forms.HiddenInput, required=False)
    class Meta:
        fields = "__all__"
        model = models.Category
        
class WareHouseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = '__all__'
        model = models.WareHouse

class InventoryCheckForm(forms.ModelForm, BootstrapMixin):
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), widget=forms.HiddenInput)
    class Meta:
        fields = "__all__"
        model = models.InventoryCheck

class TransferOrderForm(forms.ModelForm, BootstrapMixin):
    source_warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(),
        widget=forms.HiddenInput)
    class Meta:
        exclude = ['actual_completion_date', 'receiving_inventory_controller','receive_notes', 'completed']
        model = models.TransferOrder


class TransferReceiptForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ['actual_completion_date', 'receive_notes', 'receiving_inventory_controller']
        model = models.TransferOrder


class InventoryControllerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.InventoryController


class InventoryControllerUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "employee",
        model = models.InventoryController

class ScrappingRecordForm(forms.ModelForm, BootstrapMixin):
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), 
        widget=forms.HiddenInput)
    class Meta:
        fields = "__all__"
        model = models.InventoryScrappingRecord

class StorageMediaForm(forms.ModelForm, BootstrapMixin):
    location = forms.ModelChoiceField(models.StorageMedia.objects.all(), widget=forms.HiddenInput, required=False)
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), widget=forms.HiddenInput)
    class Meta:
        fields = "__all__"
        model = models.StorageMedia


class AutoStorageMedia(BootstrapMixin, forms.Form):
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), widget=forms.HiddenInput)
    number_of_corridors = forms.CharField(widget=forms.NumberInput)
    number_of_aisles_per_corridor = forms.CharField(widget=forms.NumberInput)
    number_of_shelves_per_aisle = forms.CharField(widget=forms.NumberInput)

class ShippingAndHandlingForm(BootstrapMixin, forms.Form):
    #using current account 
    #debiting cost of sales account 
    amount = forms.CharField(widget=forms.NumberInput)
    date = forms.DateField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    recorded_by = forms.ModelChoiceField(User.objects.all())
    reference = forms.CharField(widget=forms.HiddenInput)


class RawMaterialForm(ItemInitialMixin, forms.ModelForm, BootstrapMixin):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'description'),
                Tab('Stocking Information',
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Pricing', 
                    'unit',
                    'unit_purchase_price'),
                Tab('Categories', 
                    'category'),
                Tab('Dimensions', 
                    'length', 
                    'width',
                    'height'),
                Tab('Image', 'image'),
                Tab('Initial Inventory', 
                    'initial_quantity', 
                    'warehouse',
                    )
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        exclude =  'active',
        model = models.RawMaterial


class DebitNoteForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.DebitNote

    order = forms.ModelChoiceField(models.Order.objects.all(),
        widget=forms.HiddenInput)

