import datetime
import decimal
import json
import os
import urllib


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets

from accounting.models import Tax
from common_data.utilities import ContextMixin, apply_style
from common_data.views import PaginationMixin

from employees import filters, forms, models, serializers

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


class TimeSheetMixin(object):
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        update_flag = isinstance(self, UpdateView)
        
        def get_time(time_string):
            if '.' in time_string:
                time_string = time_string.split('.')[0] # removes seconds component
            try:
                return datetime.datetime.strptime(time_string, '%H:%M').time()
            except:
                return datetime.datetime.strptime(time_string, '%H:%M:%S').time()
                
        def get_duration(time_string):
            try:
                hr, min = time_string.split(":")
            except:
                hr, min, sec = time_string.split(":")
            return datetime.timedelta(hours=int(hr), minutes=int(min))

        if not self.object:
            return resp

        raw_data = request.POST['lines']
        line_data = json.loads(urllib.parse.unquote(raw_data))

        if update_flag and len(line_data) > 0:
            for i in self.object.attendanceline_set.all():
                i.delete()

        
        for line in line_data:
            if '-' in line['date']:
                date = datetime.datetime.strptime(
                    line['date'], '%Y-%m-%d')
            else:
                date =datetime.date(
                        self.object.year, 
                        self.object.month,
                        int(line['date']))
            
            models.AttendanceLine.objects.create(
                timesheet=self.object,
                date=date,
                time_in=get_time(line['timeIn']),
                time_out= get_time(line['timeOut']),
                lunch_duration=get_duration(line['breaksTaken']))
        
        return resp

class CreateTimeSheetView( TimeSheetMixin, CreateView):
    template_name = os.path.join('employees', 'timesheet', 'create_update.html')
    form_class = forms.TimesheetForm

class ListTimeSheetView(ContextMixin,  PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'timesheet','list.html')
    filterset_class = filters.TimeSheetFilter
    paginate_by = 20
    extra_context ={
        'title': 'Time Sheets',
        'new_link': reverse_lazy('employees:timesheet-create')
    }
    def get_queryset(self):
        
        return models.EmployeeTimeSheet.objects.all().order_by('pk').reverse()
    

class TimeSheetDetailView( DetailView):
    model = models.EmployeeTimeSheet
    template_name = os.path.join('employees', 'timesheet','detail.html')

class TimeSheetUpdateView(TimeSheetMixin,  UpdateView):
    template_name = os.path.join('employees', 'timesheet','create_update.html')
    form_class = forms.TimesheetForm
    queryset = models.EmployeeTimeSheet.objects.all()

class TimeSheetViewset(viewsets.ModelViewSet):
    queryset = models.EmployeeTimeSheet.objects.all()
    serializer_class = serializers.TimeSheetSerializer

class TimeLoggerView(ContextMixin, FormView):
    template_name = CREATE_TEMPLATE#os.path.join('employees', 'timesheet', 'logger.html')
    extra_context = {
        'title': 'Log Time In/Out',
        'icon': 'hourglass-half'
    }
    form_class = forms.TimeLoggerForm
    success_url = reverse_lazy('employees:time-logger')

    def form_valid(self, form):
        resp = super().form_valid(form)
        in_out = form.cleaned_data['in_out']
        employee = models.Employee.objects.get(
            pk=form.cleaned_data['employee_number'])
        messages.info(
            self.request, 
            f"{employee} logged {in_out} " 
            f"successfully at {datetime.datetime.now().time()}")
        
        return resp


class TimeLoggerWithEmployeeView(ContextMixin, FormView):
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title': 'Log Time In/Out',
        'icon': 'hourglass-half'
    }
    form_class = forms.TimeLoggerFormWithEmployee
    
    def get_success_url(self):
        return f"/employees/time-logger-success/{self.kwargs['pk']}"

    def get_initial(self):
        employee = models.Employee.objects.get(pk=self.kwargs['pk'])
        return {
            'employee_number': employee.employee_number
        }

class TimeLoggerSuccessView(TemplateView):
    template_name = os.path.join('employees', 'portal', 'timesheet_success.html')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        employee = models.Employee.objects.get(pk=self.kwargs['pk'])
        context['name']  = employee.full_name
        context['time'] = datetime.datetime.now().time().strftime('%H:%M:%S')

        return context
