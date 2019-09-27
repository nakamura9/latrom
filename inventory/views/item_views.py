# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet


from common_data.models import GlobalConfig
from common_data.utilities import *
from common_data.views import PaginationMixin
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig
from services.models import EquipmentRequisition
from inventory.views.dash_plotters import single_item_composition_plot

from .common import CREATE_TEMPLATE
import openpyxl
import csv
from invoicing.models import SalesConfig
from accounting.models import BillLine, Expense, BillPayment, Account

class ProductAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.filter(type=0)
    serializer_class = serializers.InventoryItemSerializer

class ItemsExcludingProducts(ListAPIView):
    queryset = models.InventoryItem.objects.exclude(type=0)
    serializer_class = serializers.InventoryItemSerializer


class ProductDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:product-list')


class ProductUpdateView( ContextMixin, UpdateView):
    form_class = forms.ProductForm
    model = models.InventoryItem
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {"title": "Update Existing Product"}
    
    
class ProductDetailView(ContextMixin, DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", "product", "detail.html")
    
    def get_context_data(self, *args, **kwargs):
        context =super().get_context_data(*args, **kwargs)
        context['graph'] = single_item_composition_plot(
            self.object).render(is_unicode=True)
        return context

class ProductListView( ContextMixin, PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', "product", 'list.html')
    extra_context = {
        'title': 'Product List',
        'search': filters.InventorySearchField(),
        "new_link": reverse_lazy("inventory:product-create"),
        "action_list": [
            {
                'label': 'Order Products',
                'icon': 'file-excel',
                'link': reverse_lazy('inventory:order-create')
            },
            {
                'label': 'Import Items from Excel',
                'icon': 'file-excel',
                'link': reverse_lazy('inventory:import-items-from-excel')
            },
            {
                'label': 'Create Multiple Items',
                'icon': 'file-alt',
                'link': reverse_lazy('inventory:create-multiple-items')
            },
        ]
    }

    def get_queryset(self):
        return models.InventoryItem.objects.filter(type=0, active=True).order_by('pk')


class ProductCreateView( ContextMixin, 
        CreateView):
    form_class = forms.ProductForm
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Product",
        'description': 'Cycle  through the tabs to enter information regarding product description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        },],
        'box_array':  urllib.parse.quote(json.dumps([{
                "model": "supplier",
                "app": "inventory",
                "id": "id_supplier",
            },
            {
                "model": "unitofmeasure",
                "app": "inventory",
                "id": "id_unit",
            },
            {
                "model": "category",
                "app": "inventory",
                "id": "id_category",
            }
            ]))
        }

    def get_initial(self):
        return {
            'tax': 1,
            'type': 0 #for product
        }

################################################
#               Consumable                     #
################################################

class ConsumableAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.filter(type=2)
    serializer_class = serializers.InventoryItemSerializer


class ConsumableUpdateView( ContextMixin,
        UpdateView):
    form_class = forms.ConsumableForm
    model = models.InventoryItem
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {"title": "Update Existing Consumable Inventory"}


class ConsumableDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", 'consumable',"detail.html")


class ConsumableListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', 'consumable','list.html')
    extra_context = {
        'title': 'Consumable List',
        "new_link": reverse_lazy("inventory:consumable-create"),
        "action_list": [
            {
                'label': 'Import Items from Excel',
                'icon': 'file-excel',
                'link': reverse_lazy('inventory:import-items-from-excel')
            },{
                'label': 'Purchase',
                'icon': 'cart-arrow-down',
                'link': reverse_lazy(
                    'inventory:equipment-and-consumables-purchase')
            }
        ]
    }

    def get_queryset(self):
        return models.InventoryItem.objects.filter(type=2, active=True).order_by('pk')


class ConsumableCreateView( ContextMixin, 
        CreateView):
    form_class = forms.ConsumableForm
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Consumable",
        'description': 'Cycle  through the tabs to enter information regarding consumable description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        'box_array':  urllib.parse.quote(json.dumps([{
                "model": "supplier",
                "app": "inventory",
                "id": "id_supplier",
            },
            {
                "model": "unitofmeasure",
                "app": "inventory",
                "id": "id_unit",
            },
            {
                "model": "category",
                "app": "inventory",
                "id": "id_category",
            }
            ]))
        }
    
    def get_initial(self):
        return {
            'type': 2 #for consumables
        }

class ConsumablesPurchaseView(CreateView):
    pass



####################################################
#                   Equipment Views                #
####################################################


class EquipmentAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.filter(type=1)
    serializer_class = serializers.InventoryItemSerializer


class EquipmentUpdateView( ContextMixin, 
        UpdateView):
    form_class = forms.EquipmentForm
    model = models.InventoryItem
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {"title": "Update Existing Equipment Details"}

    def get_initial(self):
        initial = super().get_initial()
        item = models.InventoryItem.objects.get(pk=self.kwargs['pk'])
        if item.equipment_component and item.equipment_component.asset_data:
            asset = item.equipment_component.asset_data
            initial.update({
                'record_as_asset': True,
                'asset_category': asset.category,
                'initial_value': asset.initial_value,
                'date_purchased': asset.init_date,
                'salvage_value': asset.salvage_value,
                'depreciation_period': asset.depreciation_period
            })
        return initial
        
class EquipmentDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", 'equipment', "detail.html")


class EquipmentListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', 'equipment', 'list.html')
    extra_context = {
        'title': 'Equipment List',
        "new_link": reverse_lazy("inventory:equipment-create"),
        "action_list": [
            {
                'label': 'Import Items from Excel',
                'icon': 'file-excel',
                'link': reverse_lazy('inventory:import-items-from-excel')
            }
        ]
    }

    def get_queryset(self):
        return models.InventoryItem.objects.filter(type=1,active=True).order_by('pk')


class EquipmentCreateView( ContextMixin, 
        CreateView):
    form_class = forms.EquipmentForm
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Add New Equipment",
        'description': 'Cycle  through the tabs to enter information regarding equipment description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        'box_array':  urllib.parse.quote(json.dumps([{
                "model": "supplier",
                "app": "inventory",
                "id": "id_supplier",
            },
            {
                "model": "unitofmeasure",
                "app": "inventory",
                "id": "id_unit",
            },
            {
                "model": "category",
                "app": "inventory",
                "id": "id_category",
            }
            ]))
        }

    def get_initial(self):
        return {
            'type': 1# for equipment
        }


class EquipmentandConsumablesPurchaseView(ContextMixin, CreateView):
    """
    Creates a bill
    form includes: date, vendor, account 
    generic table includes: equipment, quantity, """
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.EquipmentandConsumablesPurchaseForm
    extra_context = {
        'title': 'Record Purchase of Equipment and Consumables'
    }

    def form_valid(self, form):
        resp = super().form_valid(form)

        data = json.loads(urllib.parse.unquote(form.cleaned_data['data']))
        warehouse = form.cleaned_data['warehouse']
        for line in data:
            exp = Expense.objects.create(
                debit_account=self.object.vendor.account,
                date=self.object.date,
                description=f"{line['quantity']} x {line['item']} "
                            f"@ ${line['unit_price']}"
                            f"{line['unit'].split('-')[-1]}",
                amount=line['lineTotal'],
                category=7
            )
            BillLine.objects.create(
                bill=self.object,
                expense= exp
            )

            #increment inventory
            item_pk = line['item'].split('-')[0]
            item = models.InventoryItem.objects.get(pk=item_pk)
            warehouse.add_item(item, line['quantity'])

        if form.cleaned_data['paid_in_full']:
            pmt = BillPayment.objects.create(
                date=self.object.date,
                account=Account.objects.get(pk=1000),
                bill=self.object,
                amount=self.object.total,
            )
            pmt.create_entry()


        return resp 

####################################################
#                Raw Material Views                #
####################################################


class RawMaterialAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.all()
    serializer_class = serializers.InventoryItemSerializer


class RawMaterialUpdateView( ContextMixin, 
        UpdateView):
    form_class = forms.ConsumableForm# TODO make a raw material form
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Raw Materials Details"}


class RawMaterialDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", 'raw_material', "detail.html")


class RawMaterialListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', 'raw_material', 'list.html')
    extra_context = {
        'title': 'RawMaterial List',
        "new_link": reverse_lazy("inventory:raw-material-create")
    }

    def get_queryset(self):
        return models.InventoryItem.objects.all().order_by('pk')


class RawMaterialCreateView( ContextMixin, 
        CreateView):
    form_class = forms.ConsumableForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Add New Raw Material",
        'description': 'Cycle  through the tabs to enter information regarding material description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        }


class ImportItemsView(ContextMixin, FormView):
    form_class = forms.ImportItemsForm
    extra_context = {
        'title': 'Import Items from Excel File'
    }
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('inventory:product-list')

    def form_valid(self, form):
        resp = super().form_valid(form)
        file = form.cleaned_data['file']
        if file.name.endswith('.csv'):
            #process csv 
            pass
        else:

            cols = [
                form.cleaned_data['name'],
                form.cleaned_data['purchase_price'],
                form.cleaned_data['sales_price'],
                form.cleaned_data['quantity'],
                form.cleaned_data['type'],
                form.cleaned_data['unit'],
            ]
            wb = openpyxl.load_workbook(file.file)
            try:
                ws = wb[form.cleaned_data['sheet_name']]
            except:
                ws = wb.active

            settings = SalesConfig.objects.first()
            for row in ws.iter_rows(min_row=form.cleaned_data['start_row'],
                    max_row = form.cleaned_data['end_row'], 
                    max_col=max(cols)):


                qs = models.UnitOfMeasure.objects.filter(name=row[
                    form.cleaned_data['unit'] -1].value)
                if qs.exists():
                    unit = qs.first()
                else:
                    unit = models.UnitOfMeasure.objects.create(
                        name=row[form.cleaned_data['unit'] -1].value)
                
                type_mapping = ['product', 'equipment', 'consumable']
                item = models.InventoryItem.objects.create(
                    name=row[form.cleaned_data['name'] - 1].value,
                    description=row[form.cleaned_data['name'] - 1].value,
                    unit=unit,
                    type=type_mapping.index(
                        row[form.cleaned_data['type'] - 1].value),
                    unit_purchase_price=row[
                        form.cleaned_data['purchase_price'] - 1].value
                )
                
                #record quantity
                warehouse = form.cleaned_data['warehouse']
                warehouse.add_item(item, row[
                    form.cleaned_data['quantity']-1].value)
                #handle products equipment components
                if row[form.cleaned_data['type'] -1].value == 0:
                    component =models.ProductComponent.objects.create(
                        pricing_method=0,
                        tax=settings.sales_tax,
                        direct_price=row[
                            form.cleaned_data['sales_price']-1].value
                    )
                    item.product_component=component
                    item.save()
                elif row[form.cleaned_data['type'] -1].value == 1:
                    component = models.EquipmentComponent.objects.create()
                    item.equipment_component = component
                    item.save()


        return resp

class BulkCreateItemsView(ContextMixin, FormView):
    template_name = os.path.join('inventory', 'item', 'create_multiple.html')
    form_class = forms.BulkCreateItemsForm
    success_url = reverse_lazy('inventory:product-list')

    def form_valid(self, form):
        resp = super().form_valid(form)
        data = json.loads(urllib.parse.unquote(form.cleaned_data['data']))
        
        settings = SalesConfig.objects.first()
        
        for line in data:
            item = models.InventoryItem.objects.create(
                    name=line['name'],
                    type=line['type'],
                    description=line['name'],
                    unit_purchase_price=line['purchase_price']
                )
                
            #record quantity
            warehouse = form.cleaned_data['warehouse']
            warehouse.add_item(item, line['quantity'])
            #handle products equipment components
            if line['type']== 0:
                component =models.ProductComponent.objects.create(
                    pricing_method=0,
                    tax=settings.sales_tax,

                    direct_price=line['sales_price']
                )
                item.product_component=component
                item.save()
            elif line['type'] == 1:
                component = models.EquipmentComponent.objects.create()
                item.equipment_component = component
                item.save()
        
        return resp
