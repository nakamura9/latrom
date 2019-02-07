import datetime
import itertools
import os
from decimal import Decimal as D
from functools import reduce
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, FormView

from common_data.utilities import ContextMixin, extract_period
from invoicing import forms, models
from invoicing.models import AbstractSale, SalesInvoice
from .report_utils.plotters import plot_sales

class CustomerReportFormView(ContextMixin, FormView):
    extra_context = {
        'title': 'Customer Statement Report',
        'action': reverse_lazy('invoicing:customer-statement')
    }
    form_class = forms.CustomerStatementReportForm
    template_name = os.path.join('common_data', 'reports', 'report_template.html')

    def get_initial(self):
        if self.kwargs.get('pk', None):
            return {
                'customer': self.kwargs['pk']
        } 
        return {}


class CustomerStatement(TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'customer_statement.html')
    def get_context_data(self, *args, **kwargs):
        context = super(CustomerStatement, self).get_context_data(*args, **kwargs)
        kwargs = self.request.GET
        customer = models.Customer.objects.get(
            pk=kwargs['customer'])
        
        start, end = extract_period(kwargs)
        
        #invoices 
        invoices = AbstractSale.abstract_filter(Q(Q(status='invoice') | Q(status='paid')) &
            Q(Q(date__gte=start) & Q(date__lte = end)))
        
        payments = models.Payment.objects.filter( Q(date__gte=start)
            & Q(date__lte = end)
        )
        invoices = sorted(invoices,
            key=lambda inv: inv.date)
        context.update({
            'customer': customer,
            'start': start,
            'end': end,
            'invoices': invoices,
            'payments': payments
        })
        context.update(models.SalesConfig.objects.first().__dict__)
        return context
        

class InvoiceAgingReport(TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'aging.html')

    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceAgingReport, self).get_context_data(*args, **kwargs)
        outstanding_invoices = AbstractSale.abstract_filter(Q(status='invoice'))
        context.update({
            'customers': models.Customer.objects.all(),
            'outstanding_invoices': len([i for i in outstanding_invoices])
        })
        context.update(models.SalesConfig.objects.first().__dict__)
        return context

# TODO test
class SalesReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    form_class = forms.SalesReportForm
    extra_context = {
        "action": reverse_lazy("invoicing:sales-report")
    }

# TODO test
class SalesReportView(TemplateView):
    template_name = os.path.join("invoicing", "reports", "sales_report.html")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = self.request.GET

        start, end = extract_period(kwargs)
        context["period"] = "{} to {}".format(start, end)

        total_sales = sum([i.subtotal for i in SalesInvoice.objects.filter(Q(date__gte=start) & Q(date__lte=end))])
        average_sales  = total_sales / D(abs((end - start).days))

        context["total_sales"] = total_sales
        context["average_sales"] = average_sales
    
        context["report"] = plot_sales(start, end)
        return context