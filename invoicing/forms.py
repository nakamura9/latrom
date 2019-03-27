
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (HTML, 
                                Fieldset, 
                                Layout, 
                                Submit)
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
                ),
            Tab('Invoice Types',
                'use_sales_invoice',
                'use_combined_invoice',
                'use_bill_invoice',
                'use_service_invoice',
                )
        ))

        self.helper.add_input(Submit('submit', "Submit"))
        
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


class CreditNoteForm( forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(models.Invoice.objects.all(), widget=forms.HiddenInput)
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


class InvoiceForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        fields = ["status", 'customer', 'tax', 'purchase_order_number', 'ship_from', 'date', 'due', 'salesperson']
        model = models.Invoice

class InvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = ["status", 'customer', 'tax', 'purchase_order_number', 'ship_from', 'date', 'due', 'salesperson',  'terms', 'comments']
        model = models.Invoice

class QuotationForm(InvoiceCreateMixin, forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        fields = ["status", 'customer', 'tax', 'quotation_date', 'quotation_valid', 'salesperson', 'terms', 'comments']
        model = models.Invoice

class InvoicePaymentForm(forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(
        models.Invoice.objects.all(), widget=forms.HiddenInput
        )
    
    class Meta:
        exclude = [ 'active']
        model = models.Payment