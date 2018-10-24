import datetime
import itertools
import os

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, FormView

from common_data.utilities import ExtraContext, extract_period
from invoicing import forms, models
from invoicing.models import AbstractSale


class CustomerReportFormView(ExtraContext, FormView):
    extra_context = {
        'title': 'Customer Statement Report',
        'action': reverse_lazy('invoicing:customer-statement')
    }
    form_class = forms.CustomerStatementReportForm
    template_name = os.path.join('common_data', 'reports', 'report_form.html')


class CustomerStatement(TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'customer_statement.html')
    def get_context_data(self, *args, **kwargs):
        context = super(CustomerStatement, self).get_context_data(*args, **kwargs)
        kwargs = self.request.GET
        customer = models.Customer.objects.get(
            pk=kwargs['customer'])
        
        start, end = extract_period(kwargs)
        
        #invoices 
        invoices = AbstractSale.abstract_filter(Q(Q(status='sent') | Q(status='paid')) &
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
        credit_invoices = AbstractSale.abstract_filter(Q(status='sent') | Q(status='paid'))
        outstanding_invoices = AbstractSale.abstract_filter(Q(status='sent'))
        context.update({
            'customers': models.Customer.objects.all(),
            'invoice_count': len([credit_invoices]),
            'outstanding_invoices': len([outstanding_invoices])
        })
        context.update(models.SalesConfig.objects.first().__dict__)
        return context
