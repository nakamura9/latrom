
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django import forms
from django.forms.widgets import HiddenInput, MultipleHiddenInput

from accounting.models import Account, Journal,Tax
from common_data.forms import BootstrapMixin, PeriodReportForm

from . import models


class SalesConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.SalesConfig
        fields = "__all__"

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
                'document_theme',
                ),
            Tab('Financial Data Presentation',
                'currency',
                ),
            Tab('Invoice Types',
                'use_sales_invoice',
                'use_combined_invoice',
                'use_bill_invoice',
                'use_service_invoice',
                ),
            Tab('Business Information',
                'logo',
                'business_address',
                'business_name',
                'business_registration_number',
                'payment_details',
                'contact_details')
        ))

        
class OrganizationCustomerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account', 'individual']
        model = models.Customer

class IndividualCustomerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account', 'organization']
        model = models.Customer
        
class CustomerUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account', 'individual', 'organization']
        model = models.Customer

class SalesRepForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'active',
        model = models.SalesRepresentative

class InvoiceCreateMixin(forms.Form):
    apply_payment = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['status'] != 'invoice' and \
                cleaned_data['apply_payment']:
            raise forms.ValidationError('Save the document as invoice if you want to apply a payment')

        return cleaned_data

class SalesInvoiceForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    tax=forms.ModelChoiceField(Tax.objects.all(), widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number', 'entry'
        model = models.SalesInvoice

    

class SalesInvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['customer', 'active', 'discount', 'invoice_number', 'quotation_number', 'status', 'entry'] 
        model = models.SalesInvoice

class SalesInvoicePaymentForm(forms.ModelForm, BootstrapMixin):
    sales_invoice = forms.ModelChoiceField(
        models.SalesInvoice.objects.all(), widget=forms.HiddenInput
        )
    
    payment_for = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = ['service_invoice', 'bill', 'combined_invoice']
        model = models.Payment


class ServiceInvoicePaymentForm(forms.ModelForm, BootstrapMixin):
    service_invoice = forms.ModelChoiceField(
        models.ServiceInvoice.objects.all(), widget=forms.HiddenInput
        )
    
    
    payment_for = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = ['sales_invoice', 'bill', 'combined_invoice']
        model = models.Payment

class ServiceInvoiceForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    apply_payment = forms.BooleanField(required=False)
    tax=forms.ModelChoiceField(Tax.objects.all(), widget=forms.HiddenInput)

    class Meta:
        exclude = "active", 'invoice_number', 'quotation_number', 'discount', 'entry'
        model = models.ServiceInvoice

class ServiceInvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number', 'status', 'entry'
        model = models.ServiceInvoice

class BillForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    apply_payment = forms.BooleanField(required=False)

    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number', 'entry'
        model = models.Bill

class BillUpdateForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    customer = forms.ModelChoiceField(models.Customer.objects.all(), widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number', 'status', 'entry'
        model = models.Bill

class BillPaymentForm(forms.ModelForm, BootstrapMixin):
    bill = forms.ModelChoiceField(
        models.Bill.objects.all(), widget=forms.HiddenInput
        )
    payment_for = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = ['sales_invoice', 'service_invoice', 'combined_invoice']
        model = models.Payment

class CombinedInvoiceForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    apply_payment = forms.BooleanField(required=False)

    class Meta:
        exclude = "active", 'invoice_number', 'quotation_number', 'discount', 'entry'
        model = models.CombinedInvoice

class CombinedInvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number', 'status', 'entry'
        model = models.CombinedInvoice

class CombinedInvoicePaymentForm(forms.ModelForm, BootstrapMixin):
    combined_invoice = forms.ModelChoiceField(
        models.CombinedInvoice.objects.all(), widget=forms.HiddenInput
        )
    
    payment_for = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = ['service_invoice', 'bill', 'sales_invoice']
        model = models.Payment


class CreditNoteForm( forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(models.SalesInvoice.objects.all(), widget=forms.HiddenInput)
    class Meta:
        fields = '__all__'
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
    customer = forms.ModelChoiceField(models.Customer.objects.all())

class SalesReportForm(PeriodReportForm):
    '''method = forms.ChoiceField(widget=forms.RadioSelect, choices=[("invoice", "Invoice Count"), ("amount", "Sales Value")])'''
    pass