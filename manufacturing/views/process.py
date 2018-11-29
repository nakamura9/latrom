import os

from django.views.generic.edit import CreateView
from manufacturing.views.util import ManufacturingCheckMixin
from manufacturing import models
from manufacturing import forms 
from common_data.utilities import ExtraContext

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class ProcessCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process'
    }

class ProcessMachineCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessMachineForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Machine'
    }


class ProcessProductCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessProductForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Product'
    }

class ProductionOrderCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProductionOrderForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Production Order'
    }


class BillOfMaterialsCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.BillOfMaterialsForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Bill Of Materials'
    }