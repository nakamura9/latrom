from django import forms 
from .models import *
from common_data.forms import BootstrapMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from crispy_forms.bootstrap import Tab, TabHolder
from django.contrib.auth.models import User

class MessageForm(BootstrapMixin, forms.ModelForm):
    sender = forms.ModelChoiceField(User.objects.all(),     
        widget=forms.HiddenInput)

    class Meta:
        fields = ['carbon_copy', 'blind_carbon_copy', 'recipient',
            'subject', 'body', 'sender']
        model = Message