import json
import os
import urllib
import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import (CreateView, 
                                        UpdateView,
                                        FormView)
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet

from common_data.forms import AuthenticateForm
from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin
from inventory.models import Consumable, Equipment, UnitOfMeasure
from services import filters, forms, models, serializers

class EquipmentRequisitionCreateView( CreateView):
    template_name = os.path.join('services', 'requisitions', 'equipment', 
        'create.html')
    form_class = forms.EquipmentRequisitionForm
    success_url = reverse_lazy('services:equipment-requisition-list')

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        equipment = json.loads(urllib.parse.unquote(request.POST['equipment']))
        
        for equ in equipment:
            equ_pk = equ['item'].split('-')[0]
            equ_item = Equipment.objects.get(pk=equ_pk)
            line = models.EquipmentRequisitionLine.objects.create(
                requisition=self.object,
                equipment= equ_item,
                requesting_condition=equ['condition'],
                quantity=equ['quantity']
            )
        return resp


class EquipmentRequisitionAuthorizeView( DetailView):
    template_name = os.path.join('services', 'requisitions', 'equipment',
        'authorize_release.html')
    model = models.EquipmentRequisition

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['authorize_form'] = AuthenticateForm()
        return context

class EquipmentRequisitionListView( ContextMixin, PaginationMixin, FilterView):
    filterset_class = filters.EquipmentRequisitionFilter
    queryset = models.EquipmentRequisition.objects.all().order_by(
        'date').reverse()
    paginate_by = 10
    template_name = os.path.join('services', 'requisitions', 'equipment', 'list.html')

    extra_context = {
        'title': 'List of Equipment Requisitions'
    }

class EquipmentRequisitionAPIView(ModelViewSet):
    pass

def equipment_requisition_authorize(request, pk=None):
    req = get_object_or_404(models.EquipmentRequisition, pk=pk)
    redirect_path = reverse_lazy('services:equipment-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)
            req.authorized_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy('services:equipment-requisition-list'))

    return HttpResponse(request.path)


def equipment_requisition_release(request, pk=None):
    req = get_object_or_404(models.EquipmentRequisition, pk=pk)
    redirect_path = reverse_lazy('services:equipment-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)            
            req.released_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy(
                    'services:equipment-requisition-list'))

    return HttpResponseRedirect(redirect_path)


#################################################
#            Consumable Requisitions            #
#################################################

class ConsumableRequisitionCreateView( CreateView):
    template_name = os.path.join('services', 'requisitions', 'consumables', 
        'create.html')
    form_class = forms.ConsumablesRequisitionForm
    success_url = reverse_lazy('services:consumable-requisition-list')

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        consumables = json.loads(urllib.parse.unquote(request.POST['consumables']))
        
        for con in consumables:
            con_pk = con['item'].split('-')[0]
            con_item = Consumable.objects.get(pk=con_pk)
            unit_pk, _ = con['unit'].split('-')
            unit = UnitOfMeasure.objects.get(pk=unit_pk)
            line = models.ConsumablesRequisitionLine.objects.create(
                requisition=self.object,
                consumable= con_item,
                quantity=con['quantity'],
                unit=unit
            )
        return resp


class ConsumableRequisitionDetailView( DetailView):
    template_name = os.path.join('services', 'requisitions', 'consumables',
        'authorize_release.html')
    model = models.ConsumablesRequisition

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['authorize_form'] = AuthenticateForm()
        return context

class ConsumableRequisitionListView( ContextMixin, PaginationMixin, FilterView):
    filterset_class = filters.ConsumableRequisitionFilter
    queryset = models.ConsumablesRequisition.objects.all().order_by(
        'date').reverse()
    template_name = os.path.join('services', 'requisitions', 'consumables', 'list.html')
    paginate_by = 10

    extra_context = {
        'title': 'List of Consumables Requisitions'
    }

def consumable_requisition_authorize(request, pk=None):
    req = get_object_or_404(models.ConsumablesRequisition, pk=pk)
    redirect_path = reverse_lazy('services:consumable-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)
            req.authorized_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy('services:consumable-requisition-list'))

    return HttpResponse(request.path)


def consumable_requisition_release(request, pk=None):
    req = get_object_or_404(models.ConsumablesRequisition, pk=pk)
    redirect_path = reverse_lazy('services:consumable-requisition-detail', 
        kwargs={
            'pk': pk
            })
    form = AuthenticateForm(request.POST)
    if form.is_valid():
        usr = form.cleaned_data['user']
        authenticated = authenticate(
            username=usr.username, 
            password=form.cleaned_data['password']
            )
        if authenticated:
            if not hasattr(usr, 'employee'):
                return HttpResponseRedirect(redirect_path)            
            req.released_by = usr.employee
            req.save()
            return HttpResponseRedirect(reverse_lazy(
                    'services:consumable-requisition-list'))

    return HttpResponseRedirect(redirect_path)


class EquipmentReturnView( FormView):
    #TODO test
    template_name = os.path.join('services', 'requisitions', 'equipment', 
        'return.html')
    form_class = forms.EquipmentReturnForm
    success_url = "/inventory/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['requisition'] = get_object_or_404(models.EquipmentRequisition, 
            pk=self.kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        #checks for the login
        usr = authenticate(
            username=request.POST['received_by'],
            password=request.POST['password'])
        if not usr or not hasattr(usr, 'employee'):
            messages.info(request, 
                '''The username or password provided were incorrect.''')
            return HttpResponse('/services/equipment/{}'.format(
                self.kwargs['pk']))

        requisition = get_object_or_404(models.EquipmentRequisition, 
            pk=self.kwargs['pk'])

        requisition.received_by = usr.employee
        requisition.returned_date = datetime.datetime.strptime(request.POST['return_date'], "%m/%d/%Y")
        requisition.save()


        #setting line values
        fields = dict(request.POST).keys()

        for field in fields:
            if field.startswith('equipment_returned'):
                line = models.EquipmentRequisitionLine.objects.get(
                    pk=field.split('_')[2]
                )
                line.quantity_returned = request.POST[field]
                line.save()

            elif field.startswith('equipment_condition'):
                line = models.EquipmentRequisitionLine.objects.get(
                    pk=field.split('_')[2]
                )
                line.returned_condition = request.POST[field]
                line.save()
            


        print(dict(request.POST).keys())
        print(dict(request.POST))

        return resp


class EquipmentRequisitionDetailView( DetailView):
    # TODO test
    model = models.EquipmentRequisition
    template_name = os.path.join('services', 'requisitions', 'equipment', 'detail.html') 