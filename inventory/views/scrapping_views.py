import json
import os
import urllib

from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from common_data.utilities import ConfigMixin, ContextMixin
from inventory import forms, models
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
            pk = line['item'].split('-')[0]
            item = models.InventoryItem.objects.get(pk=pk)
            models.InventoryScrappingRecordLine.objects.create(
                item=item,
                scrapping_record = self.object,
                quantity=line['quantity'],
                note= line['note']
            )
        
        self.object.scrap()
        return resp

class ScrappingReportListView(ContextMixin, ListView):
    template_name = os.path.join('inventory', 'scrapping', 'list.html')
    extra_context = {
        'title': 'Scrapping History for Warehouse'
    }
    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.InventoryScrappingRecord.objects.filter(
            warehouse=warehouse).order_by('date')

    

class ScrappingReportDetailView(ContextMixin, ConfigMixin, DetailView):
    template_name = os.path.join('inventory', 'scrapping', 'detail.html')
    model = models.InventoryScrappingRecord
    extra_context = {
        'title': 'Inventory Scrapping Report'
    }
