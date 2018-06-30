
from django import forms
from common_data.forms import BootstrapMixin
import models
from inventory.models import Supplier
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import TabHolder, Tab

class ConfigForm(BootstrapMixin, forms.Form):
    start_of_financial_year = forms.DateField()
    use_default_account_names = forms.BooleanField()
    direct_payment_journal = forms.ModelChoiceField(models.Journal.objects.all())
    cash_sale_account = forms.ModelChoiceField(
        models.Account.objects.all())
    direct_payment_account = forms.ModelChoiceField(
        models.Account.objects.all())

class DirectPaymentForm(BootstrapMixin, forms.Form):
    date = forms.DateField()
    paid_to = forms.ModelChoiceField(Supplier.objects.all())
    account_paid_from = forms.ModelChoiceField(models.Account.objects.all())
    account_paid_to = forms.ModelChoiceField(models.Account.objects.all())
    method = forms.ChoiceField(choices=[
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('ecocash', 'Ecocash')])
    amount = forms.CharField(widget=forms.NumberInput)
    reference = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea)
    

class TaxForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields ='__all__'
        model = models.Tax

class TransactionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields="__all__"
        model = models.Transaction


class CompoundTransactionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude=['amount', 'debit', 'credit']
        model = models.Transaction

class AccountForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields="__all__"
        model = models.Account


class TransferForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields= ["date", "amount", "credit", "debit", "memo"]
        model = models.Transaction


class LedgerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields="__all__"
        model = models.Ledger


class JournalForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields="__all__"
        model = models.Journal

class NonInvoicedSaleForm(BootstrapMixin,forms.Form):
    date = forms.DateField()
    #items = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput)
    comments = forms.CharField(widget=forms.Textarea)

class AllowanceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Allowance

    
class CommissionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.CommissionRule

class DeductionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Deduction


class PayGradeForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.PayGrade

'''
class DirectPurchaseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ['date', 'comments']
        model = models.DirectPurchase
'''

class EmployeeForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Employee

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Personal', 
                    'first_name',
                    'last_name',
                    'address',
                    'email',
                    'phone'),
                Tab('Employee Details', 
                    'hire_date',
                    'title',
                    'pay_grade')))
        ''',
                Tab('Payment Details', 
                    'hourly_rate',
                    'overtime_rate',
                    'overtime_two_rate',
                    'monthly_salary',
                    'monthly_leave_days')'''
        self.helper.add_input(Submit('submit', 'Submit'))