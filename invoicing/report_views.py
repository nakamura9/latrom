import os
import datetime

from django.views.generic.edit import CreateView, FormView
from django.views.generic import TemplateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q

from common_data.utilities import ExtraContext, extract_period
import models 
import forms

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
        
        invoices = models.Invoice.objects.filter(
            Q(customer=customer) & Q(date_issued__gte=start)
            & Q(date_issued__lte = end)
        )
        payments = models.Payment.objects.filter(
            Q(invoice__customer=customer) & Q(date__gte=start)
            & Q(date__lte = end)
        )
        
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
        credit_invoices = models.Invoice.objects.filter(
                type_of_invoice='credit')
        outstanding_invoices = [i for i in credit_invoices \
            if not i.paid_in_full]
        context.update({
            'customers': models.Customer.objects.all(),
            'invoice_count': credit_invoices.count(),
            'outstanding_invoices': len(outstanding_invoices)
        })
        context.update(models.SalesConfig.objects.first().__dict__)
        return context