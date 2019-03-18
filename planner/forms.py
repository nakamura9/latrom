from django import forms
from django.contrib.auth.models import User

from common_data.forms import BootstrapMixin

from . import models


class ConfigForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.PlannerConfig
        fields = "number_of_agenda_items",

class EventForm(forms.ModelForm, BootstrapMixin):
    owner = forms.ModelChoiceField(
        User.objects.all(), 
        widget=forms.HiddenInput
        )
    json_participants = forms.CharField(
        widget=forms.HiddenInput
        )
    class Meta:
        model = models.Event
        exclude = ["participants", 'completed', 'completion_time']
