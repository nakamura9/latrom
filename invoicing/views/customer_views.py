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
from invoicing import filters, forms, serializers
from invoicing.models import Customer
from common_data.models import Individual, Organization


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
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.CustomerForm

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
    success_url = reverse_lazy("invoicing:home")

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
                organization.legal_name=form.cleaned_data['name'],
                organization.business_address= form.cleaned_data['address'],
                organization.website=form.cleaned_data['website'],
                organization.bp_number= \
                    form.cleaned_data['business_partner_number'],
                organization.email=form.cleaned_data['email'],
                organization.phone=form.cleaned_data['phone_1'],
                organization.logo=form.cleaned_data['image']
                organization.save()
        
        customer.save()
        
            

        return resp



class CustomerListView( ContextMixin, PaginationMixin, FilterView):
    extra_context = {"title": "List of Customers",
                    "new_link": reverse_lazy(
                        "invoicing:create-customer")}
    template_name = os.path.join("invoicing", "customer", "list.html")
    filterset_class = filters.CustomerFilter
    paginate_by = 10

    def get_queryset(self):
        return Customer.objects.all().order_by('pk')


class CustomerDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = Customer
    success_url = reverse_lazy('invoicing:customers-list')

class CustomerDetailView(DetailView):
    template_name = os.path.join('invoicing', 'customer', 'detail.html')
    model = Customer