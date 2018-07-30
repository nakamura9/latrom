
from django import forms
from common_data.forms import BootstrapMixin, PeriodReportForm
from accounting.models import Account, Journal
import models
from django.forms.widgets import HiddenInput, MultipleHiddenInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Submit
from crispy_forms.bootstrap import TabHolder, Tab

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


class QuickCustomerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ['individual', 'organization', 'billing_address']
        model = models.Customer


class SalesRepForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'active',
        model = models.SalesRepresentative

class PaymentForm(forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(
        models.Invoice.objects.filter(type_of_invoice ='credit'))
    class Meta:
        fields = '__all__'
        model = models.Payment


class PaymentUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['invoice', 'amount']
        model = models.Payment


class InvoiceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 
        model = models.Invoice

class SalesInvoiceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 
        model = models.SalesInvoice

class ServiceInvoiceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 
        model = models.ServiceInvoice

class BillForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'discount'
        model = models.Bill

class CombinedInvoiceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active", 'discount'
        model = models.CombinedInvoice


class InvoiceUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'type_of_invoice','saleseperson', 'customer', 'date_issued', 'due_date']
        model = models.Invoice

class QuoteForm(forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        super(QuoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
            Tab('Details', 
                'date',
                'customer',
                'salesperson',
                'tax'),
            Tab('Comments',
                'comments')
        ))
        self.helper.add_input(Submit('submit', 'Submit'))
    
    class Meta:
        fields = ["date","customer", "comments", 'tax', 'salesperson']
        model = models.Quote
        

class CreditNoteForm( forms.ModelForm, BootstrapMixin):
    invoice = forms.ModelChoiceField(models.Invoice.objects.exclude(customer__account__isnull=True))
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