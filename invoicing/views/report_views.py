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
                                    encode_period,
                                    extract_encoded_period,  
                                    MultiPageDocument,
                                    PeriodReportMixin,
                                    ConfigMixin, 
                                    PeriodReportMixin)
from invoicing import forms, models
from invoicing.models.invoice import Invoice
from .report_utils.plotters import (plot_sales, 
                                    plot_sales_by_customer,
                                    plot_sales_by_products_and_services,
                                    plot_ar_by_customer,
                                    plot_ar_by_aging)
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
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = forms.SalesReportForm
    extra_context = {
        "action": reverse_lazy("invoicing:sales-report")
    }

#Pagniated by Table
class SalesReportView(ContextMixin, 
                      ConfigMixin, 
                      PeriodReportMixin, 
                      TemplateView):
    extra_context = {
        'pdf_link': True
    }
    template_name = os.path.join("invoicing", "reports", "sales_report.html")

    @staticmethod
    def common_context(context, start, end):
        # if filtering reps and customers - use the entire invoice 

        context["bar_graph"] = plot_sales(start, end)
        context["pie_chart"] = plot_sales_by_customer(start, end)
        context["pie_chart_2"] = plot_sales_by_products_and_services(start, end)
        
        customer_list = set([i.customer for i in Invoice.objects.filter(date__gte=start, date__lte=end, draft=False)])
        
        context['customer_invoices'] = [{
            'name': str(c), 
            'sales': c.sales_over_period(start, end),
            'total': sum([j.subtotal for j in c.sales_over_period(start, end)])
            } for c in customer_list]


        filters = Q(Q(invoice__date__gt=start) &
            Q(invoice__date__lte=end) &
            Q(invoice__draft=False) &
            Q(
                Q(invoice__status='invoice') | 
                Q(invoice__status='paid') | 
                Q(invoice__status='paid-partially')
            ) )
        lines = models.InvoiceLine.objects.filter(filters)
        sbps = {}
        for l in lines:
            sbps.setdefault(l.name, {
                'name': l.name,
                'type': l.type_string,
                'quantity': 0,
                'total': 0
            }) 
            sbps[l.name]['quantity'] +=  l.product.quantity if l.product else 0
            sbps[l.name]['total'] += l.subtotal
        
        context['products_and_services'] = sbps
        
        total_sales = sum([i.subtotal for i in \
                     lines])
        
        average_sales  = total_sales / D(abs((end - start).days))


        context["total_sales"] = total_sales
        context["average_sales"] = average_sales
        context.update({
            'start': start.strftime("%d %B %Y"), 
            'end': end.strftime("%d %B %Y"),
            })
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
        
#Do not paginate!
class AccountsReceivableDetailReportView(ContextMixin, 
                                         ConfigMixin, 
                                         TemplateView):
    extra_context = {
        'pdf_link': True
    }
    template_name = os.path.join('invoicing', 'reports', 'accounts_receivable', 
        'report.html')

    @staticmethod
    def common_context(context):
        invs = Invoice.objects.filter(status__in=['invoice', 'paid-partially'], 
            draft=False)
        context["current"] = list(filter(lambda x: x.overdue_days == 0, invs))
        context['week'] = list(filter(
            lambda x: x.overdue_days > 0 and x.overdue_days < 7, invs))
        context['week_two'] = list(filter(
            lambda x: x.overdue_days > 6 and x.overdue_days < 15, invs))
        context['month'] = list(filter(
            lambda x: x.overdue_days > 14 and x.overdue_days < 31, invs))
        context['two_months'] = list(filter(
            lambda x: x.overdue_days > 30 and x.overdue_days < 61, invs))
        context['more'] = list(filter(
            lambda x: x.overdue_days > 60, invs))

        context['ar_by_customer'] = plot_ar_by_customer()
        context['ar_by_aging'] = plot_ar_by_aging()
        context['date'] = datetime.date.today()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AccountsReceivableDetailReportView.common_context(context)


        return context

class AccountsReceivableReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = AccountsReceivableDetailReportView.template_name
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        AccountsReceivableDetailReportView.common_context(context)
        return context
    


class SalesByCustomerReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    form_class = forms.SalesReportForm
    extra_context = {
        "action": reverse_lazy("invoicing:sales-by-customer-report")
    }

#Do not paginate(For Now!)
class SalesByCustomerReportView(ContextMixin, ConfigMixin, TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'sales_by_customer', 
        'report.html')
    extra_context = {
        'pdf_link': True
    }

    @staticmethod
    def common_context(context, start, end):
        context["customers"] = [{
            'name': str(c),
            'sales': sum([i.subtotal for i in c.sales_over_period(start, end)])
            } for c in models.Customer.objects.all()]
        context["sales"] = models.Invoice.objects.filter(date__gte=start,
            date__lte=end)
        
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = extract_period(self.request.GET)
        context.update({
            'start': start.strftime("%d %B %Y"),
            'end': end.strftime("%d %B %Y")
        })
        SalesByCustomerReportView.common_context(context, start, end)
        return context

class SalesByCustomerReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = SalesByCustomerReportView.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        start, end = extract_encoded_period(self.kwargs)
        SalesByCustomerReportView.common_context(context, start, end)
        return context
    
class CustomerPaymentsReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = forms.SalesReportForm
    extra_context = {
        "action": reverse_lazy("invoicing:customer-payments-report")
    }


class CustomerPaymentsReportView(ContextMixin,
                                 ConfigMixin, 
                                 MultiPageDocument,
                                 TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'customer_payments', 
        'report.html')
    page_length = 20
    extra_context = {
        'pdf_link': True
    }

    def get_multipage_queryset(self):
        start, end = extract_period(self.request.GET)
        return models.Payment.objects.filter(date__gte=start, 
            date__lte=end)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = encode_period(*extract_period(self.request.GET))

        context.update({
            'start': start,
            'end': end
        })
        return context


class CustomerPaymentsPDFView(ConfigMixin, 
                              MultiPageDocument, 
                              PDFTemplateView):
    template_name = CustomerPaymentsReportView.template_name
    page_length=20

    def get_multipage_queryset(self):
        start, end = extract_encoded_period(self.kwargs)
        return models.Payment.objects.filter(date__gte=start, 
            date__lte=end)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = extract_encoded_period(self.kwargs)
        context.update({
            'start': start,
            'end': end
        })
        return context

class AverageDaysToPayReportView(ContextMixin,
                                 ConfigMixin, 
                                 MultiPageDocument,
                                 TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'average_days_to_pay', 
        'report.html')
    page_length = 20
    extra_context = {
        'pdf_link': True,
        'date': datetime.date.today()
    }

    def get_multipage_queryset(self):
        return models.Customer.objects.all()

    @staticmethod
    def common_context(context):
        chart = pygal.Bar()
        chart.title = 'Average Days to Pay'
        customer_names = [str(i) for i in models.Customer.objects.all()]
        customer_averages = [i.average_days_to_pay \
            for i in models.Customer.objects.all()]
        chart.x_labels = customer_names
        chart.add('Days To Pay', customer_averages)

        context['graph'] = chart.render(is_unicode=True)
        return context 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.__class__.common_context(context)
        
        return context

class AverageDaysToPayPDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = AverageDaysToPayReportView.template_name
    page_length= AverageDaysToPayReportView.page_length

    def get_multipage_queryset(self):
        return AverageDaysToPayReportView.get_multipage_queryset(self)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['date'] = datetime.date.today()
        AverageDaysToPayReportView.common_context(context)
        return context