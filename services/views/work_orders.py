import json
import os
import urllib
import datetime 
from functools import reduce

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet
from django.contrib import messages

from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin
from services import filters, forms, models, serializers
from accounting.forms import ExpenseForm
from accounting.models import Expense
from employees.models import Employee
from decimal import Decimal as D

class WorkOrderCRUDMixin(object):
    def post(self, request, *args, **kwargs):
        update_flag = isinstance(self, UpdateView)
        resp = super(WorkOrderCRUDMixin, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        service_people = json.loads(urllib.parse.unquote(
            request.POST['service_people']))
        
        if update_flag and service_people != "":
            self.object.service_people.clear()

        for sp in service_people:
            elements = sp.split('-')
            service_person = models.ServicePerson.objects.get(pk=elements[0])
            self.object.service_people.add(service_person)

        return resp



class WorkOrderCreateView( WorkOrderCRUDMixin, ContextMixin,
        CreateView):
    template_name = os.path.join('services', 'work_order', 'create.html')
    form_class = forms.ServiceWorkOrderForm
    extra_context = {
        'related_links': [
            {
                'name': 'Add Service Team',
                'url': '/services/team-create/'
            }
        ]
    }
    def get_initial(self):
        return {
            'status': 'requested',
            'works_request': self.kwargs['pk']
        }

    
class WorkOrderUpdateView( WorkOrderCRUDMixin, UpdateView):
    template_name = os.path.join('services', 'work_order', 'update.html')
    form_class = forms.ServiceWorkOrderForm
    model = models.ServiceWorkOrder


class WorkOrderCompleteView(UpdateView):
    template_name = os.path.join('services', 'work_order', 'complete.html')
    form_class = forms.ServiceWorkOrderCompleteForm
    model = models.ServiceWorkOrder

    def get(self, *args, **kwargs):
        if not hasattr(self, 'object'):
            obj = self.get_object()
        obj.status = 'progress'
        obj.save()
        
        return super().get(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)

        if not self.object:
            self.get_object()

        
        
        log_data = json.loads(urllib.parse.unquote(request.POST['service_time'])) if request.POST['service_time'] != '' else []

        for log in log_data:
            pk = log['employee'].split('-')[0]
            employee = Employee.objects.get(pk=pk)
            date= datetime.datetime.strptime(
                log['date'], "%Y-%m-%d")
            normal_time = datetime.datetime.strptime(
                log['normal_time'], "%H:%M")
            normal_time = datetime.timedelta(
                hours=normal_time.hour, minutes=normal_time.minute)
            
            overtime = datetime.datetime.strptime(log['overtime'], "%H:%M")
            overtime = datetime.timedelta(
                hours=overtime.hour, minutes=overtime.minute)
            

            models.TimeLog.objects.create(
                work_order=self.object,
                date=date,
                employee=employee,
                normal_time=normal_time,
                overtime=overtime,
            )

        # get the progress
        if request.POST.get('steps[]', None):
            steps = request.POST.getlist('steps[]')
            self.object.progress = ",".join(steps)
            self.object.save()
        else:
            self.object.progress = ""
            self.object.save()

        return resp 


class WorkOrderDetailView( DetailView):
    template_name = os.path.join('services', 'work_order', 'detail.html')
    model = models.ServiceWorkOrder

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['authorization_form'] = \
            forms.ServiceWorkOrderAuthorizationForm(initial={
                'order': self.object.pk
            })

        return context
class WorkOrderListView( ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('services', 'work_order', 'list.html')
    filterset_class = filters.WorkOrderFilter
    queryset = models.ServiceWorkOrder.objects.all().order_by('date').reverse()
    extra_context = {
        'title': 'List of Work Orders'
            }


class WorkOrderViewSet(ModelViewSet):
    serializer_class = serializers.WorkOrderSerializer
    queryset = models.ServiceWorkOrder.objects.all()


def work_order_authorize(request, pk=None):
    worder = get_object_or_404(models.ServiceWorkOrder, pk=pk)
    form = forms.ServiceWorkOrderAuthorizationForm(request.POST)
    if form.is_valid():
        worder.status = form.cleaned_data['status']
        worder.authorized_by = form.cleaned_data['authorized_by']
        worder.save()
    else: 
        pk = request.path.split("/")[-1]
        messages.info(request, "The authorization password is incorrect")
        return HttpResponseRedirect("/services/work-order-detail/{}".format(pk))
    return HttpResponseRedirect(reverse_lazy('services:work-order-list'))


class WorkOrderRequestListView(ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('services', 'work_order', 'request', 
        'list.html')
    queryset = models.WorkOrderRequest.objects.all()
    paginate_by = 20
    filterset_class = filters.WorkOrderRequestFilters
    extra_context= {
        'title': 'Work Order Requests',
        'description': 'Work Order Requests are requests generated by the system whenever a service invoice is created. These are fulfilled by work orders that track the execution of a service ',
        'new_link': '/services/work-order/request/create/'
    }

class WorkOrderRequestCreateView(ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'create_template.html')
    model = models.WorkOrderRequest
    form_class = forms.WorkOrderRequestForm
    extra_context = {
        'title': 'Create Work Order Request'
    }
    

class WorkOrderRequestDetailView(DetailView):
    template_name = os.path.join("services", "work_order", "request", 
        "detail.html")

    model = models.WorkOrderRequest

class WorkOrderExpenseCreateView(ContextMixin, CreateView):
    template_name = os.path.join("common_data", "crispy_create_template.html")
    form_class = ExpenseForm
    model = Expense
    extra_context = {
        'title': 'Record Work Order Expense'
    }
    def get_success_url(self):
        #TODO fix
        '''pk = models.WorkOrderExpense.objects.latest('pk').pk
        if pk:
            return reverse_lazy('services:work-order-costing', kwargs={'pk': pk})'''
        return reverse_lazy('services:work-order-list')

    def post(self, *args, **kwargs):
        resp = super().post(*args, **kwargs)

        if not self.object:
            return resp
        work_order = models.ServiceWorkOrder.objects.get(pk=self.kwargs['pk'])
        
        models.WorkOrderExpense.objects.create(
            expense=self.object,
            work_order=work_order
        )

        return resp 


