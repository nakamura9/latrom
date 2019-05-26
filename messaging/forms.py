from django import forms 
from .models import *
from common_data.forms import BootstrapMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, HTML
from crispy_forms.bootstrap import Tab, TabHolder
from django.contrib.auth.models import User

class MessageForm(BootstrapMixin, forms.ModelForm):
    sender = forms.ModelChoiceField(User.objects.all(),     
        widget=forms.HiddenInput)
    copy = forms.ModelMultipleChoiceField(User.objects.all(),
        widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        fields = ['copy', 'recipient',
            'subject', 'body', 'sender']
        model = Message

class GroupForm(forms.ModelForm):
    admin = forms.ModelChoiceField(User.objects.all(), widget=forms.HiddenInput)
    class Meta:
        model = Group
        fields = 'name', 'icon', 'admin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'admin',
            'icon',
            HTML("""<div id="group-participant-select"></div>""")
        )

        self.helper.add_input(Submit('submit', "Create Group"))
