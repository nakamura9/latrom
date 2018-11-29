from django import forms 
from common_data.forms import BootstrapMixin
from manufacturing import models

class ShiftForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.Shift
        fields = "__all__"

class ShiftScheduleForm(forms.ModelForm, BootstrapMixin):
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

class ProcessProductForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProcessProduct
        fields = "__all__"

class ProductionOrderForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.ProductionOrder
        fields = "__all__"


class BillOfMaterialsForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = models.BillOfMaterials
        fields = "__all__"