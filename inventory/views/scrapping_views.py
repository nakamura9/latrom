import os
import json 
import urllib

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from inventory import forms
from inventory import models
from common_data.utilities import ExtraContext, ConfigMixin
from invoicing.models import SalesConfig


class ScrappingRecordCreateView(CreateView):
    template_name = os.path.join('inventory', 'scrapping', 'create.html')
    form_class = forms.ScrappingRecordForm
    success_url = reverse_lazy('inventory:warehouse-list')

    def get_initial(self):
        return {
            'warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(ScrappingRecordCreateView, self).post(
            request, *args, **kwargs)
        if not self.object:
            return resp
        
        raw_data = request.POST['items']
        item_list = json.loads(urllib.parse.unquote(raw_data))

        for line in item_list:
            item = models.Product.objects.get(pk=line['pk'])
            models.InventoryScrappingRecordLine.objects.create(
                product=item,
                scrapping_record = self.object,
                quantity=line['quantity'],
                note= line['note']
            )
        
        return resp

class ScrappingReportListView(ExtraContext, ListView):
    template_name = os.path.join('inventory', 'scrapping', 'list.html')
    extra_context = {
        'title': 'Scrapping History for Warehouse'
    }
    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.InventoryScrappingRecord.objects.filter(
            warehouse=warehouse).order_by('date')

    

class ScrappingReportDetailView(ExtraContext, ConfigMixin, DetailView):
    template_name = os.path.join('inventory', 'scrapping', 'detail.html')
    model = models.InventoryScrappingRecord
    extra_context = {
        'title': 'Inventory Scrapping Report'
    }