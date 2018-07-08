
from django import forms
import models
from accounting.models import Account
from common_data.forms import BootstrapMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import TabHolder, Tab

#models ommitted UnitOfMeasure OrderItem Category
VALUATION_OPTIONS = [
        ('fifo', 'First In First Out'),
        ('lifo', 'Last In First Out'),
        ('averaging', 'Averaging'),
        ('lcm', 'Lower of Cost or Market'),
    ]
class ConfigForm(BootstrapMixin, forms.Form):
    inventory_valuation = forms.ChoiceField(choices=VALUATION_OPTIONS)

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
                    'quantity', 
                    'minimum_order_level',
                    'maximum_stock_level',
                    'supplier'),
                Tab('Pricing', 
                    'unit',
                    'pricing_method',
                    'price',
                    'unit_purchase_price'),
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
                    'unit_sales_price',
                    'unit_purchase_price'),
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
                'type_of_order',
                'deferred_date'),
                Tab('Shipping and Notes', 
                    'bill_to', 
                    'ship_to',
                    'tracking_number',
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
        fields =  ['item_name', 'price', 'pricing_method','unit_purchase_price', 'quantity', 'unit']
        model = models.Item

class CategoryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Category