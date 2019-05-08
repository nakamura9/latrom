from django import forms
from crispy_forms.bootstrap import TabHolder, Tab
from common_data.forms import BootstrapMixin
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper

from crispy_forms.layout import (Row, 
                                Column, 
                                Fieldset,
                                Submit, 
                                Layout,
                                HTML)
from . import models
from employees.models import Employee


class ServiceForm(forms.ModelForm,BootstrapMixin):
    category = forms.ModelChoiceField(models.ServiceCategory.objects.all(), required=False)

    class Meta:
        fields = "__all__"
        model = models.Service

        widgets = {
                'description':forms.Textarea(attrs={'rows':4, 'cols':15}), 
            }   
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                    'name',
                    'description',
                    Row(
                        Column('flat_fee', css_class='form-group col-6'),
                        Column('hourly_rate', css_class='form-group col-6'),
                    ),
                    Row(
                        Column('category', css_class='form-group col-4'),
                        Column('procedure', css_class='form-group col-4'),
                        Column('frequency', css_class='form-group col-4'),
                    ),
                    'is_listed',
    )
        self.helper.add_input(Submit('submit', 'Submit'))
class ServiceCategoryForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.ServiceCategory


class ServicePersonForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.ServicePerson
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
class ServicePersonUpdateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "employee",
        model = models.ServicePerson


class ServiceTeamForm(forms.ModelForm, BootstrapMixin):
    #create members in react
    class Meta:
        exclude = "members",
        model = models.ServiceTeam

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Team Creation Form',
                    'name',
                    'description',
                    'manager',
                ),
                Tab('Service People',
                    HTML(
                    """
                    <div class="col-sm-4"><div id="personnel-list"></div>
                    """
                    )
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit')) 

class ServiceWorkOrderForm(forms.ModelForm, BootstrapMixin):
    #create service people in react
    status = forms.CharField(widget=forms.HiddenInput)
    works_request = forms.ModelChoiceField(
        models.WorkOrderRequest.objects.all(),
        widget=forms.HiddenInput)
    class Meta:
        fields = ['date', 'time', 'expected_duration', 'team', 'status', 'description', 'works_request' ]
        model = models.ServiceWorkOrder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Form',
                    Row(
                        Column('date', css_class="form group col-6"),
                        Column('time', css_class="form group col-6"),
                    ),
                    'internal',
                    'works_request',
                    'description',
                    'completed',
                    'expected_duration',
                    'status',
                    'authorized_by',
                    'team',
                    'progress',
                ),
                Tab('Service People',
                    HTML(
                        """
                        <div id="work-order-persons">

            </div>      
                        """
                    ),
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))
        
class ServiceWorkOrderCompleteForm(forms.ModelForm, BootstrapMixin):
    progress = forms.CharField(widget=forms.HiddenInput, required=False)
    service_time = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        fields = ["progress"]
        model = models.ServiceWorkOrder


class ServiceWorkOrderAuthorizationForm(BootstrapMixin, forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    authorized_by = forms.ModelChoiceField(Employee.objects.all())
    status = forms.ChoiceField(choices=models.ServiceWorkOrder.STATUS_CHOICES)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        password = cleaned_data['password']
        employee = cleaned_data['authorized_by']

        if not authenticate(username=employee.user.username, password=password):
            raise forms.ValidationError('The password supplied is incorrect.')

        return cleaned_data

class EquipmentRequisitionForm(forms.ModelForm, BootstrapMixin):
    equipment = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        exclude = "authorized_by", "released_by", 'received_by', 'returned_date'
        model = models.EquipmentRequisition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date','equipment' , css_class="col-sm-6"), 
                Column('work_order', css_class="col-sm-6"), css_class="form-row"),
            Row(
                Column('department', css_class="col-sm-6"),
                Column('warehouse', css_class="col-sm-6"), 
                 css_class="form-row"),
            Row(
                Column('reference', css_class="col-sm-6"), 
                Column('requested_by', css_class="col-sm-6"), css_class="form-row")
        )
        self.helper.add_input(Submit('submit', 'Submit'))
        


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
    consumables = forms.CharField(widget=forms.HiddenInput)
    
    class Meta:
        exclude = "authorized_by", "released_by",
        model = models.ConsumablesRequisition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date', 'consumables', css_class="col-sm-6"), 
                Column('work_order', css_class="col-sm-6"), css_class="form-row"),
            Row(
                Column('department', css_class="col-sm-6"),
                Column('warehouse', css_class="col-sm-6"), 
                 css_class="form-row"),
            Row(
                Column('reference', css_class="col-sm-6"), 
                Column('requested_by', css_class="col-sm-6"), css_class="form-row")
        )
        self.helper.add_input(Submit('submit', 'Submit'))


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
                css_class="form-row"),
        )
class ServiceProcedureForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        exclude = "required_equipment", "required_consumables"
        model = models.ServiceProcedure
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Procedure Details',
                    'name',
                    'reference',
                    'author',
                    'description',
                ),
                Tab('procedure steps',
                    HTML(
                        """
                        <div id="procedure-widgets" style="display:block;clear:both">
                        </div>
                        """
                    )
                ),
                Tab('Select Equipment And Consumables',
                    HTML(
                        """
            <div id="inventory-widgets" style="display:block;clear:both"></div>
                        """
                    )
                ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class EquipmentReturnForm(BootstrapMixin, forms.Form):
    received_by = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    return_date = forms.DateField()