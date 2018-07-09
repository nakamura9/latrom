
from django import forms
from common_data.forms import BootstrapMixin
import models
from inventory.models import Supplier
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from crispy_forms.bootstrap import TabHolder, Tab
from django.contrib.auth.models import User

class ConfigForm(BootstrapMixin, forms.Form):
    start_of_financial_year = forms.DateField()
    use_default_account_names = forms.BooleanField()
    direct_payment_journal = forms.ModelChoiceField(models.Journal.objects.all())
    cash_sale_account = forms.ModelChoiceField(
        models.Account.objects.all())
    direct_payment_account = forms.ModelChoiceField(
        models.Account.objects.all())

class AssetForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Asset

class ExpenseForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Expense

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
    #items = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput)
    comments = forms.CharField(widget=forms.Textarea)

class AllowanceForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Allowance

    
class CommissionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.CommissionRule

class DeductionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude="active",
        model = models.Deduction


class PayGradeForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.PayGrade

class EmployeeForm(forms.ModelForm, BootstrapMixin):
    link_with_user = forms.BooleanField(required=False)
    username = forms.CharField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=False, 
        widget=forms.PasswordInput)
    class Meta:
        exclude="active", 'user',
        model = models.Employee

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)


        if self.instance and self.instance.user:
                self.fields['username'].initial = self.instance.user.username
                self.fields['link_with_user'].initial = True
        
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
                    'pay_grade',
                    'leave_days',
                    ),
                Tab('User Details', 
                'link_with_user', 
                'username',
                'password', 
                'confirm_password')))
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()

        if cleaned_data.get('link_with_user'):
            if cleaned_data.get('username') == "":
                raise forms.ValidationError("If an employee is going to be"
                    "linked with a user a username must be specified")
            else:
                if cleaned_data.get('password') == "" \
                        or cleaned_data.get("confirm_password") == "":
                    raise forms.ValidationError("The password fields cannot be blank")
                elif cleaned_data.get("password") != \
                        cleaned_data.get("confirm_password"):
                    raise forms.ValidationError("The passwords must match")
                else:
                    #matching non void passwords
                    try:
                        if self.instance and self.instance.user:
                            #updating existing users
                            self.instance.user.username = cleaned_data.get(
                                "username")
                            self.instance.user.set_password(
                                cleaned_data.get('password'))
                            self.instance.user.save()
                        else:
                            self.created_user = User.objects.create(
                                first_name=cleaned_data.get("first_name"),
                                last_name=cleaned_data.get("last_name"),
                                username=cleaned_data.get("username"))
                            self.created_user.set_password(
                                cleaned_data.get("password"))
                        #necessary!
                            self.created_user.save()
                    except:
                        raise forms.ValidationError('Failed to create User')
                    else:
                        return cleaned_data

        return cleaned_data

    def save(self, *args, **kwargs):
        obj = super(EmployeeForm, self).save(*args, **kwargs)
        if hasattr(self, 'created_user'):
            self.instance.user = self.created_user
            self.instance.save()
        return obj
