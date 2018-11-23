import json
import os
import urllib

from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet

from common_data.utilities import ExtraContext
from common_data.views import PaginationMixin
from inventory.models import Consumable, Equipment
from services import filters, forms, models
from services.serializers import ProcedureSerializer
from services.views.util import ServiceCheckMixin


class ProcedureCRUDMixin(object):
    def post(self, request, *args, **kwargs):
        update_flag = isinstance(self, UpdateView)
        resp = super(ProcedureCRUDMixin, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        #for updates remove all relations first
        #might need to back them up first
        if update_flag:
            self.object.required_equipment.clear()
            self.object.required_consumables.clear()
            for t in self.object.task_set.all():
                t.delete()

        #tasks 
        steps = json.loads(urllib.parse.unquote(request.POST['tasks']))
        for task in steps:
            models.Task.objects.create(
                procedure=self.object,
                description=task    
            )
        #equipment 
        equipment = json.loads(urllib.parse.unquote(request.POST['equipment']))
        for item in equipment:
            pk = item['value'].split('-')[0]
            self.object.required_equipment.add(Equipment.objects.get(pk=pk))

        #consumables
        consumables = json.loads(urllib.parse.unquote(request.POST['consumables']))
        for item in consumables:
            pk = item['value'].split('-')[0]
            self.object.required_consumables.add(Consumable.objects.get(pk=pk))


        return resp

class ProcedureCreateView(ServiceCheckMixin, ProcedureCRUDMixin, ExtraContext, 
        CreateView):
    form_class = forms.ServiceProcedureForm
    template_name = os.path.join('services', 'procedure', 'create.html')
    success_url = reverse_lazy('services:list-procedures')
    extra_context = {
        'related_links': [
            {
                'name': 'Add Equipment',
                'url': '/inventory/equipment-create/'
            },
            {
                'name': 'Add Consumable',
                'url': '/inventory/consumable-create/'
            }
        ]
    }

class ProcedureUpdateView(ServiceCheckMixin, ProcedureCRUDMixin, UpdateView):
    form_class = forms.ServiceProcedureForm
    template_name = os.path.join('services', 'procedure', 'update.html')
    success_url = reverse_lazy('services:list-procedures')
    model = models.ServiceProcedure

class ProcedureDetailView(ServiceCheckMixin, DetailView):
    template_name = os.path.join('services', 'procedure', 'detail.html')
    model = models.ServiceProcedure

class ProcedureListView(ServiceCheckMixin, ExtraContext, PaginationMixin, FilterView):
    template_name = os.path.join('services', 'procedure', 'list.html')
    filterset_class = filters.ProcedureFilter
    model = models.ServiceProcedure
    extra_context = {
        'title': 'List of Procedures',
        'new_link': reverse_lazy('services:create-procedure')
    }

class ProcedureAPIView(ModelViewSet):
    serializer_class = ProcedureSerializer
    queryset = models.ServiceProcedure.objects.all()
