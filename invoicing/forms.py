
from django import forms
from common_data.utilities import load_config
from common_data.forms import BootstrapMixin
from accounting.models import Account, Journal
import models
from django.forms.widgets import HiddenInput, MultipleHiddenInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Submit
from crispy_forms.bootstrap import TabHolder, Tab

class ConfigForm(forms.Form):
    business_name = forms.CharField()
    business_address = forms.CharField(widget=forms.Textarea)
    contact_details = forms.CharField(widget=forms.Textarea)
    currency = forms.ChoiceField(choices=[("$", "Dollars")])
    '''invoice_account = forms.ModelChoiceField(Account.objects.all())
    invoice_credit_account = forms.ModelChoiceField(Account.objects.all())
    sales_account = forms.ModelChoiceField(Account.objects.all())
    invoice_journal = forms.ModelChoiceField(Journal.objects.all())
    payment_journal = forms.ModelChoiceField(Journal.objects.all())
    '''
    logo = forms.FileField(required = False)
    include_billing = forms.BooleanField(required=False)
    invoice_title = forms.CharField()
    include_shipping = forms.BooleanField(required=False)
    include_business_address = forms.BooleanField(required=False)
    include_discount_column = forms.BooleanField(required=False)
    tax_rate = forms.CharField(widget=forms.NumberInput)
    tax_inclusive = forms.BooleanField(required=False)
    tax_column = forms.BooleanField(required=False)
    invoice_template = forms.ChoiceField(choices=[("1", "Simple"),("2", "Blue"),("3", "Steel"),("4", "Verdant"),("5", "Warm"),])
    registration_number = forms.CharField()
    default_terms = forms.CharField()
    default_invoice_comments = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            

class CustomerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = ['active', 'account']
        model = models.Customer


class QuickCustomerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ['name', 'business_address', 'phone']
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

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["class"] = "form-control ui-date-picker"


class InvoiceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active",
        model = models.Invoice

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

period_choices = ['------','Last Month', 'Last Quarter', 'Last 6 Months', 'Last Year']
PERIOD_CHOICES = [(period_choices.index(i), i) for i in period_choices]
class CustomerStatementReportForm(BootstrapMixin, forms.Form):
    customer = forms.ModelChoiceField(models.Customer.objects.all())
    default_periods = forms.ChoiceField(choices=PERIOD_CHOICES)
    start_period = forms.DateField(required=False)
    end_period = forms.DateField(required=False)

    #custom validator

class PeriodReportForm(BootstrapMixin, forms.Form):
    default_periods = forms.ChoiceField(choices=PERIOD_CHOICES)
    start_period = forms.DateField(required=False)
    end_period = forms.DateField(required=False)