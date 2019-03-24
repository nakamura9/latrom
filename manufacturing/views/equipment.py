import os
import urllib 
import json

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django_filters.views import FilterView

from manufacturing.views.util import ManufacturingCheckMixin
from manufacturing import models
from manufacturing import forms 
from common_data.utilities import ContextMixin
from manufacturing import serializers
from manufacturing import filters
from rest_framework.viewsets import ModelViewSet
from inventory.models import UnitOfMeasure
from common_data.views import PaginationMixin

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


class ProcessMachineCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessMachineForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Machine'
    }

class ProcessMachineUpdateView(ManufacturingCheckMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessMachineForm
    success_url = '/manufacturing/'
    model = models.ProcessMachine
    extra_context = {
        'title': 'Update Process Machine'
    }

class ProcessMachineDetailView(ManufacturingCheckMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessMachineForm
    success_url = '/manufacturing/'
    model = models.ProcessMachine
    extra_context = {
        'title': 'Update Process Machine'
    }

class ProcessMachineListView(ManufacturingCheckMixin, PaginationMixin, FilterView):
    filterset_class = filters.ProcessMachineFilter
    queryset = models.ProcessMachine.objects.all()
    template_name = os.path.join('manufacturing', 'process', 'equipment', 'list.html')

class ProcessMachineDetailView(ManufacturingCheckMixin, DetailView):
    queryset = models.ProcessMachine.objects.all()
    template_name = os.path.join('manufacturing', 'process', 'equipment', 'detail.html')


class ProcessMachineGroupCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 'process','equipment', 'machine_group', 'create.html')
    form_class = forms.ProcessMachineGroupForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'New Process Machine Group',
        'description': 'use this form to organize multiple machines into a single group focused on one process'
    }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if self.object is None:
            return resp

        form = self.form_class(request.POST)
       
        if form.is_valid():
            machine_string = request.POST['machines']
        else:
            return resp

        if machine_string != "":
            data = json.loads(urllib.parse.unquote(machine_string))
            
            for choice in data:

                machine = models.ProcessMachine.objects.get(
                    pk=choice['value'].split('-')[0])
                machine.machine_group = self.object
                machine.save()
                
        return resp

class ProcessMachineGroupListView(ManufacturingCheckMixin, PaginationMixin, 
        FilterView):
    filterset_class = filters.MachineGroupFilter
    queryset = models.ProcessMachineGroup.objects.all()
    template_name = os.path.join('manufacturing', 'process', 'equipment', 
        'machine_group', 'list.html')

class ProcessMachineGroupDetailView(ManufacturingCheckMixin, DetailView):
    queryset = models.ProcessMachineGroup.objects.all()
    template_name = os.path.join('manufacturing', 'process', 'equipment', 
        'machine_group', 'detail.html')

class ProcessMachineAPIView(ModelViewSet):
    queryset = models.ProcessMachine.objects.all()
    serializer_class = serializers.ProcessMachineSerializer
