from django import forms 
from common_data.forms import BootstrapMixin
from manufacturing import models

class ShiftForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.Shift
        fields = "__all__"

class ShiftScheduleForm(forms.ModelForm, BootstrapMixin):
    shift_lines = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = models.ShiftSchedule
        fields = "__all__"



class ProcessForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.Process
        fields = "__all__"

class ProcessMachineForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProcessMachine
        fields = "__all__"


class ProcessEquipmentForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProcessEquipment
        fields = "__all__"

class ProcessRateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProcessRate
        fields = "__all__"

class ProcessMachineGroupForm(forms.ModelForm, BootstrapMixin):    
    class Meta:
        model = models.ProcessMachineGroup
        fields = "__all__"

        
class ProcessProductForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProcessProduct
        exclude = 'product_list',

class ProcessProductListForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProductList
        fields = "__all__"

class ProductionOrderForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProductionOrder
        fields = "__all__"


class BillOfMaterialsForm(forms.ModelForm, BootstrapMixin):
    products = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = models.BillOfMaterials
        fields = "__all__"