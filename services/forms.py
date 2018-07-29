from django import forms
import models 
from common_data.forms import BootstrapMixin

class ServiceForm(forms.ModelForm,BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Service

