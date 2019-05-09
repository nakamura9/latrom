
import os

from django.views.generic.edit import CreateView, FormView

from django.urls import reverse
from common_data.utilities import ContextMixin
from django.views.generic import TemplateView, DetailView
from employees import forms
from employees import models
from django_filters.views import FilterView
from common_data.views import PaginationMixin
from employees.filters import LeaveRequestFilter
from django.db.models import Q
import datetime
from django.http import JsonResponse


class LeaveCalendarView( TemplateView):
    template_name = os.path.join('employees', 'leave', 'calendar.html')

class LeaveRequestList( ContextMixin, 
        PaginationMixin, FilterView):
    filterset_class = LeaveRequestFilter
    queryset = models.Leave.objects.all()
    template_name = os.path.join('employees', 'leave', 'list.html')
    extra_context = {
        'title': 'List of Vaction Applications',
        'new_link': '/employees/leave-request'
    }
class LeaveDayRequestView(ContextMixin,  CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.LeaveRequestForm
    extra_context = {
        'title': 'Vacation Application Form',
        'description': 'Use this form to apply for vacation or to request leave of absence for the reasons under the category list.'
    }
    

class LeaveDayDetailView( DetailView):
    template_name = os.path.join('employees', 'leave', 'detail.html')
    model = models.Leave

class LeaveAuthorizationView( ContextMixin, FormView):
    form_class = forms.LeaveAuthorizationForm
    template_name = os.path.join('common_data', 'create_template.html')
    extra_context = {
        'title': 'Authorize Leave Request'
    }

    def get_success_url(self):
        return reverse('employees:leave-detail', kwargs={
            'pk': self.kwargs['pk']
            })

    def get_initial(self):
        return {
            'leave_request': self.kwargs['pk']
        }

    def form_valid(self, cleaned_data):
        resp = super().form_valid(cleaned_data)
        leave_obj = models.Leave.objects.get(
            pk=cleaned_data['leave_request'].value())
        leave_obj.status = cleaned_data['status'].value()
        leave_obj.notes = cleaned_data['notes'].value()
        authorizer = models.Employee.objects.get(
            pk=cleaned_data['authorized_by'].value()
        )
        leave_obj.authorized_by = authorizer
        leave_obj.save()

        return resp

def _month_data(year, month):
    year = int(year)
    month = int(month)
    lower_limit = datetime.date(year=year, month=month, day=1)
    if not month == 12:     
        upper_limit = datetime.date(year=year, month=month + 1, day=1)
    else:
        upper_limit = datetime.date(year=year + 1, month=1, day=1)

    leave_data = models.Leave.objects.filter(
        Q(start_date__gte=lower_limit) &
        Q(start_date__lt = upper_limit) &
        Q(status = 1))
        #design method for spanning multiple months


    def data_dict(d):
        return ({
        'start_date': d.start_date.day, 
        'end_date': d.end_date.day, 
        'employee': d.employee.full_name,
        'id': d.pk
    })

    return [data_dict(d) for d in leave_data]

def get_month_data(request, year=None, month=None):
    lower_limit = datetime.date(year=int(year), month=int(month), day=1)
    
    leave_data = _month_data(year, month)
    data = {
        'leave': leave_data ,
        'title': lower_limit.strftime("%B, %Y")    
    }

    return JsonResponse(data)

def get_year_data(request, year=None):
    leave_data = []
    for i in range(12):
        leave_data.append(_month_data(year, (i+1)))
    data = {
        'leave': leave_data
    
    }
    return JsonResponse(data)