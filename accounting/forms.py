from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Fieldset, 
                                Layout, 
                                Submit, 
                                HTML,
                                Row,
                                Column)
from django import forms
from django.contrib.auth.models import User

from common_data.forms import BootstrapMixin, PeriodReportForm
from inventory.models import Supplier, WareHouse

from . import models


class ConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.AccountingSettings
        exclude = "is_configured",

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        
class AssetForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Asset

    init_date =forms.DateField(label="Date purchased")
    depreciation_period = forms.CharField(widget=forms.NumberInput, label="Depreciation Period(years)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    Row(
                        Column('name', css_class='form-group col-6'),
                        Column('created_by', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('initial_value', css_class='form-group col-6'),
                        Column('salvage_value', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('depreciation_period', css_class='form-group col-6'),
                        Column('depreciation_method', css_class='form-group col-6'),                        
                    ),
                    'init_date',
                    'category',
                ),
                Tab('description',
                    'description',
                    'credit_account',
                    
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class ExpenseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "entry", 
        model = models.Expense

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    Row(
                        Column('customer', css_class='form-group col-6'),
                        Column('date', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('amount', css_class='form-group col-6'),
                        Column('debit_account', css_class='form-group col-6'),                        
                    ),
                    'category',
                    'recorded_by',
                ),
                Tab('description',
                    'description',
                    'reference',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class RecurringExpenseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "last_created_date", 'entry'
        model = models.RecurringExpense

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    Row(
                        Column('start_date', css_class='form-group col-6'),
                        Column('expiration_date', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('amount', css_class='form-group col-6'),
                        Column('debit_account', css_class='form-group col-6'),
                    ),
                    'category',
                    'recorded_by',
                    'cycle',
                ),
                Tab('description',
                    'description',
                    'reference',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class DirectPaymentForm(BootstrapMixin, forms.Form):
    date = forms.DateField()
    paid_to = forms.ModelChoiceField(Supplier.objects.all())
    account_paid_from = forms.ModelChoiceField(models.Account.objects.all())
    method = forms.ChoiceField(choices=[
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('ecocash', 'Ecocash')])
    amount = forms.CharField(widget=forms.NumberInput)
    reference = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('basic',
                    'date',
                    Row(
                        Column('paid_to', css_class='form-group col-6'),
                        Column('account_paid_from', css_class='form-group col-6'),
                        ),
                    Row(
                        Column('method', css_class='form-group col-6'),
                        Column('amount', css_class='form-group col-6'),                
                        ),
                        'reference',
                ),
                Tab('notes',
                    'notes',
                ),
            )
            
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class TaxForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields ='__all__'
        model = models.Tax

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

class TaxUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields ='name',
        model = models.Tax

class SimpleJournalEntryForm(forms.ModelForm, BootstrapMixin):
    amount = forms.DecimalField()
    credit = forms.ModelChoiceField(models.Account.objects.all())
    debit = forms.ModelChoiceField(models.Account.objects.all())
    class Meta:
        exclude = "draft", "posted_to_ledger", "adjusted"
        model = models.JournalEntry

    def save(self, *args, **kwargs):
        obj = super(SimpleJournalEntryForm, self).save(*args, **kwargs)
        obj.simple_entry(
            self.cleaned_data['amount'],
            self.cleaned_data['credit'],
            self.cleaned_data['debit']
        )
        return obj
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date', css_class="col-6"),
                Column('created_by', css_class="col-6"),
            ),
            Row(
                Column('credit', css_class="col-6"),
                Column('debit', css_class="col-6"),
            ),
            'memo',
            'journal',
            'amount',
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class ComplexEntryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="posted_to_ledger", "adjusted"
        model = models.JournalEntry

        widgets = {
            'memo':forms.Textarea(attrs={'rows':4, 'cols':15}),           
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date', css_class='form group col-10'),
                Column('draft', css_class='form group col-2'),
            ),
            'memo',
            'journal',
            'created_by',
            HTML(
                """
                <div id="transaction-table">
            </div>
            """
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class AccountForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Account
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('general',
                    'name',
                    'balance',
                    Row(
                        Column('balance_sheet_category', css_class='form-group col-6'),
                        Column('type', css_class='form-group col-6'),
                    ),
                ),
                Tab('account',
                    'bank_account_number',
                    'parent_account',
                    Row(
                        Column('control_account', css_class='form-group col-6'),
                        Column('bank_account', css_class='form-group col-6'),
                    ),
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class AccountUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active", "balance"
        model = models.Account


class LedgerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields="__all__"
        model = models.Ledger


class JournalForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Journal

class NonInvoicedSaleForm(BootstrapMixin,forms.Form):
    date = forms.DateField()
    sold_from = forms.ModelChoiceField(WareHouse.objects.all())
    comments = forms.CharField(widget=forms.Textarea)


class BookkeeperForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "active",
        model = models.Bookkeeper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


class ExchangeTableForm(forms.ModelForm):
    class Meta:
        fields = 'reference_currency', 'name',
        model = models.CurrencyConversionTable

class JournalReportForm(PeriodReportForm):
    journal = forms.ModelChoiceField(models.Journal.objects.all(), 
        widget=forms.HiddenInput)

class AccountReportForm(PeriodReportForm):
    account = forms.ModelChoiceField(models.Account.objects.all(), 
        widget=forms.HiddenInput)
