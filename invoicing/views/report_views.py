import datetime
import itertools
import os
from decimal import Decimal as D
from functools import reduce
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, FormView
from wkhtmltopdf.views import PDFTemplateView
import urllib
from accounting.models import Credit, Debit


from common_data.utilities import (ContextMixin, 
                                    extract_period,  
                                    MultiPageDocument,
                                    PeriodReportMixin,
                                    ConfigMixin, 
                                    PeriodReportMixin)
from invoicing import forms, models
from invoicing.models.invoice import Invoice
from .report_utils.plotters import plot_sales

import pygal

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


class CustomerStatement(ConfigMixin, 
                        MultiPageDocument, 
                        PeriodReportMixin, 
                        TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'customer_statement.html')
    page_length=20

    def get_multipage_queryset(self):
        kwargs = self.request.GET
        customer = models.Customer.objects.get(
            pk=kwargs['customer'])
        
        start, end = extract_period(kwargs)
        
        credits = Credit.objects.filter(
            Q(entry__date__gte=start) & 
            Q(entry__date__lte=end) &
            Q(account=customer.account)
        ).order_by('pk')
        debits = Debit.objects.filter(
            Q(entry__date__gte=start) & 
            Q(entry__date__lte=end) &
            Q(account=customer.account)
        ).order_by('pk')

        return sorted(itertools.chain(debits, credits), key=lambda t: t.entry.date)


    @staticmethod 
    def common_context(context, customer, start, end):
        
        context.update({
            'customer': customer,
            'start': start.strftime("%d %B %Y"),
            'end': end.strftime("%d %B %Y"),
             'balance_brought_forward': customer.account.balance_on_date(start),
            'balance_at_end_of_period': customer.account.balance_on_date(end)
        })
        return context

    def get_context_data(self, *args, **kwargs):
        context = super(CustomerStatement, self).get_context_data(*args, **kwargs)

        kwargs = self.request.GET
        customer = models.Customer.objects.get(
            pk=kwargs['customer'])
        
        start, end = extract_period(kwargs)
        
        context['pdf_link'] = True
        return CustomerStatement.common_context(context, customer, start, end)
        
class CustomerStatementPDFView(ConfigMixin, MultiPageDocument,PDFTemplateView):
    template_name = CustomerStatement.template_name
    file_name ="customer_statement.pdf"

    page_length=20

    def get_multipage_queryset(self):
        start = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['end']), "%d %B %Y")
        customer = models.Customer.objects.get(pk=self.kwargs['customer'])
        
        
        credits = Credit.objects.filter(
            Q(entry__date__gte=start) & 
            Q(entry__date__lte=end) &
            Q(account=customer.account)
        ).order_by('pk')
        debits = Debit.objects.filter(
            Q(entry__date__gte=start) & 
            Q(entry__date__lte=end) &
            Q(account=customer.account)
        ).order_by('pk')

        return sorted(itertools.chain(debits, credits), key=lambda t: t.entry.date)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['end']), "%d %B %Y")
        customer = models.Customer.objects.get(pk=self.kwargs['customer'])
        return CustomerStatement.common_context(context, customer, start, end)
        


class InvoiceAgingReport(ConfigMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'aging.html')
    page_length = 20

    def get_multipage_queryset(self):
        return models.Customer.objects.all()

        
    @staticmethod 
    def common_context(context):
        outstanding_invoices = Invoice.objects.filter(Q(status='invoice'))
        context.update({
            'customers': models.Customer.objects.all(),
            'outstanding_invoices': len([i for i in outstanding_invoices])
        })
        return context

    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceAgingReport, self).get_context_data(*args, **kwargs)
        context['pdf_link'] = True
        return InvoiceAgingReport.common_context(context)

class InvoiceAgingPDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = InvoiceAgingReport.template_name
    file_name ="invoice_aging.pdf"
    page_length = 20

    def get_multipage_queryset(self):
        return models.Customer.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return InvoiceAgingReport.common_context(context)

class SalesReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    form_class = forms.SalesReportForm
    extra_context = {
        "action": reverse_lazy("invoicing:sales-report")
    }

class SalesReportView(ConfigMixin, PeriodReportMixin, TemplateView):
    template_name = os.path.join("invoicing", "reports", "sales_report.html")

    @staticmethod
    def common_context(context, start, end):

        total_sales = sum([i.subtotal for i in Invoice.objects.filter(Q(date__gt=start) & Q(date__lte=end) & Q(
            Q(status='invoice') | 
            Q(status='paid') | 
            Q(status='paid-partially')) & 
            Q(draft=False))
            ])
        average_sales  = total_sales / D(abs((end - start).days))

        context["total_sales"] = total_sales
        context["average_sales"] = average_sales
        context.update({
            'start': start.strftime("%d %B %Y"), 
            'end': end.strftime("%d %B %Y")
            })
        context["report"] = plot_sales(start, end)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = self.request.GET
        context['pdf_link'] = True
        start, end = extract_period(kwargs)
        return SalesReportView.common_context(context, start, end)

class SalesReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = SalesReportView.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        start = datetime.datetime.strptime(
            urllib.parse.unquote(self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(
            urllib.parse.unquote(self.kwargs['end']), "%d %B %Y")
        return SalesReportView.common_context(context, start, end)
        