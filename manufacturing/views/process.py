import os
import urllib 
import json

from django.views.generic.edit import CreateView
from manufacturing.views.util import ManufacturingCheckMixin
from manufacturing import models
from manufacturing import forms 
from common_data.utilities import ExtraContext
from manufacturing import serializers
from rest_framework.viewsets import ModelViewSet
from inventory.models import UnitOfMeasure

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class ProcessCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 'process', 'process_create.html')
    form_class = forms.ProcessForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process',
        'related_links': [{
            'name': 'Define Process Equipment',
            'url': '/manufacturing/process-equipment/create'
        },]
    }


class ProcessMachineCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessMachineForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Machine'
    }

class ProcessEquipmentCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessEquipmentForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Process Equipment',
        'description': 'use this form to define the equipment used to '
        'carry out a process',
        'related_links': [{
            'name': 'Create Process Machine',
            'url': '/manufacturing/process-machine/create'
        },
        {
            'name': 'Create Machine Group',
            'url': '/manufacturing/process-machine-group/create'
        },
        ]
    }

class ProcessMachineGroupCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 'process','equipment', 'machine_group_create.html')
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


class ProcessProductCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessProductForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Product'
    }

class ProcessProductListCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 'process','product', 'product_list_create.html')
    form_class = forms.ProcessProductListForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Product List'
    }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if self.object is None:
            return resp

        form = self.form_class(request.POST)
       
        if form.is_valid():
            data_string = request.POST['products']
        else:
            return resp

        

        if data_string != "":
            data = json.loads(urllib.parse.unquote(data_string))
            
            for choice in data:
                product = models.ProcessProduct.objects.get(
                    pk=choice['value'].split('-')[0])
                product.product_list = self.object
                product.save()
                
        return resp

class ProcessRateCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessRateForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Rate'
    }

class ProductionOrderCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProductionOrderForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Production Order'
    }


class BillOfMaterialsCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 
        'process', 'materials', 'bill_create.html')
    form_class = forms.BillOfMaterialsForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Bill Of Materials'
    }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if self.object is None:
            return resp

        form = self.form_class(request.POST)
       
        if form.is_valid():
            data_string = request.POST['products']
        else:
            return resp

        

        if data_string != "":
            data = json.loads(urllib.parse.unquote(data_string))
            
            for choice in data:
                models.BillOfMaterialsLine.objects.create(
                    bill =self.object,
                    type = 1,
                    product= models.ProcessProduct.objects.get(
                        pk=choice['product'].split('-')[0]),
                    quantity = choice['quantity'],
                    unit=UnitOfMeasure.objects.get(
                        pk=choice['unit'].split('-')[0])
                )
                
        return resp

class ProcessMachineAPIView(ModelViewSet):
    queryset = models.ProcessMachine.objects.all()
    serializer_class = serializers.ProcessMachineSerializer


class ProcessProductAPIView(ModelViewSet):
    queryset = models.ProcessProduct.objects.all()
    serializer_class = serializers.ProcessProductSerializer

class ProcessAPIView(ModelViewSet):
    queryset = models.Process.objects.all()
    serializer_class = serializers.ProcessSerializer