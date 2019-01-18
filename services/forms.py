from django import forms

from common_data.forms import BootstrapMixin

from . import models
from employees.models import Employee


class ServiceForm(forms.ModelForm,BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Service

class ServiceCategoryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.ServiceCategory


class ServicePersonForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.ServicePerson

class ServicePersonUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "employee",
        model = models.ServicePerson


class ServiceTeamForm(forms.ModelForm, BootstrapMixin):
    #create members in react
    class Meta:
        exclude = "members",
        model = models.ServiceTeam

class ServiceWorkOrderForm(forms.ModelForm, BootstrapMixin):
    #create service people in react
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = ['date', 'time', 'expected_duration', 'team', 'status', 'description' ]
        model = models.ServiceWorkOrder

class ServiceWorkOrderCompleteForm(forms.ModelForm, BootstrapMixin):
    status = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        fields = ["status","actual_duration", "comments"]
        model = models.ServiceWorkOrder


class ServiceWorkOrderAuthorizationForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ["authorized_by", "status"]
        model = models.ServiceWorkOrder

class EquipmentRequisitionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "authorized_by", "released_by", 'received_by', 'returned_date'
        model = models.EquipmentRequisition


class ConsumablesRequisitionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "authorized_by", "released_by",
        model = models.ConsumablesRequisition

class ServiceProcedureForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "required_equipment", "required_consumables"
        model = models.ServiceProcedure


class EquipmentReturnForm(BootstrapMixin, forms.Form):
    received_by = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    return_date = forms.DateField()