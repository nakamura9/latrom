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

class ProcessCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 'process', 'create.html')
    form_class = forms.ProcessForm
    success_url = '/manufacturing/'
    
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        material_data =json.loads(
            urllib.parse.unquote(
                request.POST['materials'])) if request.POST['materials'] != "" else []
        equipment_data = json.loads(
            urllib.parse.unquote(
                request.POST['equipment'])) if request.POST['equipment'] != "" else []
        products_data = json.loads(
            urllib.parse.unquote(
                request.POST['products'])) if request.POST['products'] != "" else []

        #materials
        if len(material_data) > 0:
            bill = models.BillOfMaterials.objects.create(
                name=str(self.object.id),
                description=('Bill of materials for: ' + str(self.object.pk)),
            )
            for material in material_data:
                material_obj = RawMaterial.objects.get(
                    pk=material['raw material'].split('-')[0])
                unit = UnitOfMeasure.objects.get(
                    pk=material['unit'].split('-')[0])
                models.BillOfMaterialsLine.objects.create(
                    bill=bill,
                    type=0,
                    raw_material = material_obj,
                    unit = unit,
                    quantity =0.0
                )
            self.object.bill_of_materials = bill
            self.object.save()

        #equipment
        if len(equipment_data) > 0:
            mg = models.ProcessMachineGroup.objects.create(
                name="MachineGroup_" + str(self.object.pk),
                description="Machines required for process: " + str(self.object.pk),
            )
            for pe_id in process_equipment:
                pe = models.ProcessMachine.objects.get(
                    pk=pe_id.split('-')[0]
                )
                pe.machine_group = mg
                pe.save()

            self.object.process_equipment = mg
            self.object.save()

            
        #process products
        if len(products_data) > 0:
            pl = models.ProductList.objects.create(
                name="Process Product List " + str(self.object.pk),
                description="List of output products for process " + str(self.object.pk),
            )
            for pp in products_data:
                pp_obj = models.ProcessProduct.objects.get(
                    pk=pp['process product'].split('-')[0]
                )
                pp_obj.product_list = pl
                pp_obj.save()
                
            self.object.product_list = pl
            self.object.save()

        # for process with process rates?
        # how to select existing ones?
        if self.object.type == 0:
            pr = models.ProcessRate.objects.create(
                unit=UnitOfMeasure.objects.get(
                    pk=request.POST['process_rate_unit'].split('-')[0]),
                unit_time=request.POST['process_rate_unit_time']
            )

            self.object.rate = pr
            self.object.save()


        return resp


class ProcessUpdateView(UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessUpdateForm
    queryset = models.Process.objects.all()
    success_url = "/manufacturing/"


class ProcessDetailView(DetailView):
    template_name = os.path.join('manufacturing', 'process', 'detail.html')
    model = models.Process

class ProcessDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Process
    success_url = "/manufacturing/"

class ProcessListView(ManufacturingCheckMixin, PaginationMixin, FilterView):
    filterset_class = filters.ProcessFilter
    model = models.Process
    template_name = os.path.join('manufacturing', 'process', 'list.html')



class ProcessProductCreateView(ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ProcessProductForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Process Product'
    }

class ProcessProductListView(ManufacturingCheckMixin, PaginationMixin,
        FilterView):
    template_name = os.path.join('manufacturing', 'process', 'product', 
        'list.html')
    queryset = models.ProcessProduct.objects.all()
    filterset_class = filters.ProcessProductFilter
    extra_context = {
        'title': 'Create Process Product'
    }

class ProcessProductListCreateView(ManufacturingCheckMixin, CreateView):
    template_name = os.path.join('manufacturing', 'process','product', 'list', 'create.html')
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

class ProductionOrderListView(ManufacturingCheckMixin, PaginationMixin, 
        FilterView):
    template_name = os.path.join('manufacturing', 'process', 'order', 
        'list.html')
    queryset = models.ProductionOrder.objects.all()
    filterset_class = filters.ProductionOrderFilter
    extra_context = {
        'title': 'Production Order List'
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



class ProcessProductAPIView(ModelViewSet):
    queryset = models.ProcessProduct.objects.all()
    serializer_class = serializers.ProcessProductSerializer

class ProcessAPIView(ModelViewSet):
    queryset = models.Process.objects.all()
    serializer_class = serializers.ProcessSerializer