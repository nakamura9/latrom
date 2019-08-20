import datetime
import os
import urllib

from services.models import TimeLog, ServiceWorkOrder
from django.views.generic import TemplateView, DetailView
from common_data.utilities import extract_period, PeriodReportMixin, PeriodSelectionException
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from common_data.views import ContextMixin
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

class JobProfitabilityReport(TemplateView):
    template_name = os.path.join('services', 'reports', 'job_profitability.html')

    def get_context_data(self, *args, **kwargs):
        context =super().get_context_data(*args, **kwargs)
        start, end = extract_period(self.request.GET)
        jobs = InvoiceLine.objects.filter(
                Q(invoice__date__gte=start) &
                Q(invoice__date__lte=end) &
                Q(invoice__draft=False) &
                Q(invoice__status__in=['paid', 'invoice', 'paid-partially']) &
                Q(service__isnull=False))
        revenue = sum([i.subtotal for i in jobs])
        expenses = sum([i.service.cost_of_sale for i in jobs])

        context['jobs'] = jobs
        context['revenue'] = revenue
        context['expenses'] = expenses
        context['income'] = revenue - expenses
        context.update({
            'start': start,
            'end': end,
            'date': datetime.date.today()
        })

        return context

class WorkOrderCostingView(DetailView):
    template_name = os.path.join('services', 'work_order', 'costing.html')
    model = ServiceWorkOrder

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        labour = sum([i.total_cost for i in self.object.time_logs])
        expenses = sum([i.expense.amount \
            for i in self.object.workorderexpense_set.all()])
        consumables = sum([i.line_value for i in \
                 self.object.consumables_used])
        
        context['total_consumables_costs'] = consumables
        context['total_labour_cost'] = labour 
        context['total_expense_costs'] = expenses
        context['total_costs'] = labour + expenses + consumables
        context['graph'] = plot_expense_breakdown(self.object)
        return context


class UnbilledCostsByJobReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = PeriodReportForm
    
    extra_context = {
        'action':reverse_lazy('services:reports-unbilled-costs-by-job'),
    }

class UnbilledCostsByJobReportView(TemplateView):
    template_name = os.path.join('services', 'reports', 'unbilled_costs.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end = extract_period(self.request.GET)
        context["jobs"] = ServiceWorkOrder.objects.filter(date__gte=start, 
            date__lte=end)
        context.update({
            'start': start,
            'end': end,
            'date': datetime.date.today()
        })
        return context
    