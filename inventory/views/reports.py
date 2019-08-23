import datetime
import os

from django.views.generic import TemplateView, FormView
from common_data.forms import PeriodReportForm
from . import models
from common_data.utilities import (ConfigMixin, 
                                   MultiPageDocument,
                                   ContextMixin,
                                   extract_period)
                                
from inventory.views.common import CREATE_TEMPLATE
from wkhtmltopdf.views import PDFTemplateView
from accounting.models import JournalEntry, Credit, Debit
from django.db.models import Q

class InventoryReport( ConfigMixin, MultiPageDocument,TemplateView):
    template_name = os.path.join('inventory', 'reports', 'inventory',
        'report.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.InventoryItem.objects.filter(type=0, active=True)

    def get_context_data(self, *args, **kwargs):
        context = super(InventoryReport, self).get_context_data(*args, **kwargs)
        context['items'] = models.WareHouseItem.objects.filter(item__type=0)
        context['date'] = datetime.date.today()
        context['pdf_link'] = True


        #insert config
        return context


class OutstandingOrderReport( ConfigMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('inventory', 'reports', 'outstanding_orders','report.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.Order.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(OutstandingOrderReport, self).get_context_data(*args, **kwargs)
        context['orders'] = models.Order.objects.all()
        context['date'] = datetime.date.today()
        context['pdf_link'] = True
        #insert config
        return context



class InventoryReportPDFView( ConfigMixin, MultiPageDocument,  PDFTemplateView):
    template_name = os.path.join('inventory', 'reports', 'inventory_report.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.WareHouseItem.objects.filter(item__type=0)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['items'] = models.WareHouseItem.objects.all()
        context['date'] = datetime.date.today()
        #insert config
        return context


class OutstandingOrderReportPDFView( ConfigMixin, PDFTemplateView):
    template_name = os.path.join('inventory', 'reports', 'outstanding_orders.html')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #TODO limit to orders that are not yet fully received
        context['orders'] = models.Order.objects.all()
        context['date'] = datetime.date.today()
        #insert config
        return context


class PaymentsDueReportView(ContextMixin,
                            ConfigMixin, 
                            MultiPageDocument, 
                            TemplateView):
    template_name = os.path.join('inventory', 'reports', 'payments_due',
        'report.html')
    page_length = 20
    extra_context ={
        'date': datetime.date.today(),
        'pdf_link': True
    }
    

    def get_multipage_queryset(self):
        return models.Order.objects.filter(
                due__lte=datetime.date.today(),
                status__in=['order', 'received', 'received_partially']) 

    
class VendorBalanceReportView(ContextMixin, 
                          ConfigMixin, 
                          MultiPageDocument, 
                          TemplateView):
    template_name = os.path.join('inventory', 'reports', 'vendor_balance',
        'report.html')
    page_length = 20
    extra_context = {
        'date': datetime.date.today(),
        'pdf_link': True,
        'total': lambda: sum([i.account.balance \
                             for i in models.Supplier.objects.all()])
    }

    def get_multipage_queryset(self):
        return models.Supplier.objects.all()


class VendorAverageDaysToDeliverReportView(ConfigMixin,
                                         ContextMixin,
                                         MultiPageDocument,
                                         TemplateView):

    template_name = os.path.join('inventory', 'reports', 'days_to_deliver', 
        'report.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.Supplier.objects.all()
    extra_context = {
        'date': datetime.date.today(),
        'pdf_link': True
    } 

class TransactionByVendorReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = PeriodReportForm
    extra_context = {
        'action': '/inventory/vendor-transactions-report/'
    }

class TransactionByVendorReportView(ConfigMixin, TemplateView):
    template_name = os.path.join('inventory', 'reports', 'vendor_transactions', 'report.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = extract_period(self.request.GET)
        vendors = models.Supplier.objects.all()
        context.update({
            'start': start,
            'end': end,
            'pdf_link': True
        })
        context["vendors"] = [{
            'name': v.name,
            'transactions': sorted(list(Credit.objects.filter(
                account=v.account, 
                entry__date__gte=start,
                entry__date__lte=end
                )
            ) + list(Debit.objects.filter(account=v.account, 
                entry__date__gte=start,
                entry__date__lte=end
                    )
                ),
            key=lambda x: x.entry.date),
            'total': v.account.balance_over_period(start, end)
        } for v in vendors]
        return context
    