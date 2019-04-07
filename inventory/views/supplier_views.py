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

from common_data.models import GlobalConfig, Individual, Organization
from common_data.utilities import *
from common_data.views import PaginationMixin
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig

from .common import CREATE_TEMPLATE


class SupplierCreateView(ContextMixin, FormView):
    form_class = forms.SupplierForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join('inventory', 'supplier', 'create.html')
    extra_context = {"title": "Add Vendor"}

    def get_initial(self):
        return {
            'vendor_type': 'individual'
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
    success_url = reverse_lazy('inventory:home')
    extra_context = {"title": "Update Existing Vendor"}

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
                organization.legal_name=form.cleaned_data['name'],
                organization.business_address= form.cleaned_data['address'],
                organization.website=form.cleaned_data['website'],
                organization.bp_number= \
                    form.cleaned_data['business_partner_number'],
                organization.email=form.cleaned_data['email'],
                organization.phone=form.cleaned_data['phone_1'],
                organization.logo=form.cleaned_data['image']
                organization.save()
        
        vendor.save()
        
            

        return resp

class SupplierListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.SupplierFilter
    template_name = os.path.join("inventory", "supplier", "list.html")
    extra_context = {"title": "Vendor List",
                    "new_link": reverse_lazy(
                        "inventory:supplier-create")}

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