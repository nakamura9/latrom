# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import (CreateView, 
                                        DeleteView, 
                                        UpdateView, 
                                        FormView)
from django_filters.views import FilterView
from rest_framework import viewsets

from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin
from common_data.forms import IndividualForm
from invoicing import filters, forms, serializers
from invoicing.models import Customer, Invoice, CreditNote
from common_data.models import Individual, Organization
import openpyxl
import csv
import json
import urllib


#########################################
#           Customer Views              #
#########################################

class CustomerAPIViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

#No customer list, overlooked!

class CustomerCreateView( ContextMixin, 
        FormView):
    extra_context = {
        "title": "New  Customer",
        'description': 'Add individuals and organizations that buy your' 
        ' products to your records',

        }
    template_name = os.path.join("invoicing", "customer", "create.html")
    form_class = forms.CustomerForm

    def get_success_url(self):
        return reverse_lazy('invoicing:customer-details', kwargs={
            'pk': Customer.objects.latest('pk').pk + 1
        })

    def get_initial(self):
        return {
            'customer_type': 'individual'
        }

    def form_valid(self, form, *args, **kwargs):
        resp = super().form_valid(form, *args, **kwargs)
        
        if form.cleaned_data['customer_type'] == "individual":
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
            Customer.objects.create(
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
            Customer.objects.create(
                organization=org,
                billing_address=form.cleaned_data['billing_address'],
                banking_details=form.cleaned_data['banking_details']
            )

        return resp

class CustomerUpdateView( ContextMixin, FormView):
    extra_context = {"title": "Update Existing Customer"}
    template_name = os.path.join("invoicing", "customer", "create.html")
    form_class = forms.CustomerForm


    def get_success_url(self):
        return reverse_lazy('invoicing:customer-details', kwargs={
            'pk': self.kwargs['pk']
            })

    def get_initial(self):
        customer = Customer.objects.get(pk=self.kwargs['pk'])
        if customer.is_organization:
            org = customer.organization
            return {
                'customer_type': 'organization',
                'name': org.legal_name,
                'address': org.business_address,
                'billing_address': customer.billing_address,
                'banking_details': customer.banking_details,
                'email': org.email,
                'phone_1': org.phone,
                'image': org.logo,
                'website': org.website,
                'business_partner_number': org.bp_number
            }
        else:
            ind = customer.individual
            return {
                'customer_type': 'individual',
                'name': ind.first_name + " " + ind.last_name,
                'address': ind.address,
                'billing_address': customer.billing_address,
                'banking_details': customer.banking_details,
                'email': ind.email,
                'phone_1': ind.phone,
                'phone_2': ind.phone_two,
                'image': ind.photo,
                'other_details': ind.other_details,
                'organization': ind.organization
            }

    def form_valid(self, form):
        resp = super().form_valid(form)
        customer = Customer.objects.get(pk=self.kwargs['pk'])
        
        customer.billing_address=form.cleaned_data['billing_address']
        customer.banking_details=form.cleaned_data['banking_details']
        
        org = None
        individual = None
        
        if customer.organization and \
                form.cleaned_data['customer_type'] == "individual":
            customer.organization.delete()
            org = Organization.objects.create(
                legal_name=form.cleaned_data['name'],
                business_address=form.cleaned_data['address'],
                website=form.cleaned_data['website'],
                bp_number=form.cleaned_data['business_partner_number'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone_1'],
                logo=form.cleaned_data['image']
            )
            customer.organization = org
            
        
        elif customer.individual and \
                form.cleaned_data['customer_type'] == "organization":
            customer.individual.delete()
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
            customer.individual = individual
        else:
            #if the customer type hasn't changed
                
            if form.cleaned_data['customer_type'] == "individual":
                
                names = form.cleaned_data['name'].split(' ')
                # for those with multiple first names
                individual = customer.individual
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
                customer.individual = individual

            
            else:
                organization = customer.organization
                organization.legal_name=form.cleaned_data['name']
                organization.business_address= form.cleaned_data['address']
                organization.website=form.cleaned_data['website']
                organization.bp_number= \
                    form.cleaned_data['business_partner_number']
                organization.email=form.cleaned_data['email']
                organization.phone=form.cleaned_data['phone_1']
                organization.logo=form.cleaned_data['image']
                organization.save()
        
        customer.save()
        
            

        return resp


class CustomerListView( ContextMixin, PaginationMixin, FilterView):
    extra_context = {"title": "List of Customers",
                    "new_link": reverse_lazy(
                        "invoicing:create-customer"),
                    "action_list": [
                            {
                                'label': 'Import Customers from Excel',
                                'icon': 'file-excel',
                                'link': reverse_lazy('invoicing:import-customers-from-excel')
                            },
                            {
                                'label': 'Create Multiple Customers',
                                'icon': 'file-alt',
                                'link': reverse_lazy('invoicing:create-multiple-customers')
                            },
                        ]
                    }
    template_name = os.path.join("invoicing", "customer", "list.html")
    filterset_class = filters.CustomerFilter
    paginate_by = 20

    def get_queryset(self):
        return Customer.objects.all().order_by('pk')


class CustomerDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = Customer
    success_url = reverse_lazy('invoicing:customers-list')

class CustomerDetailView(DetailView):
    template_name = os.path.join('invoicing', 'customer', 'detail.html')
    model = Customer

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'invoices': Invoice.objects.filter(
                customer=self.object,
                status='invoice'),
            'quotations': Invoice.objects.filter(
                customer=self.object,
                status='quotation'),
            'credit_notes': CreditNote.objects.filter(
                invoice__customer=self.object
            )
        })

        return context 

#TODO test
class AddCustomerIndividualView(ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = IndividualForm
    success_url = reverse_lazy('invoicing:customers-list')#wont redirect

    extra_context = {
        'title': 'Add member to organization'
    }

    def get_initial(self):
        return {
            'organization': self.kwargs['pk']
        }

class RemoveCustomerIndividualView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')


class CreateMultipleCustomersView(FormView):
    template_name = os.path.join('invoicing', 'customer', 
        'create_multiple.html')
    form_class = forms.CreateMultipleCustomersForm
    success_url=reverse_lazy('invoicing:customers-list')

    def form_valid(self, form):
        resp = super().form_valid(form)
        data = json.loads(urllib.parse.unquote(form.cleaned_data['data']))
        def null_buster(arg):
            if not arg:
                return ''
            return arg

        for line in data:
            cus = None
            if line['type'] == 'organization':
                org = Organization.objects.create(
                    legal_name = line['name'],
                    business_address = null_buster(line['address']),
                    email = null_buster(line['email']),
                    phone = null_buster(line['phone']),
                )
                cus =Customer.objects.create(
                    organization=org
                )
            else:
                names = line['name'].split(' ')
                ind = Individual.objects.create(
                    first_name=" ".join(names[:-1]),# for those with multiple first names
                    last_name=names[-1],
                    address=null_buster(line['address']),
                    email=null_buster(line['email']),
                    phone=null_buster(line['phone']),
                )

                cus = Customer.objects.create(
                    individual=ind
                )

            
            
            if line['account_balance']:
                    cus.account.balance = line['account_balance']
                    cus.account.save()

        return resp


class ImportCustomersView(ContextMixin, FormView):
    extra_context = {
        'title': 'Import Customers from Excel File'
    }
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.ImportCustomersForm
    success_url=reverse_lazy('invoicing:customers-list')

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
                form.cleaned_data['type'],
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
                cus = None
                if row[form.cleaned_data['type']-1].value == 0:
                    org = Organization.objects.create(
                        legal_name = row[form.cleaned_data['name']-1].value,
                        business_address = null_buster(row[form.cleaned_data['address']-1].value),
                        email = null_buster(row[form.cleaned_data['email']-1].value),
                        phone = null_buster(row[form.cleaned_data['phone']-1].value),
                    )
                    cus = Customer.objects.create(
                        organization=org
                    )
                else:
                    names = row[form.cleaned_data['name']-1].value.split(' ')
                    ind = Individual.objects.create(
                        first_name=" ".join(names[:-1]),# for those with multiple first names
                        last_name=names[-1],
                        address=null_buster(row[form.cleaned_data['address']-1].value),
                        email=null_buster(row[form.cleaned_data['email']-1].value),
                        phone=null_buster(row[form.cleaned_data['phone']-1].value),
                    )

                    cus = Customer.objects.create(
                        individual=ind
                    )
                    
                    
                    if row[form.cleaned_data['account_balance'] -1].value:
                        cus.account.balance = row[
                            form.cleaned_data['account_balance'] -1].value
                    
                        cus.account.save()
                
        return resp