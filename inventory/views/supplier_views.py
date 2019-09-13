# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from common_data.models import GlobalConfig, Individual, Organization
from common_data.utilities import *
from common_data.views import PaginationMixin
from common_data.forms import IndividualForm
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig
import openpyxl
import csv

from .common import CREATE_TEMPLATE


class SupplierCreateView(ContextMixin, FormView):
    form_class = forms.SupplierForm
    template_name = os.path.join('inventory', 'supplier', 'create.html')
    extra_context = {
        "title": "Add Vendor",
        "description": "Record details of business partners that provide your organization with goods and services"
        }

    success_url = '/inventory/supplier/list'

    def get_initial(self):
        return {
            'vendor_type': 'organization'
        }
        

    def form_valid(self, form, *args, **kwargs):
        resp = super().form_valid(form, *args, **kwargs)
        
        if form.cleaned_data['vendor_type'] == "individual":
            names = form.cleaned_data['name'].split(' ')
            individual = Individual.objects.create(
                first_name=" ".join(names[:-1]),# for those with multiple first names
                last_name=names[-1],
                address=form.cleaned_data['address'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone_1'],
                phone_two=form.cleaned_data['phone_2'],
                photo=form.cleaned_data['image'],
                other_details=form.cleaned_data['other_details'],
                organization=form.cleaned_data['organization']
            )
            models.Supplier.objects.create(
                individual=individual,
                billing_address=form.cleaned_data['billing_address'],
                banking_details=form.cleaned_data['banking_details']
            )
        else:
            org = Organization.objects.create(
                legal_name=form.cleaned_data['name'],
                business_address=form.cleaned_data['address'],
                website=form.cleaned_data['website'],
                bp_number=form.cleaned_data['business_partner_number'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone_1'],
                logo=form.cleaned_data['image']
            )
            models.Supplier.objects.create(
                organization=org,
                billing_address=form.cleaned_data['billing_address'],
                banking_details=form.cleaned_data['banking_details']
            )

        return resp


class SupplierUpdateView(ContextMixin, FormView):
    form_class = forms.SupplierForm
    template_name = os.path.join('inventory', 'supplier', 'create.html')
    extra_context = {"title": "Update Existing Vendor"}

    def get_success_url(self):
        return reverse('inventory:supplier-detail', 
            kwargs={'pk': self.kwargs['pk']
        })

    def get_initial(self):
        vendor = models.Supplier.objects.get(pk=self.kwargs['pk'])
        if vendor.is_organization:
            org = vendor.organization
            return {
                'vendor_type': 'organization',
                'name': org.legal_name,
                'address': org.business_address,
                'billing_address': vendor.billing_address,
                'banking_details': vendor.banking_details,
                'email': org.email,
                'phone_1': org.phone,
                'image': org.logo,
                'website': org.website,
                'business_partner_number': org.bp_number
            }
        else:
            ind = vendor.individual
            return {
                'vendor_type': 'individual',
                'name': ind.first_name + " " + ind.last_name,
                'address': ind.address,
                'billing_address': vendor.billing_address,
                'banking_details': vendor.banking_details,
                'email': ind.email,
                'phone_1': ind.phone,
                'phone_2': ind.phone_two,
                'image': ind.photo,
                'other_details': ind.other_details,
                'organization': ind.organization
            }

    def form_valid(self, form):
        resp = super().form_valid(form)
        vendor = models.Supplier.objects.get(pk=self.kwargs['pk'])
        
        vendor.billing_address=form.cleaned_data['billing_address']
        vendor.banking_details=form.cleaned_data['banking_details']
        
        org = None
        individual = None
        
        if vendor.organization and \
                form.cleaned_data['vendor_type'] == "individual":
            vendor.organization.delete()
            org = Organization.objects.create(
                legal_name=form.cleaned_data['name'],
                business_address=form.cleaned_data['address'],
                website=form.cleaned_data['website'],
                bp_number=form.cleaned_data['business_partner_number'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone_1'],
                logo=form.cleaned_data['image']
            )
            vendor.organization = org
            
        
        elif vendor.individual and \
                form.cleaned_data['vendor_type'] == "organization":
            vendor.individual.delete()
            names = form.cleaned_data['name'].split(' ')

            individual = Individual.objects.create(
                first_name=" ".join(names[:-1]),# for those with multiple first names
                last_name=names[-1],
                address=form.cleaned_data['address'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone_1'],
                phone_two=form.cleaned_data['phone_2'],
                photo=form.cleaned_data['image'],
                other_details=form.cleaned_data['other_details'],
                organization=form.cleaned_data['organization']
            )
            vendor.individual = individual
        else:
            #if the vendor type hasn't changed
                
            if form.cleaned_data['vendor_type'] == "individual":
                
                names = form.cleaned_data['name'].split(' ')
                # for those with multiple first names
                individual = vendor.individual
                individual.first_name=" ".join(names[:-1])
                individual.last_name=names[-1]
                individual.address=form.cleaned_data['address']
                individual.email=form.cleaned_data['email']
                individual.phone=form.cleaned_data['phone_1']
                individual.phone_two=form.cleaned_data['phone_2']
                individual.photo=form.cleaned_data['image']
                individual.other_details= form.cleaned_data['other_details']
                individual.organization= form.cleaned_data['organization']

                individual.save()
                vendor.individual = individual

            
            else:
                organization = vendor.organization
                organization.legal_name=form.cleaned_data['name']
                organization.business_address= form.cleaned_data['address']
                organization.website=form.cleaned_data['website']
                organization.bp_number= \
                    form.cleaned_data['business_partner_number']
                organization.email=form.cleaned_data['email']
                organization.phone=form.cleaned_data['phone_1']
                organization.logo=form.cleaned_data['image']
                organization.save()
        
        vendor.save()
        
            

        return resp

class SupplierListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.SupplierFilter
    template_name = os.path.join("inventory", "supplier", "list.html")
    extra_context = {"title": "Vendor List",
                    "new_link": reverse_lazy(
                        "inventory:supplier-create"),
                     "action_list": [
            {
                'label': 'Import Suppliers from Excel',
                'icon': 'file-excel',
                'link': reverse_lazy('inventory:import-suppliers-from-excel')
            },
            {
                'label': 'Create Multiple Suppliers',
                'icon': 'file-alt',
                'link': reverse_lazy('inventory:create-multiple-suppliers')
            },
        ]}

    def get_queryset(self):
        return models.Supplier.objects.all().order_by('pk')



class SupplierDeleteView( 
        DeleteView):
    template_name = os.path.join('common_data', 
        'delete_template.html')
    success_url=reverse_lazy('inventory:organization-supplier-list')
    model = models.Supplier

class SupplierListAPIView(ListAPIView):
    serializer_class = serializers.SupplierSerializer
    queryset = models.Supplier.objects.all()

class SupplierDetailView( 
        DetailView):
    template_name=os.path.join('inventory', 'supplier', 'detail.html')
    model = models.Supplier

class AddSupplierIndividualView(ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = IndividualForm
    success_url = reverse_lazy('inventory:supplier-list')#wont redirect

    extra_context = {
        'title': 'Add member to organization'
    }

    def get_initial(self):
        return {
            'organization': self.kwargs['pk']
        }

class CreateMultipleSuppliersView(FormView):
    template_name = os.path.join('inventory', 'supplier', 
        'create_multiple.html')
    form_class = forms.CreateMultipleSuppliersForm
    success_url=reverse_lazy('inventory:supplier-list')

    def form_valid(self, form):
        resp = super().form_valid(form)
        data = json.loads(urllib.parse.unquote(form.cleaned_data['data']))
        
        settings = SalesConfig.objects.first()
        
        for line in data:
            org = Organization.objects.create(
                    legal_name = line['name'],
                    business_address = line['address'],
                    email = line['email'],
                    phone = line['phone'],
                )
            sup = models.Supplier.objects.create(
                    organization=org
                )
            if line['account_balance']:
                    sup.account.balance = line['account_balance']
                    sup.account.save()

        return resp


class ImportSuppliersView(ContextMixin, FormView):
    extra_context = {
        'title': 'Import Vendors from Excel File'
    }
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.ImportSuppliersForm
    success_url=reverse_lazy('inventory:supplier-list')

    def form_valid(self, form):
        #assumes all suppliers are organizations
        resp = super().form_valid(form)
        def null_buster(arg):
            if not arg:
                return ''
            return arg


        file = form.cleaned_data['file']
        if file.name.endswith('.csv'):
            #process csv 
            pass
        else:
            cols = [
                form.cleaned_data['name'],
                form.cleaned_data['phone'],
                form.cleaned_data['address'],
                form.cleaned_data['email'],
                form.cleaned_data['account_balance'],
            ]
            wb = openpyxl.load_workbook(file.file)
            try:
                ws = wb[form.cleaned_data['sheet_name']]
            except:
                ws = wb.active

        
            for row in ws.iter_rows(min_row=form.cleaned_data['start_row'],
                    max_row = form.cleaned_data['end_row'], 
                    max_col=max(cols)):
                
                org  = Organization.objects.create(
                    legal_name = row[form.cleaned_data['name'] - 1].value,
                    business_address = null_buster(row[
                        form.cleaned_data['address'] - 1].value),
                    email = null_buster(row[
                        form.cleaned_data['email'] - 1].value),
                    phone =null_buster(row[
                        form.cleaned_data['phone'] - 1].value),
                )

                sup = models.Supplier.objects.create(
                    organization=org
                )
                if row[form.cleaned_data['account_balance'] -1].value:
                    sup.account.balance = row[
                        form.cleaned_data['account_balance'] -1].value
                
                    sup.account.save()
                
        return resp