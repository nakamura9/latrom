import urllib
import json
import os 
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from manufacturing.views.util import ManufacturingCheckMixin
from common_data.utilities import ContextMixin
from manufacturing import models 
from manufacturing import forms
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet
from manufacturing import serializers
from manufacturing import filters
from common_data.views import PaginationMixin

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class ShiftCreateView(ContextMixin, ManufacturingCheckMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ShiftForm
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Create Shift'
    }

class ShiftUpdateView(ContextMixin, ManufacturingCheckMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ShiftForm
    model = models.Shift
    success_url = '/manufacturing/'
    extra_context = {
        'title': 'Update Shift'
    }


class ShiftListView(ManufacturingCheckMixin, PaginationMixin,FilterView):
    filterset_class = filters.ShiftFilter
    model = models.Shift
    template_name = os.path.join('manufacturing', 'shifts', 'list.html')

class ShiftScheduleListView(ManufacturingCheckMixin, PaginationMixin, 
        FilterView):
    filterset_class = filters.ShiftScheduleFilter
    model = models.ShiftSchedule
    template_name = os.path.join('manufacturing', 'shifts', 'schedule','list.html')

class ShiftScheduleDetailView(ManufacturingCheckMixin, DetailView):
    template_name = os.path.join('manufacturing', 'shifts', 'schedule','detail.html')
    model = models.ShiftSchedule


class ShiftDetailView(ManufacturingCheckMixin, DetailView):
    template_name = os.path.join('manufacturing', 'shifts', 'detail.html')
    model = models.Shift


class ShiftScheduleCreateView(ContextMixin, 
        ManufacturingCheckMixin, 
        CreateView):
    template_name = os.path.join(
        'manufacturing', 'shifts', 'schedule','create.html')
    form_class = forms.ShiftScheduleForm
    success_url = '/manufacturing/'

    extra_context = {
        'title': 'Create Shift Schedule'
    }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if self.object is None:
            return resp

        form = self.form_class(request.POST)
        if form.is_valid():
            data_string = form.cleaned_data['shift_lines']
            data = json.loads(urllib.parse.unquote(data_string))

        else: return resp

        for line in data:
            models.ShiftScheduleLine.objects.create(
                schedule=self.object,
                start_time = line['startTime'],
                end_time = line['endTime'],
                shift = models.Shift.objects.get(
                    pk=line['shift'].split('-')[0]
                ),
                monday=line['monday'],
                tuesday=line['tuesday'],
                wednesday=line['wednesday'],
                thursday=line['thursday'],
                friday=line['friday'],
                saturday=line['saturday'],
                sunday=line['sunday'],
            )

        return resp

class ShiftAPIView(ModelViewSet):
    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer