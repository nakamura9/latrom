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
from django_select2.forms import Select2Widget
from invoicing.models import Customer

from common_data.forms import BootstrapMixin, PeriodReportForm
from inventory.models import Supplier, WareHouse

from . import models


class ConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.AccountingSettings
        exclude = "is_configured", 'service_hash'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        
class AssetForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Asset
        widgets = {
            'credit_account': Select2Widget(attrs={'data-width': '20rem'})
        }

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
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), 
        widget=Select2Widget(attrs={'data-width': '20rem'}), required=False)
    class Meta:
        exclude = "entry", 'debit_account',
        model = models.Expense

        widgets = {
            'description':forms.Textarea(attrs={'rows':4, 'cols':15}),           
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic',
                    
                    Row(
                        Column('amount', css_class='form-group col-6'),
                        Column('date', css_class='form-group col-6'),                        
                    ),
                    'description',
                    'category',
                    Row(
                        Column('recorded_by', css_class='form-group col-6'),                        
                        Column('reference', css_class='form-group col-6'),                        
                    )
                ),
                Tab('Billing',
                    'billable',
                    'customer',
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class RecurringExpenseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "last_created_date", 'entry', 'debit_account'
        model = models.RecurringExpense
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4
            })
        }

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
                        Column('cycle', css_class='form-group col-6'),
                    ),
                    'description',
                    Row(
                        Column('category', css_class='form-group col-6'),
                        Column('recorded_by', css_class='form-group col-6'),
                    ),
                    'reference'
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class DirectPaymentForm(BootstrapMixin, forms.Form):
    date = forms.DateField()
    paid_to = forms.ModelChoiceField(Supplier.objects.all(),
        widget=Select2Widget)
    account_paid_from = forms.ModelChoiceField(models.Account.objects.all(),
        widget=Select2Widget)
    method = forms.ChoiceField(choices=[
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('ecocash', 'Ecocash')])
    amount = forms.CharField(widget=forms.NumberInput)
    reference = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))

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
                        'notes'
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
    credit = forms.ModelChoiceField(models.Account.objects.all(), 
        widget=Select2Widget)
    debit = forms.ModelChoiceField(models.Account.objects.all(),
        widget=Select2Widget)
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
            'memo':forms.Textarea(attrs={'rows':6, 'cols':15}),           
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date','journal', 'created_by',
                    css_class='form group col-6'),
                Column('draft','memo', css_class='form group col-6'),
            ),            
            HTML(
                """
                <div id="transaction-table">
            </div>
            """
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class AccountForm(forms.ModelForm, BootstrapMixin):
    #account_code = forms.IntegerField(required=False)
    class Meta:
        exclude="active",
        model = models.Account
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'parent_account': Select2Widget(attrs={'data-width': '14rem'})

        }
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
                    'description',
                ),
                Tab('account',
                    #'account_code',
                    'bank_account_number',
                    'parent_account',
                    'pk',
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

class BillForm(BootstrapMixin, forms.ModelForm):
    data = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = '__all__'
        model = models.Bill
        widgets = {
            'memo': forms.Textarea(attrs={'rows': 2})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'data',
            Row(
                Column('date', 'due', css_class='col-6'),
                Column('vendor', 'reference', css_class='col-6'),
            ),
            'memo',
            HTML("<div id='bill-table'></div>")
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class BillPaymentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = models.BillPayment
        widgets = {
            'bill': forms.HiddenInput,
            'account': Select2Widget,
            'memo': forms.Textarea(attrs={'rows': 6})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'bill',
            Row(
                Column('date', 'account', 'amount', css_class='col-6'),
                Column('memo', css_class='col-6'),
            ),
            HTML("<div id='bill-table'></div>")
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class AccountImportForm(forms.Form):
    file = forms.FileField()
    sheet_name = forms.CharField()
    name = forms.IntegerField()
    description = forms.IntegerField()
    balance = forms.IntegerField()
    type = forms.IntegerField()
    code = forms.IntegerField()
    balance_sheet_category = forms.IntegerField()
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
            <p>State the columns that correspond to the required features to populate an account.Convert alphabetic columns to numbers and insert below e.g. A=1, D=4 etc.</p>
            <ul>
                <li>Name - the label for the account</li>
                <li>Description</li>
                <li>Balance - current balance of the account</li>
                <li>Type - each row must be populated with one of expense, asset, income, cost-of-sales, liability, equity</li>
                <li>Balance sheet category - each cell must be populated with one of current_assets, long-term-assets, current-liabilities, long_term-liabilities, equity or not_included </li>
            </ul>"""),
            Row(
                Column('name', css_class='col-2'),
                Column('description', css_class='col-2'),
                Column('balance', css_class='col-2'),
                Column('code', css_class='col-2'),
                Column('type', css_class='col-2'),
                Column('balance_sheet_category', css_class='col-2'),
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

class BulkAccountsForm(forms.Form):
    data = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'data',
            HTML("""<div id='accounts-list'></div>""")
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class ImportJournalEntryForm(BootstrapMixin, forms.Form):
    date = forms.IntegerField()
    memo = forms.IntegerField()
    file = forms.FileField()
    sheet_name = forms.CharField(max_length = 256)
    start_row = forms.IntegerField()
    end_row = forms.IntegerField()
    credit = forms.IntegerField()
    debit = forms.IntegerField()
    entry_id = forms.IntegerField()
    account = forms.IntegerField()

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
            <p>State the columns that correspond to the required features to populate an account.Convert alphabetic columns to numbers and insert below e.g. A=1, D=4 etc.</p>
            <ul>
                <li>Date - in the format DD/MM/YYYY</li>
                <li>Entry ID - number represeting unique entry identifier</li>
                <li>Memo - short description of transaction</li>
                <li>Credit - amount credited account</li>
                <li>Debit - amount debited the account</li>
                <li>Account - the code of the account affected</li>
            </ul>"""),
             Row(
                Column('date', css_class='col-2'),
                Column('entry_id', css_class='col-2'),
                Column('memo', css_class='col-2'),
                Column('credit', css_class='col-2'),
                Column('debit', css_class='col-2'),
                Column('account', css_class='col-2'),
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


class MultipleEntriesForm(forms.Form):
    data = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'data',
            HTML("""<div id='entries-list'></div>""")
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class ImportExpensesForm(BootstrapMixin, forms.Form):
    file = forms.FileField()
    sheet_name = forms.CharField(max_length = 256)
    start_row = forms.IntegerField()
    end_row = forms.IntegerField()
    amount = forms.IntegerField()
    description = forms.IntegerField()
    category = forms.IntegerField()
    date = forms.IntegerField()
    account_paid_from  = forms.ModelChoiceField(
        models.Account.objects.filter(type='asset'), widget=Select2Widget)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>File</h4>'),
            Row(
                Column('file', css_class='col-6'),
                Column('sheet_name', css_class='col-6'),
            ),
            'account_paid_from',
            HTML("""
            <h4>Columns</h4>
            <p>State the columns that correspond to the required features to record an expense.Convert alphabetic columns to numbers and insert below e.g. A=1, D=4 etc.</p>
            <ul>
                <li>Date - in the format DD/MM/YYYY</li>
                <li>Description - short description of the expense incurred</li>
                <li>Category - The type of expense one of: Advertising, Bank And Service Charges, Dues and Subscriptions, Equipment Rental, Telephone, Vehicles, Travel and Expenses, Supplies, Salaries and Wages, Rent, Payroll Taxes, Legal and Accounting, Insurance, Office Expenses, Carriage Outwards, Training and Vendor Services. NB: Categories are case-sensitive and will default to other if not among those listed.</li>
                <li>Amount - amount expensed</li>
            </ul>"""),
             Row(
                Column('date', css_class='col-3'),
                Column('description', css_class='col-3'),
                Column('category', css_class='col-3'),
                Column('amount', css_class='col-3'),
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


class MultipleExpensesForm(forms.Form):
    data = forms.CharField(widget=forms.HiddenInput)
    account_paid_from  = forms.ModelChoiceField(
        models.Account.objects.filter(type='asset'), widget=Select2Widget)

    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'data',
            'account_paid_from',
            HTML("""<div id='expenses-list'></div>""")
        )
        self.helper.add_input(Submit('submit', 'Submit'))