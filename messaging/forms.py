from django import forms
from .models import *
from common_data.forms import BootstrapMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, HTML, Row, Column
from crispy_forms.bootstrap import Tab, TabHolder
from django.contrib.auth.models import User
from draftjs_exporter.dom import DOM
from draftjs_exporter.html import HTML as exporterHTML
import json
import urllib
from messaging.email_api.secrets import get_secret_key
from cryptography.fernet import Fernet


class EmailForm(BootstrapMixin, forms.ModelForm):
    body = forms.CharField(widget=forms.HiddenInput, required=True)
    folder = forms.ModelChoiceField(EmailFolder.objects.all(),
        widget=forms.HiddenInput)
    owner = forms.ModelChoiceField(User.objects.all(),
                                    widget=forms.HiddenInput)
    save_as_draft = forms.BooleanField(required=False)
    class Meta:
        fields = ['save_as_draft', 
                'folder', 'subject', 'body', 'owner', 'attachment']
        model = Email

    def clean(self):
        
        cleaned_data = super().clean()

        config = {}
        exporter = exporterHTML(config)
        try:
            msg = exporter.render(json.loads(
                urllib.parse.unquote(cleaned_data['body'])
            ))
        except json.decoder.JSONDecodeError:
            raise forms.ValidationError('The message must have content')
            
        if cleaned_data['attachment'] and \
                cleaned_data['attachment'].size > 5000000:
            raise forms.ValidationError('The uploaded file exceeds 5MB')

        cleaned_data['body'] = msg
        return cleaned_data

class PrePopulatedEmailForm(EmailForm):
    attachment_path = forms.CharField(widget=forms.HiddenInput)
    attachment = forms.FileField(widget=forms.HiddenInput, required=False)
    class Meta:
        fields = ['attachment_path',
                    'save_as_draft', 
                'folder', 'subject', 'body', 'owner', 'attachment'
                  ]
        model = Email
class GroupForm(forms.ModelForm):
    admin = forms.ModelChoiceField(
        User.objects.all(), widget=forms.HiddenInput)
    icon = forms.ImageField(required=False)

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
            HTML("""
            <p>Participants</p>
            <div id="group-participant-select"></div>""")
        )

        self.helper.add_input(Submit('submit', "Create Group"))


class UserProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), widget=forms.HiddenInput)
    
    class Meta:
        fields = "__all__"
        model = UserProfile
        widgets ={
            'email_password': forms.PasswordInput(render_value=True)
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic',
                    Row(
                        Column('user', 'avatar', 'email_address',
                            'email_password', css_class='form-group col-6'),
                        Column(HTML("""
                            {% load render_bundle from webpack_loader %}
                            {% render_bundle 'widgets' %}
                            <div id="avatar-preview"></div>
                        """), css_class='form-group col-6'),
                    )
                ),
                Tab('Advanced',
                    'outgoing_server',
                    'outgoing_port',
                    'incoming_host',
                    'incoming_port'
                )
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['email_password'].encode()
        crypt = Fernet(get_secret_key())
        cleaned_data['email_password'] = crypt.encrypt(password).decode() 

        return cleaned_data
class AxiosEmailForm(forms.Form):
    attachment = forms.FileField(required=False)
    body = forms.CharField()

class EmailAddressForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = EmailAddress
        fields = "__all__"
