from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms import ValidationError
from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (HTML, 
                                Row,
                                Column,
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
            field.widget.attrs['class'] ="form-control form-control-sm"

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

    def clean(self):
        data = super().clean()
        if data['default_periods'] == 0 and (data['start_period'] == "" or \
                data['end_period'] == ""):
            raise forms.ValidationError('Select either a default period or select a custom start and end periods')

        return data

class OrganizationForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Organization

class IndividualForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'active',
        model = models.Individual
        widgets ={
            'address': forms.Textarea(attrs={'rows': 4}),
            'other_details': forms.Textarea(attrs={'rows': 8})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-6'),
                Column('last_name', css_class='col-6'),
            ),
            'address',
            Row(
                Column('email', 'phone', 'phone_two', css_class='col-6'),
                Column('other_details', css_class='col-6'),
            ),
            'photo',
            'organization',
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class GlobalConfigForm(forms.ModelForm, BootstrapMixin):
    #not showing password on update view
    #email_password = forms.CharField(widget=forms.PasswordInput)
    organization_name = forms.CharField()
    organization_logo =forms.ImageField(required=False)
    organization_email = forms.EmailField(required=False)
    organization_phone = forms.CharField(required=False)
    organization_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows':4}))
    organization_website = forms.CharField(required=False)
    organization_business_partner_number = forms.CharField(required=False)
    use_backups = forms.BooleanField(label="Use backups?", required=False)
    #backup_location_type= forms.ChoiceField(
    #        widget=forms.RadioSelect, choices=[
    #            ('local', 'Local File System'),
    #            ('network', 'Network Storage via FTP')
    #            ], required=False)
    
    class Meta:
        exclude = "hardware_id", "application_version", "last_license_check",'document_theme', 'currency', 'organization', "backup_location_type", "backup_location", 'is_configured', 'last_automated_service_run',
        model = models.GlobalConfig

        widgets = {
            'business_address':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'contact_details':forms.Textarea(attrs={'rows':4, 'cols':15}),
            'payment_details':forms.Textarea(attrs={'rows':8, 'cols':15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Business Details',

                    'organization_name',
                    'organization_address',
                    'organization_business_partner_number',
                    Row(
                        Column('organization_logo',
                                'logo_aspect_ratio',
                            css_class='form-group col-6'),
                        Column(
                            HTML("""
                        <img id="id-logo-preview" width="300" height="200" class="img" src="" alt="logo image" />"""),
                            css_class='form-group col-6')
                    ),
                    Row(
                    
                        Column('payment_details', css_class='form-group col-6'),
                        Column(
                            Row(Column('organization_email', 
                                css_class='form-group col-12')),
                            Row(Column('organization_phone', 
                                css_class='form-group col-12')),
                            Row(Column('organization_website', 
                                css_class='form-group col-12')),
                            css_class='form-group col-6'
                        )
                    )
                    ),
                
                Tab('Backups',
                    'use_backups',
                    'backup_frequency',
                )
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        if instance.organization:
            org = instance.organization
        else:
            org = models.Organization()

        org.legal_name = self.cleaned_data['organization_name'] 
        org.business_address = self.cleaned_data['organization_address']
        org.website = self.cleaned_data['organization_website']
        org.bp_number = \
            self.cleaned_data['organization_business_partner_number']
        org.email = self.cleaned_data['organization_email']
        org.phone = self.cleaned_data['organization_phone']
        org.logo = self.cleaned_data['organization_logo']

        org.save()
        instance.organization = org
        instance.save()

        return instance

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