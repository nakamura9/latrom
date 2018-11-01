
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django import forms
from django.forms.widgets import HiddenInput, MultipleHiddenInput

from accounting.models import Account, Journal
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
                'include_units_in_sales_invoice',
                'include_shipping_address',
                'document_theme',
                ),
            Tab('Financial Data Presentation',
                'currency',
                'apply_price_multiplier',
                'price_multiplier',
                ),
            Tab('Business Information',
                'logo',
                'business_address',
                'business_name',
                'business_registration_number',
                'payment_details',
                'contact_details')
        ))
class CustomerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account']
        model = models.Customer

class SalesRepForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'active',
        model = models.SalesRepresentative


class SalesInvoiceForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number'
        model = models.SalesInvoice


class SalesInvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['customer', 'active', 'discount', 'invoice_number', 'quotation_number'] 
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

class ServiceInvoiceForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'invoice_number', 'quotation_number', 'discount'
        model = models.ServiceInvoice

class ServiceInvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number'
        model = models.ServiceInvoice

class BillForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number'
        model = models.Bill

class BillUpdateForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    customer = forms.ModelChoiceField(models.Customer.objects.all(), widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number'
        model = models.Bill

class BillPaymentForm(forms.ModelForm, BootstrapMixin):
    bill = forms.ModelChoiceField(
        models.Bill.objects.all(), widget=forms.HiddenInput
        )
    payment_for = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = ['sales_invoice', 'service_invoice', 'combined_invoice']
        model = models.Payment

class CombinedInvoiceForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = "active", 'invoice_number', 'quotation_number', 'discount'
        model = models.CombinedInvoice

class CombinedInvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'discount', 'invoice_number', 'quotation_number'
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
