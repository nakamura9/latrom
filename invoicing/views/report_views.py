import datetime
import itertools
import os
import json 
import urllib
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
from .report_utils.plotters import plot_sales, plot_lines
from inventory.models import InventoryItem
from services.models import Service

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
    template_name = os.path.join('invoicing', 'reports', 'sales_report_form.html')
    form_class = forms.SalesReportForm
    extra_context = {
        "action": reverse_lazy("invoicing:sales-report")
    }

class SalesReportView(ConfigMixin, PeriodReportMixin, TemplateView):
    template_name = os.path.join("invoicing", "reports", "sales_report.html")

    @staticmethod
    def common_context(context, start, end, kwargs):
        # if filtering reps and customers - use the entire invoice 

        products = json.loads(urllib.parse.unquote(kwargs['products']))
        services = json.loads(urllib.parse.unquote(kwargs['services']))

        def get_invoice_filters(data):
            rep_query = Q()
            cus_query = Q()
            reps = json.loads(urllib.parse.unquote(data['reps']))
            for rep_str in reps:
                id = rep_str.split('-')[0]
                rep = models.SalesRepresentative.objects.get(pk=id)
                rep_query.add(Q(salesperson=rep), Q.OR)
            
            customers = json.loads(urllib.parse.unquote(data['customers']))
            for cus_str in customers:
                id = cus_str.split('-')[0]
                cus = models.Customer.objects.get(pk=id)
                cus_query.add(Q(customer=cus), Q.OR)

            
            query = Q(rep_query & cus_query)
            return query

        def get_line_filters(services, products):
            pro_query= Q()
            srv_query= Q()
            for pro_str in products:
                id = pro_str.split('-')[0]
                pro = InventoryItem.objects.get(pk=id)
                pro_query.add(Q(product__product=pro), Q.OR)

            for srv_str in services:
                id = srv_str.split('-')[0]
                srv = Service.objects.get(pk=id)
                srv_query.add(Q(service__service=srv), Q.OR)
            
            query = Q(pro_query & srv_query)
            return query

        if len(products) == 0 and len(services) == 0:
            additional_args = get_invoice_filters(kwargs)
            total_sales = sum([i.subtotal for i in Invoice.objects.filter(
                Q(date__gt=start) & 
                Q(date__lte=end) & 
                Q(draft=False) & Q(
                    Q(status='invoice') | 
                    Q(status='paid') | 
                    Q(status='paid-partially')
                ) & 
                additional_args)
                ])
            context["report"] = plot_sales(start, end, filters=additional_args)
            
        else:
            additional_args = get_line_filters(services, products)
            
            filters = Q(Q(invoice__date__gt=start) &
                Q(invoice__date__lte=end) &
                Q(invoice__draft=False) &
                Q(
                    Q(invoice__status='invoice') | 
                    Q(invoice__status='paid') | 
                    Q(invoice__status='paid-partially')
                ) &
                additional_args)
            total_sales = sum([i.subtotal for i in \
                     models.InvoiceLine.objects.filter(filters)])
            context["report"] = plot_lines(start, end, filters=additional_args)

            

        
        average_sales  = total_sales / D(abs((end - start).days))

        context["total_sales"] = total_sales
        context["average_sales"] = average_sales
        context.update({
            'start': start.strftime("%d %B %Y"), 
            'end': end.strftime("%d %B %Y")
            })
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = self.request.GET
        context['pdf_link'] = True
        start, end = extract_period(kwargs)
        return SalesReportView.common_context(context, start, end, kwargs)

class SalesReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = SalesReportView.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        start = datetime.datetime.strptime(
            urllib.parse.unquote(self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(
            urllib.parse.unquote(self.kwargs['end']), "%d %B %Y")
        return SalesReportView.common_context(context, start, end)
        