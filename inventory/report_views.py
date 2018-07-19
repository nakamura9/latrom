import datetime
import os 

from django.views.generic import TemplateView

import models 

class InventoryReport(TemplateView):
    template_name = os.path.join('inventory', 'reports', 'inventory_report.html')

    def get_context_data(self, *args, **kwargs):
        context = super(InventoryReport, self).get_context_data(*args, **kwargs)
        context['items'] = models.WareHouseItem.objects.all()
        context['date'] = datetime.date.today()
        #insert config
        return context


class OutstandingOrderReport(TemplateView):
    template_name = os.path.join('inventory', 'reports', 'outstanding_orders.html')

    def get_context_data(self, *args, **kwargs):
        context = super(OutstandingOrderReport, self).get_context_data(*args, **kwargs)
        context['orders'] = models.Order.objects.all()
        context['date'] = datetime.date.today()
        #insert config
        return context