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


class MessageForm(BootstrapMixin, forms.ModelForm):
    body = forms.CharField(widget=forms.HiddenInput)
    sender = forms.ModelChoiceField(User.objects.all(),
                                    widget=forms.HiddenInput)
    copy = forms.ModelMultipleChoiceField(User.objects.all(),
                                          widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        fields = ['copy', 'recipient',
                  'subject', 'body', 'sender']
        model = Message

    def clean(self):
        cleaned_data = super().clean()

        config = {}
        exporter = exporterHTML(config)
        msg = exporter.render(json.loads(
            urllib.parse.unquote(cleaned_data['body'])
        ))

        cleaned_data['body'] = msg
        print(msg)
        return cleaned_data


class EmailForm(BootstrapMixin, forms.ModelForm):
    body = forms.CharField(widget=forms.HiddenInput)
    sender = forms.ModelChoiceField(User.objects.all(),
                                    widget=forms.HiddenInput)
    copy = forms.ModelMultipleChoiceField(EmailAddress.objects.all(),
                                          widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        fields = ['copy', 'to',
                  'subject', 'body', 'sender']
        model = Email

    def clean(self):
        cleaned_data = super().clean()

        config = {}
        exporter = exporterHTML(config)
        msg = exporter.render(json.loads(
            urllib.parse.unquote(cleaned_data['body'])
        ))

        cleaned_data['body'] = msg
        print(msg)
        return cleaned_data


class GroupForm(forms.ModelForm):
    admin = forms.ModelChoiceField(
        User.objects.all(), widget=forms.HiddenInput)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('user', 'avatar', 'email_address',
                       'email_password', css_class='form-group col-6'),
                Column(HTML("""
                    {% load render_bundle from webpack_loader %}
                    {% render_bundle 'widgets' %}
                    <div id="avatar-preview"></div>
                """), css_class='form-group col-6'),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))
