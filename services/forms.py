from django import forms
import models 
from common_data.forms import BootstrapMixin

class ServiceForm(forms.ModelForm,BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Service

class ServiceCategoryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = 'parent',
        model = models.ServiceCategory

class ServiceManagerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.ServicesManager

class ServicePersonForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.ServicesPerson


class ServiceTeamForm(forms.ModelForm, BootstrapMixin):
    #create members in react
    class Meta:
        exclude = "members",
        model = models.ServiceTeam

class ServiceWorkOrderCreateForm(forms.ModelForm, BootstrapMixin):
    #create service people in react
    class Meta:
        fields = ['date', 'time', 'expected_duration', 'team' ]
        model = models.ServiceWorkOrder

class ServiceWorkOrderCompleteForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = ["actual_duration", "comments"]
        model = models.ServiceWorkOrder

class EquipmentRequisitionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "authorized_by", "released_by",
        model = models.EquipmentRequisition


class ConsumablesRequisitionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "authorized_by", "released_by",
        model = models.ConsumablesRequisition

class ServiceProcedureForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "required_equipment", "required_consumables"
        model = models.ServiceProcedure