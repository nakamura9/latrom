
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.contrib.auth.models import User

from common_data.forms import BootstrapMixin
from inventory.models import Supplier, WareHouse

from . import models


class ConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.AccountingSettings
        fields = "__all__"
        
class AssetForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Asset

class ExpenseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "__all__"
        model = models.Expense

class RecurringExpenseForm(forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        super(RecurringExpenseForm, self).__init__(*args, **kwargs)
        self.fields['recurring'].value =True

    class Meta:
        fields = "__all__"
        model = models.RecurringExpense

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
    

class TaxForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields ='__all__'
        model = models.Tax

class SimpleJournalEntryForm(forms.ModelForm, BootstrapMixin):
    amount = forms.DecimalField()
    credit = forms.ModelChoiceField(models.Account.objects.all())
    debit = forms.ModelChoiceField(models.Account.objects.all())
    class Meta:
        fields="__all__"
        model = models.JournalEntry

    def save(self, *args, **kwargs):
        obj = super(SimpleJournalEntryForm, self).save(*args, **kwargs)
        obj.simple_entry(
            self.cleaned_data['amount'],
            self.cleaned_data['credit'],
            self.cleaned_data['debit']
        )
        return obj

class ComplexEntryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields="__all__"
        model = models.JournalEntry

class AccountForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Account

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
