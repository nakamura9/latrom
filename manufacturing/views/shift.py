import os 
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView
from manufacturing.views.util import ManufacturingCheckMixin
from common_data.utilities import ExtraContext
from manufacturing import models 
from manufacturing import forms
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class ShiftCreateView(ExtraContext, ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ShiftForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Shift'
    }

class ShiftScheduleCreateView(ExtraContext, 
        ManufacturingCheckMixin, 
        CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ShiftScheduleForm
    success_url = '/manufacturing/'

    extra_context = {
        'title': 'Create Shift Schedule'
    }