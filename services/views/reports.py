import datetime
import os
import urllib

from services.models import TimeLog, ServiceWorkOrder
from django.views.generic import TemplateView, DetailView

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from common_data.utilities import (ContextMixin, 
                                   MultiPageDocument,
                                   extract_period, 
                                   PeriodReportMixin, 
                                   PeriodSelectionException,
                                   encode_period,
                                   extract_encoded_period)
from common_data.forms import PeriodReportForm
from functools import reduce
from wkhtmltopdf.views import PDFTemplateView
from invoicing.models import InvoiceLine
import pygal
from services.views.report_utils.plotters import plot_expense_breakdown

class ServicePersonUtilizationFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = PeriodReportForm
    
    extra_context = {
        'action':reverse_lazy('services:reports-service-person-utilization'),
    }

class ServicePersonUtilizationReport( PeriodReportMixin, TemplateView):
    template_name = os.path.join('services', 'reports', 'service_person_utilization.html')

    @staticmethod
    def common_context(context, start, end):
        logs = TimeLog.objects.filter(Q(date__gte=start), Q(date__lte=end))
        histogram = {}
        for log in logs:
            histogram.setdefault(str(log.employee), [])
            histogram[str(log.employee)].append(log.normal_time)

        x = histogram.keys()
        y = [reduce(lambda x, y: x + y, histogram[key], datetime.timedelta(seconds=0)).seconds / 3600  for key in x]
        
        chart = pygal.Bar()
        chart.title = 'Service Person Utilization'
        chart.x_labels = x
        chart.add('Hours', y)


        context['graph'] = chart.render(is_unicode=True)
        average_time = 0 
        if len(y) > 0:
            average_time = sum(y) / len(y)
        context.update({
            'start': start.strftime("%d %B %Y"),
            'end': end.strftime("%d %B %Y"),
            'date': datetime.date.today(),
            'number_employees': len(x),
            'average_time': average_time
            })
        return context

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        kwargs =  self.request.GET
        start, end = extract_period(kwargs)
        context['pdf_link'] = True
        return ServicePersonUtilizationReport.common_context(context, start, 
            end)

    


class ServicePersonUtilizationReportPDFView(PDFTemplateView):
    template_name = os.path.join('services', 'reports', 'service_person_utilization.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        start = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['end']), "%d %B %Y")

        return ServicePersonUtilizationReport.common_context(context, start, 
            end)

class JobProfitabilityReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = PeriodReportForm
    
    extra_context = {
        'action':reverse_lazy('services:reports-job-profitability'),
    }

class JobProfitabilityReport(ContextMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('services', 'reports', 
        'job_profitability.html')
    page_length = 20
    extra_context = {
        'pdf_link': True
    }

    def get_multipage_queryset(self):
        start, end = extract_period(self.request.GET)

        return InvoiceLine.objects.filter(
                Q(invoice__date__gte=start) &
                Q(invoice__date__lte=end) &
                Q(invoice__draft=False) &
                Q(invoice__status__in=['paid', 'invoice', 'paid-partially']) &
                Q(service__isnull=False))

    @staticmethod
    def common_context(context, start, end):
        jobs = InvoiceLine.objects.filter(
                Q(invoice__date__gte=start) &
                Q(invoice__date__lte=end) &
                Q(invoice__draft=False) &
                Q(invoice__status__in=['paid', 'invoice', 'paid-partially']) &
                Q(service__isnull=False))
        revenue = sum([i.subtotal for i in jobs])
        expenses = sum([i.service.cost_of_sale for i in jobs])
        context['jobs_count'] = jobs.count()
        context['revenue'] = revenue
        context['expenses'] = expenses
        context['income'] = revenue - expenses
        start, end = encode_period(start, end)
        context.update({
            'start': start,
            'end': end,
            'date': datetime.date.today()
        })

    def get_context_data(self, *args, **kwargs):
        context =super().get_context_data(*args, **kwargs)
        start, end = extract_period(self.request.GET)
        self.__class__.common_context(context, start, end)

        return context

class JobProfitabilityPDFView(MultiPageDocument, PDFTemplateView):
    template_name = JobProfitabilityReport.template_name
    page_length = JobProfitabilityReport.page_length

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = extract_encoded_period(self.kwargs)
        JobProfitabilityReport.common_context(context, start, end)
        
        return context

    def get_multipage_queryset(self):
        start, end = extract_encoded_period(self.kwargs)

        return InvoiceLine.objects.filter(
                Q(invoice__date__gte=start) &
                Q(invoice__date__lte=end) &
                Q(invoice__draft=False) &
                Q(invoice__status__in=['paid', 'invoice', 'paid-partially']) &
                Q(service__isnull=False))

class WorkOrderCostingView(ContextMixin, DetailView):
    template_name = os.path.join('services', 'work_order', 'costing.html')
    model = ServiceWorkOrder
    extra_context = {
        'pdf_link': True
    }

    @staticmethod
    def common_context(context, obj):
        labour = sum([i.total_cost for i in obj.time_logs])
        expenses = sum([i.expense.amount \
            for i in obj.workorderexpense_set.all()])
        consumables = sum([i.line_value for i in \
                 obj.consumables_used])
        
        context['total_consumables_costs'] = consumables
        context['total_labour_cost'] = labour 
        context['total_expense_costs'] = expenses
        context['total_costs'] = labour + expenses + consumables
        context['graph'] = plot_expense_breakdown(obj)
        


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.__class__.common_context(context, self.object)
        return context


class WorkOrderCostingPDFView(PDFTemplateView):
    template_name = WorkOrderCostingView.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] =ServiceWorkOrder.objects.get(pk=self.kwargs['pk'])
        WorkOrderCostingView.common_context(context,
            context['object'])
        return context


class UnbilledCostsByJobReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = PeriodReportForm
    
    extra_context = {
        'action':reverse_lazy('services:reports-unbilled-costs-by-job'),
    }

class UnbilledCostsByJobReportView(ContextMixin,
                                   MultiPageDocument, 
                                   TemplateView):
    template_name = os.path.join('services', 'reports', 'unbilled_costs.html')
    page_length = 10
    extra_context = {
        'pdf_link': True
    }

    def get_multipage_queryset(self):
        start, end = extract_period(self.request.GET)
        
        return ServiceWorkOrder.objects.filter(date__gte=start, 
            date__lte=end)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = encode_period(*extract_period(self.request.GET))
        context.update({
            'start': start,
            'end': end,
            'date': datetime.date.today()
        })
        return context
    

class UnbilledCostsByJobPDFView(MultiPageDocument, PDFTemplateView):
    template_name = UnbilledCostsByJobReportView.template_name
    page_length = UnbilledCostsByJobReportView.page_length

    def get_multipage_queryset(self):
        start, end = extract_encoded_period(self.kwargs)
        return ServiceWorkOrder.objects.filter(date__gte=start, 
            date__lte=end)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = extract_encoded_period(self.kwargs)
        context.update({
            'start': start,
            'end': end,
            'date': datetime.date.today()
        })
        return context
    