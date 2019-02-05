from django import forms

from common_data.forms import BootstrapMixin
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper

from crispy_forms.layout import Row, Column, Fieldset, Layout
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
    works_request = forms.ModelChoiceField(
        models.WorkOrderRequest.objects.all(),
        widget=forms.HiddenInput)
    class Meta:
        fields = ['date', 'time', 'expected_duration', 'team', 'status', 'description', 'works_request' ]
        model = models.ServiceWorkOrder

class ServiceWorkOrderCompleteForm(forms.ModelForm, BootstrapMixin):
    progress = forms.CharField(widget=forms.HiddenInput, required=False)
    service_time = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        fields = ["progress"]
        model = models.ServiceWorkOrder


class ServiceWorkOrderAuthorizationForm(forms.ModelForm, BootstrapMixin):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        fields = ["authorized_by", "status"]
        model = models.ServiceWorkOrder

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        user = cleaned_data['authorized_by']

        if not authenticate(username=user.user.username, password=password):
            raise forms.ValidationError('The password supplied is incorrect.')

        return cleaned_data

class EquipmentRequisitionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "authorized_by", "released_by", 'received_by', 'returned_date'
        model = models.EquipmentRequisition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date', css_class="col-sm-6"), 
                Column('work_order', css_class="col-sm-6"), css_class="form-row"),
            Row(
                Column('department', css_class="col-sm-6"),
                Column('warehouse', css_class="col-sm-6"), 
                 css_class="form-row"),
            Row(
                Column('reference', css_class="col-sm-6"), 
                Column('requested_by', css_class="col-sm-6"), css_class="form-row")
        )
        


class WorkOrderEquipmentRequisitionForm(forms.ModelForm, BootstrapMixin):
    work_order = forms.ModelChoiceField(models.ServiceWorkOrder.objects.all(), 
        widget=forms.HiddenInput)
    class Meta:
        exclude = "authorized_by", "released_by", 'received_by', 'returned_date'
        model = models.EquipmentRequisition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('work_order', css_class="col-sm-12"), css_class="form-row"),
            Row(
                Column('date', css_class="col-sm-6"), 
                Column('requested_by', css_class="col-sm-6"), css_class="form-row"),
            Row(
                Column('department', css_class="col-sm-6"),
                Column('warehouse', css_class="col-sm-6"), 
                 css_class="form-row"),
            Row(
                Column('reference', css_class="col-sm-12"),
                css_class="form-row")
        )
    

class ConsumablesRequisitionForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "authorized_by", "released_by",
        model = models.ConsumablesRequisition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date', css_class="col-sm-6"), 
                Column('work_order', css_class="col-sm-6"), css_class="form-row"),
            Row(
                Column('department', css_class="col-sm-6"),
                Column('warehouse', css_class="col-sm-6"), 
                 css_class="form-row"),
            Row(
                Column('reference', css_class="col-sm-6"), 
                Column('requested_by', css_class="col-sm-6"), css_class="form-row")
        )

class WorkOrderConsumablesRequisitionForm(forms.ModelForm, BootstrapMixin):
    work_order = forms.ModelChoiceField(models.ServiceWorkOrder.objects.all(), 
        widget=forms.HiddenInput)
    class Meta:
        exclude = "authorized_by", "released_by",
        model = models.ConsumablesRequisition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('work_order', css_class="col-sm-12"), css_class="form-row"),
            Row(
                Column('date', css_class="col-sm-6"), 
                Column('requested_by', css_class="col-sm-6"), css_class="form-row"),
            Row(
                Column('department', css_class="col-sm-6"),
                Column('warehouse', css_class="col-sm-6"), 
                 css_class="form-row"),
            Row(
                Column('reference', css_class="col-sm-12"),
                css_class="form-row")
        )
class ServiceProcedureForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "required_equipment", "required_consumables"
        model = models.ServiceProcedure


class EquipmentReturnForm(BootstrapMixin, forms.Form):
    received_by = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    return_date = forms.DateField()