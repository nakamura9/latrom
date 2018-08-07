# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from invoicing import forms
from wkhtmltopdf.views import PDFTemplateView
from wkhtmltopdf import utils as pdf_tools
from common_data.forms import SendMailForm
from common_data.models import GlobalConfig
from django.core.mail import EmailMessage
from rest_framework import viewsets

from common_data.utilities import ExtraContext, apply_style
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from invoicing.views.common import  SalesRepCheckMixin
from wkhtmltopdf.views import PDFTemplateView
from wkhtmltopdf import utils as pdf_tools
from django.core.mail import EmailMessage
from common_data.forms import SendMailForm

def process_data(items, inv):
    if items:
        items = json.loads(urllib.unquote(items))
        print items
        for item in items:
            inv.add_line(item['id'], item['hours'])
                
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        
    if inv.status == 'sent': 
        pass
        #inv.create_credit_entry()
    elif inv.status == 'paid':
        pass
        #inv.create_cash_entry()
    else:#includes drafts and quotations
        pass
        
class ServiceInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ServiceInvoiceSerializer
    queryset = ServiceInvoice.objects.all()
class ServiceInvoiceListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Service Invoice List",
                    "new_link": reverse_lazy("invoicing:create-service-invoice")}
    template_name = os.path.join("invoicing", "service_invoice","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return ServiceInvoice.objects.filter(active=True).order_by('date')
    

class ServiceInvoiceDetailView(SalesRepCheckMixin, DetailView):
    model = ServiceInvoice
    template_name = os.path.join("invoicing", "service_invoice",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(ServiceInvoiceDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return apply_style(context)

class ServiceInvoiceUpdateView(ExtraContext, UpdateView):
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:service-invoice-list')
    model = ServiceInvoice
    form_class = forms.ServiceInvoiceUpdateForm
    extra_context = {
        'title': 'Update Service Invoice'
    }
class ServiceInvoiceCreateView(SalesRepCheckMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","service_invoice", "create.html")
    form_class = forms.ServiceInvoiceForm
    success_url = reverse_lazy("invoicing:service-invoice-list")

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceInvoiceCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(ServiceInvoiceCreateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp

        inv = self.object
        items = request.POST.get("item_list", None)
        
        process_data(items, inv)

        return resp


class ServiceDraftUpdateView(SalesRepCheckMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","service_invoice", "create.html")
    form_class = forms.ServiceInvoiceForm
    success_url = reverse_lazy("invoicing:service-invoice-list")
    model = ServiceInvoice

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceDraftUpdateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(ServiceDraftUpdateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp

        #remove existing items
        for line in self.object.serviceinvoiceline_set.all():
            line.delete()
        
        inv = self.object
        items = request.POST.get("item_list", None)
        
        process_data(items, inv)

        return resp

class ServiceInvoicePaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.ServiceInvoicePaymentForm
    success_url = reverse_lazy('invoicing:service-invoice-list')
    extra_context= {
        'title': 'Apply Payment to Service Invoice'
    }

    def get_initial(self):
        return {
            'service_invoice': self.kwargs['pk'],
            'payment_for': 1
            }


class ServiceInvoicePaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'service_invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(service_invoice=ServiceInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceInvoicePaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = ServiceInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class ServiceInvoicePDFView(PDFTemplateView):
    template_name = os.path.join("invoicing", "service_invoice",
        'pdf.html')
    file_name = 'service_invoice.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(ServiceInvoicePDFView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['object'] = ServiceInvoice.objects.get(pk=self.kwargs['pk'])
        return apply_style(context)

class ServiceInvoiceEmailSendView(ExtraContext, FormView):
    form_class = SendMailForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')
    extra_context = {
        'title': 'Send Invoice as PDF attatchment'
    }

    def get_initial(self):
        inv = ServiceInvoice.objects.get(pk=self.kwargs['pk'])
        
        return {
            'recepient': inv.customer.customer_email
        }
    def post(self,request, *args, **kwargs):
        resp = super(ServiceInvoiceEmailSendView, self).post(
            request, *args, **kwargs)
        form = self.form_class(request.POST)
        
        if not form.is_valid():
            return resp
        
        config = GlobalConfig.objects.get(pk=1)
        msg = EmailMessage(
            subject=form.cleaned_data['subject'],
            body = form.cleaned_data['content'],
            from_email=config.email_user,
            to=[form.cleaned_data['recepient']]
        )

        template = os.path.join("invoicing", "service_invoice",
            'pdf.html')
        out_file = os.path.join(os.getcwd(), 'media', 'temp','out.pdf')
    
        context = {
            'object': ServiceInvoice.objects.get(pk=self.kwargs['pk'])
        }
        context.update(SalesConfig.objects.first().__dict__)
        options = {
            'output': out_file
        }
        try:
            pdf_tools.render_pdf_from_template(
                template, None, None, 
                apply_style(context),
                cmd_options=options)
        except Exception as e:
            raise Exception('Error occured creating pdf %s' % e )

        if os.path.isfile(out_file):
            msg.attach_file(out_file)
            msg.send()
            os.remove(out_file)

        # if the message is successful delete it.
        return resp