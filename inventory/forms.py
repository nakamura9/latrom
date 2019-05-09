from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Fieldset, 
                                Layout, 
                                Submit, 
                                HTML,
                                Row,
                                Column)
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from accounting.models import Account, Expense, Tax, Asset
from common_data.forms import BootstrapMixin
from employees.models import Employee
from common_data.models import Individual, Organization

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
        exclude = "is_configured",
        model = models.InventorySettings
       
        widgets = {
            'inventory_check_date': forms.Select(choices=[(i, i) for i in range(1, 29)])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Inventory Settings',
                    'inventory_check_date',
                    'inventory_check_frequency',
                    'default_product_sales_pricing_method',
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
    


class SupplierForm(BootstrapMixin, forms.Form):
    vendor_type = forms.ChoiceField(widget=forms.RadioSelect, choices=[
        ('individual', 'Individual'),
        ('organization', 'Organization')
        ], required=True)
    name=forms.CharField()
    address=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':15}), 
                            required=False)
    billing_address=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':15}), 
                            required=False)
    banking_details=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':15}), 
                            required=False)
    email= forms.EmailField(required=False)
    organization=forms.ModelChoiceField(Organization.objects.all(), 
        required=False)
    phone_1=forms.CharField(required=False)
    phone_2=forms.CharField(required=False)
    image=forms.ImageField(required=False)
    website=forms.CharField(required=False)
    business_partner_number=forms.CharField(required=False)

    other_details=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':15}), 
                            required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout= Layout(
            TabHolder(
                Tab('details',
                    Row(
                        Column('vendor_type', css_class='form-group col-3'),
                        Column('name', css_class='form-group col-9'),
                    ),
                    'email',
                    Row(
                        Column('address', css_class='form-group col-6'),
                        Column('banking_details', css_class='form-group col-6'),
                    ),
                    'billing_address'
                ),
                    
                Tab('other',
                    'website',
                    'image',
                    'organization',
                    'other_details',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        
        if cleaned_data['vendor_type'] == "individual":
            if " " not in cleaned_data['name']:
                raise forms.ValidationError('The vendor name must have both a first and last name separated by a space.')

        return cleaned_data

    def save(self):
        cleaned_data = self.clean()
        if cleaned_data['vendor_type'] == "individual":
            names = cleaned_data['name'].split(' ')
            individual = Individual.objects.create(
                first_name=" ".join(names[:-1]),# for those with multiple first names
                last_name=names[-1],
                address=cleaned_data['address'],
                email=cleaned_data['email'],
                phone=cleaned_data['phone_1'],
                phone_two=cleaned_data['phone_2'],
                photo=cleaned_data['image'],
                other_details=cleaned_data['other_details'],
                organization=cleaned_data['organization']
            )
            models.Supplier.objects.create(
                individual=individual,
                billing_address=cleaned_data['billing_address'],
                banking_details=cleaned_data['banking_details']
            )
        else:
            org = Organization.objects.create(
                legal_name=cleaned_data['name'],
                business_address=cleaned_data['address'],
                website=cleaned_data['website'],
                bp_number=cleaned_data['business_partner_number'],
                email=cleaned_data['email'],
                phone=cleaned_data['phone_1'],
                logo=cleaned_data['image']
            )
            models.Supplier.objects.create(
                organization=org,
                billing_address=cleaned_data['billing_address'],
                banking_details=cleaned_data['banking_details']
            )

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
    pricing_method = forms.CharField(widget=forms.NumberInput, required=False)
    margin = forms.CharField(widget=forms.NumberInput, required=False)
    markup = forms.CharField(widget=forms.NumberInput, required=False)
    direct_price = forms.CharField(widget=forms.NumberInput, required=False)
    type=forms.CharField(widget=forms.HiddenInput)
    tax=forms.ModelChoiceField(Tax.objects.all())
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'unit_purchase_price',
                    'description',
                    'type',
                    ),
                Tab('Pricing', 
                    'unit',
                    'tax',
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
                Tab('Image', 'image',
                ),
            )
            )
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        exclude = 'quantity', 'product_component', 'equipment_component'
        model = models.InventoryItem


    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        if instance.product_component:
            component = instance.product_component
            component.pricing_method= self.cleaned_data['pricing_method']
            component.direct_price= self.cleaned_data['direct_price']
            component.margin=self.cleaned_data['margin']
            component.markup=self.cleaned_data['markup']
            component.tax=self.cleaned_data['tax']
            
            instance.product_component.save()

        else:
            component = models.ProductComponent.objects.create(
                pricing_method=self.cleaned_data['pricing_method'],
                direct_price=self.cleaned_data['direct_price'],
                margin=self.cleaned_data['margin'],
                markup=self.cleaned_data['markup'],
                tax=self.cleaned_data['tax']
            )

            instance.product_component = component
    
        instance.save()

        return instance
    

class EquipmentForm(ItemInitialMixin, forms.ModelForm, BootstrapMixin):
    type=forms.CharField(widget=forms.HiddenInput)
    asset_data = forms.ModelChoiceField(Asset.objects.all(), required=False)
    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Description', 
                    'name',
                    'description',
                    'unit_purchase_price',
                    'type'
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
        exclude = "maximum_stock_level", "minimum_order_level", "product_component", "equipment_component", 
        model = models.InventoryItem

    def save(self, **kwargs):
        instance = super().save(**kwargs)

        if instance.equipment_component:
            instance.equipment_component.asset_data = \
                self.cleaned_data['asset_data']
            instance.equipment_component.save()
      
        else:
            instance.equipment_component = \
                models.EquipmentComponent.objects.create(
                    asset_data=self.cleaned_data['asset_data']
                )

        instance.save()
        return instance
        

class ConsumableForm(ItemInitialMixin, forms.ModelForm, BootstrapMixin):
    type=forms.CharField(widget=forms.HiddenInput, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                    'supplier',
                    'type'),
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
        exclude = 'quantity', 'product_component', 'equipment_component',
        model = models.InventoryItem



class OrderForm(forms.ModelForm, BootstrapMixin):
    tax=forms.ModelChoiceField(
        Tax.objects.all(),
        widget=forms.HiddenInput
    )
    make_payment= forms.BooleanField(initial=False, required=False)
    status = forms.CharField(widget=forms.HiddenInput)
    ship_to = forms.ModelChoiceField(models.WareHouse.objects.all(), label='Ship To Warehouse')


    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic',
                Row(
                    Column('date', css_class='form group col-6'),
                    Column('expected_receipt_date', css_class='form group col-6'),
                ),
                Row(
                    Column('supplier', css_class='form group col-6'),
                    Column('ship_to', css_class='form group col-6'),
                ),
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
            HTML(
                """
                <div id="order-root"></div>
                """
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
        exclude = ["entry", "received_to_date", "shipping_cost_entries"]
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
        widgets = {
            'note': forms.Textarea(attrs={
                'rows': 5
            })
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
            Column('received_by', 
                    'receive_date',
                    'order',
                    'warehouse',
                    css_class="col-sm-6"),
            Column('note', css_class="col-sm-6")
            )
        )

        self.helper.add_input(Submit('submit', 'Submit'))



class UnitForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'eval_string'
        model = models. UnitOfMeasure



class CategoryForm(forms.ModelForm, BootstrapMixin):
    parent = forms.ModelChoiceField(models.Category.objects.all(), widget=forms.HiddenInput, required=False)
    class Meta:
        fields = "__all__"
        model = models.Category
        
class WareHouseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = '__all__'
        model = models.WareHouse

        widgets = {
                'address':forms.Textarea(attrs={'rows':4, 'cols':15}), 
                'description':forms.Textarea(attrs={'rows':4, 'cols':15}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'address',
            'description',
            'inventory_controller',
            Row(
                Column('length', css_class='form group col-4'),
                Column('width', css_class='form group col-4'),
                Column('height', css_class='form group col-4'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class InventoryCheckForm(forms.ModelForm, BootstrapMixin):
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), widget=forms.HiddenInput)
    class Meta:
        fields = "__all__"
        model = models.InventoryCheck
        widgets = {
            'comments': forms.Textarea(attrs={
                'rows': 5
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
            Column('date', 
                    'adjusted_by',
                    'warehouse',
                    css_class="col-sm-6"),
            Column('comments', css_class="col-sm-6")
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class TransferOrderForm(forms.ModelForm, BootstrapMixin):
    source_warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(),
        widget=forms.HiddenInput)
    items = forms.CharField(widget=forms.HiddenInput)
    order_issuing_notes = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 8}))
    class Meta:
        exclude = ['actual_completion_date', 'receiving_inventory_controller','receive_notes', 'completed']
        model = models.TransferOrder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
            Column(
                    Row(
                        Column('date', css_class="col-sm-6"),
                        Column('expected_completion_date',css_class="col-sm-6"),
                    ),
                    'issuing_inventory_controller',
                    'receiving_warehouse',
                    'source_warehouse',
                    'items',
                    css_class="col-sm-6"),
            Column('order_issuing_notes', css_class="col-sm-6")
            )
        )

        self.helper.add_input(Submit('submit', 'Submit'))


class TransferReceiptForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ['actual_completion_date', 'receive_notes', 'receiving_inventory_controller']
        model = models.TransferOrder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
            Column('actual_completion_date', 
                    'receiving_inventory_controller', 
                    css_class="col-sm-6"),
            Column('receive_notes', css_class="col-sm-6")
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class InventoryControllerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.InventoryController

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


class InventoryControllerUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "employee",
        model = models.InventoryController

class ScrappingRecordForm(forms.ModelForm, BootstrapMixin):
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), 
        widget=forms.HiddenInput)
    items = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = "__all__"
        model = models.InventoryScrappingRecord
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 5})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
            Column('date', 
                    'controller',
                    'items',
                    'warehouse',
                    css_class="col-sm-6"),
            Column('comments', css_class="col-sm-6")
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class StorageMediaForm(forms.ModelForm, BootstrapMixin):
    location = forms.ModelChoiceField(models.StorageMedia.objects.all(), widget=forms.HiddenInput, required=False)
    warehouse = forms.ModelChoiceField(models.WareHouse.objects.all(), widget=forms.HiddenInput)
    class Meta:
        fields = "__all__"
        model = models.StorageMedia

        widgets = {
                'description':forms.Textarea(attrs={'rows':4, 'cols':15}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic',
                    'name',
                    Row(
                        Column('length', css_class="form group col-4"),
                        Column('width', css_class="form group col-4"),
                        Column('height', css_class="form group col-4"),
                    ),
                    'capacity',
                ),
                Tab('description',
                    'description',
                    'unit',
                    'warehouse',
                    'location',
                ),
                Tab('Parent Storage Medium',
                    HTML(
                        """
                        <div id="storage-media-select-widget"></div>                        
                        """
                    ),
                ),
            ),
        )        
        self.helper.add_input(Submit('submit', 'Submit'))
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



class DebitNoteForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.DebitNote

    order = forms.ModelChoiceField(models.Order.objects.all(),
        widget=forms.HiddenInput)
