import os
import datetime
from django.views.generic import FormView, DetailView, TemplateView
from common_data.utilities import ExtraContext, load_config
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q

import models
import forms
FORM_TEMPLATE = os.path.join('common_data', 'create_template.html')

class CustomerStatementReportFormView(ExtraContext, FormView):
    form_class = forms.CustomerStatementReportForm
    template_name = FORM_TEMPLATE
    extra_context = {
        'title': 'Select Customer for report.'
    }
    success_url = reverse_lazy('invoicing:customer-statement-form')
    def post(self, request):
        resp = super(CustomerStatementReportFormView, self).post(request)
        form = self.form_class(request.POST)
        if not form.is_valid():
            return resp
        else:
            data = request.POST.dict()
            del data['csrfmiddlewaretoken']
            request.session.update(data) 
            return HttpResponseRedirect(
                reverse_lazy('invoicing:customer-statement'))

class CustomerStatementReport(TemplateView):
    template_name = os.path.join('invoicing', 'reports', 'customer_statement.html')

    def get_context_data(self):
        context = super(CustomerStatementReport, self).get_context_data()
        customer = models.Customer.objects.get(pk=self.request.session['customer'])
        context['customer'] = customer
        context.update(load_config())

        if self.request.session['default_periods'] == '0':
            start_period = datetime.datetime.strptime(
                    self.request.session['start_period'], "%m/%d/%Y")
            end_period = datetime.datetime.strptime(
                    self.request.session['end_period'], "%m/%d/%Y")
        else:
            deltas = {
                '1': 30,
                '2': 90,
                '3': 180
                }
            end_period = datetime.date.today()
            start_period = end_period - datetime.timedelta(
                deltas[self.request.session['default_periods']])

        context['start'] = start_period
        context['end'] = end_period
        context['payments'] = models.Payment.objects.filter(Q(invoice__customer=customer)
                & Q(date__gte=start_period)
                & Q(date__lte=end_period))
        context['invoices'] = models.Invoice.objects.filter(Q(customer=customer)
                & Q(date_issued__gte=start_period)
                & Q(date_issued__lte=end_period))
        
        return context