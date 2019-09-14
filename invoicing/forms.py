
from crispy_forms.bootstrap import Tab, TabHolder, InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (HTML, 
                                Fieldset, 
                                Layout,
                                Row,
                                Column, 
                                Div,
                                Submit)

from django import forms
from django.forms.widgets import HiddenInput, MultipleHiddenInput

from accounting.models import Account, Journal,Tax
from common_data.forms import BootstrapMixin, PeriodReportForm
from common_data.models import Organization, Individual
from . import models
from django.forms import ValidationError
from django_select2.forms import Select2Widget

class SalesConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.SalesConfig
        exclude = "is_configured",

        widgets = {
            'default_invoice_comments':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'default_credit_note_comments':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'default_quotation_comments':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'default_terms':forms.Textarea(attrs={'rows':4, 'cols':15}),            
        }

    def __init__(self, *args, **kwargs):
        super(SalesConfigForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
            Tab('Document Fields', 
                'default_invoice_comments',
                'default_credit_note_comments',
                'default_quotation_comments',
                'default_terms',
                ),
            Tab('Page Layout',
                'sales_tax',
                'include_tax_in_invoice',
                'next_invoice_number',
                'next_quotation_number',
                'include_units_in_sales_invoice',
                'include_shipping_address',
                )
        ))

        self.helper.add_input(Submit('submit', "Submit"))
        
class CustomerForm(BootstrapMixin, forms.Form):
    customer_type = forms.ChoiceField(widget=forms.RadioSelect, choices=[
        ('individual', 'Individual'),
        ('organization', 'Organization')
        ])
    name=forms.CharField()
    address=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':10}),
                            required=False)
    billing_address=forms.CharField(widget=forms.Textarea, 
                            required=False)
    banking_details=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':10}),
                            required=False)
    email= forms.EmailField(required=False)
    organization=forms.ModelChoiceField(Organization.objects.all(), 
        required=False)
    phone_1=forms.CharField(required=False)
    phone_2=forms.CharField(required=False)
    image=forms.ImageField(required=False)
    website=forms.CharField(required=False)
    business_partner_number=forms.CharField(required=False)

    other_details=forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout= Layout(
            TabHolder(
                Tab('details',
                Row(
                        Column('customer_type', css_class='form-group col-3'),
                        Column('name', css_class='form-group col-9'),
                    ),
                    Row(
                        Column('address', css_class='form-group col-6'),
                        Column('banking_details', css_class='form-group col-6'),
                    ),
                    Row(
                        Column(
                            'phone_1',
                            'phone_2',
                            'email', css_class='form group col-6'
                        ),
                        Column('billing_address', css_class='form group col-6')
                    ),                    
                ),
                Tab('other',
                    'website',
                    'image',
                    'other_details',
                    'organization'
                ),
            ),
            Div(Submit('submit', 'Submit'), css_class="floating-submit")
        )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        if cleaned_data['customer_type'] == "individual":
            if " " not in cleaned_data['name']:
                raise ValidationError('The customer name must have both a first and last name separated by a space.')

        return cleaned_data

    def save(self):
        cleaned_data = self.clean()
        if cleaned_data['customer_type'] == "individual":
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
            models.Customer.objects.create(
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
            models.Customer.objects.create(
                organization=org,
                billing_address=cleaned_data['billing_address'],
                banking_details=cleaned_data['banking_details']
            )


class SalesRepForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'active',
        model = models.SalesRepresentative

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

class InvoiceCreateMixin(forms.Form):
    apply_payment = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['status'] != 'invoice' and \
                cleaned_data['apply_payment']:
            raise forms.ValidationError('Save the document as invoice if you want to apply a payment')

        return cleaned_data


class CreditNoteForm( forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(models.Invoice.objects.all(), widget=forms.HiddenInput)
    class Meta:
        exclude = 'entry',
        model = models.CreditNote

#######################################################
#               Report Forms                          #
#######################################################
# report types
# customer statement
# invoice aging report
# invoice summary
# past due invoices
# outstanding invoices
# payment summary
# sales by item 

class CustomerStatementReportForm(PeriodReportForm):
    customer = forms.ModelChoiceField(models.Customer.objects.all(), widget=Select2Widget)

class SalesReportForm(PeriodReportForm):
    '''method = forms.ChoiceField(widget=forms.RadioSelect, choices=[("invoice", "Invoice Count"), ("amount", "Sales Value")])'''
    pass


class InvoiceForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        fields = ["status", 'customer', 'purchase_order_number', 'ship_from', 'date', 'due', 'salesperson', 'terms', 'comments', 'invoice_number']
        model = models.Invoice
        widgets = {
            'customer': Select2Widget
        }

class InvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = ["status", 'customer', 'purchase_order_number', 'ship_from', 'date', 'due', 'salesperson',  'terms', 'comments', 'invoice_number']
        model = models.Invoice
        widgets = {
            'customer': Select2Widget
        }

class QuotationForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    quotation_date = forms.DateField(required=True)
    quotation_valid = forms.DateField(required=True)

    class Meta:
        fields = ["status", 'customer', 'quotation_date', 'quotation_valid', 'salesperson', 'terms', 'comments']
        model = models.Invoice
        widgets = {
            'customer': Select2Widget
        }

class InvoicePaymentForm(forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(
        models.Invoice.objects.all(), widget=forms.HiddenInput
        )
    
    class Meta:
        exclude = [ 'active', 'entry']
        model = models.Payment

class CreateMultipleCustomersForm(forms.Form):
    data = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'data',
            HTML("""<div id='multiple-customers-list'></div>""")
        )
        self.helper.add_input(Submit('submit', 'Submit'))



class ImportCustomersForm(forms.Form):
    file = forms.FileField()
    sheet_name = forms.CharField()
    name = forms.IntegerField()
    type = forms.IntegerField()
    address = forms.IntegerField()
    email = forms.IntegerField()
    phone = forms.IntegerField()
    account_balance = forms.IntegerField()
    start_row = forms.IntegerField()
    end_row = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>File</h4>'),
            Row(
                Column('file', css_class='col-6'),
                Column('sheet_name', css_class='col-6'),
            ),
            HTML("""
            <h4>Columns</h4>
            <p>State the columns that correspond to the required data tp describe a customer .Convert alphabetic columns to numbers and insert below e.g. A=1, D=4 etc.</p>
            <ul>
                <li>Name - Legal name of the customer</li>
                <li>Address - Customer's Physical address that appears on bills</li>
                <li>Type - One of Individual or Organization</li>
                <li>Email</li>
                <li>Phone</li>
                <li>Account Balance - current balance with customer</li>
                
            </ul>"""),
            Row(
                Column('name', css_class='col-2'),
                Column('address', css_class='col-2'),
                Column('type', css_class='col-2'),
                Column('email', css_class='col-2'),
                Column('phone', css_class='col-2'),
                Column('account_balance', css_class='col-2'),
            ),
            HTML("""
            <h4>Rows:</h4>
            <p>State the rows the list starts and ends in, both are inclusive.</p>"""),
            Row(
                Column('start_row', css_class='col-6'),
                Column('end_row', css_class='col-6'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class ImportInvoiceForm(BootstrapMixin,forms.Form):
    file = forms.FileField()
    sheet_name = forms.CharField()
    date = forms.CharField(
        widget=forms.DateInput(
            attrs={'class':'ui-date-picker'}))
    due = forms.CharField(
        widget=forms.DateInput(
            attrs={'class':'ui-date-picker'}))
    customer = forms.ModelChoiceField(
        models.Customer.objects.all(),
        widget=Select2Widget
        )
    salesperson = forms.ModelChoiceField(
        models.SalesRepresentative.objects.all(),
        widget=Select2Widget
        )
    sales_tax = forms.ModelChoiceField(
        Tax.objects.all()
        )
    invoice_number = forms.IntegerField()
    
    description = forms.IntegerField()
    unit = forms.IntegerField()
    quantity = forms.IntegerField()
    unit_price = forms.IntegerField()
    subtotal = forms.IntegerField()
    
    start_row = forms.IntegerField()
    end_row = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>File</h4>'),
            Row(
                Column('file', css_class='col-6'),
                Column('sheet_name', css_class='col-6'),
            ),
            HTML('<h4>Invoice</h4>'),
            Row(
                Column('date', 'due', 'invoice_number',css_class='col-6'),
                Column('customer', 'salesperson', 'sales_tax',css_class='col-6'),
            ),
            
            HTML("""
            <h4>Columns</h4>
            <p>State the columns that correspond to the required data tp describe a customer .Convert alphabetic columns to numbers and insert below e.g. A=1, D=4 etc.</p>
            <ul>
                <li>Description - Name of product or service. Mark services with a '*' in the description cell. E.g. 'Bearing change' becomes '*Bearing change'.</li>
                <li>Unit - Unit of measure as it appears on invoice</li>
                <li>Quantity - One of Individual or Organization</li>
                <li>Unit Price - Price per item</li>
                <li>Subtotal - Total for the invoice line</li>
                
            </ul>"""),
            Row(
                Column('description', css_class='col-4'),
                Column('unit', css_class='col-2'),
                Column('quantity', css_class='col-2'),
                Column('unit_price', css_class='col-2'),
                Column('subtotal', css_class='col-2'),
            ),
            HTML("""
            <h4>Rows:</h4>
            <p>State the rows the list starts and ends in, both are inclusive.</p>"""),
            Row(
                Column('start_row', css_class='col-6'),
                Column('end_row', css_class='col-6'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit'))
