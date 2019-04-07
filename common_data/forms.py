from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms import ValidationError
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (HTML, 
                                Fieldset, 
                                Layout, 
                                Submit)


from . import models


class BootstrapMixin(forms.Form):
    """This class intergrates bootstrap into select form fields
    
    The class is a mixin that adds the 'form-control class' to each field in the form as well as making each text input have a placeholder instead of a label. It can be used as a common point for inserting other standard behaviour in the future."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control input-sm"

            if isinstance(field.widget, forms.widgets.DateInput):
                field.widget.attrs['class'] += " ui-date-picker"
            
period_choices = [
        '-Custom Period-',
        'Last Week', 
        'Last Month', 
        'Last Quarter', 
        'Last 6 Months', 
        'Last Year'
        ]
PERIOD_CHOICES = [(period_choices.index(i), i) for i in period_choices]


class PeriodReportForm(BootstrapMixin, forms.Form):
    default_periods = forms.ChoiceField(choices=PERIOD_CHOICES)
    start_period = forms.DateField(required=False)
    end_period = forms.DateField(required=False)


class OrganizationForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Organization

class IndividualForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Individual

class GlobalConfigForm(forms.ModelForm, BootstrapMixin):
    #not showing password on update view
    #email_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        fields = "__all__"
        model = models.GlobalConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Business Details',
                    'business_name',
                    'business_address',
                    'logo',
                    'document_theme',
                    'currency',
                    'payment_details',
                    'contact_details',
                    'business_registration_number'),
                Tab('Email Config',
                    'email_host',
                    'email_port',
                    'email_user',
                    'email_password',
                )
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class SendMailForm(BootstrapMixin, forms.Form):
    recipient = forms.EmailField()
    subject = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)

class AuthenticateForm(BootstrapMixin, forms.Form):
    user = forms.ModelChoiceField(User.objects.all())
    password = forms.CharField(widget=forms.PasswordInput)


    def clean(self):
        cleaned_data = super().clean()
        user = authenticate(username=cleaned_data['user'].username,
                            password=cleaned_data['password'])
        
        if not user:
            raise ValidationError('The user did not authenticate properly')


        return cleaned_data