# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from invoicing import forms

from common_data.utilities import ExtraContext, apply_style
from inventory.models import Item
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from invoicing.views.common import SalesRepCheckMixin
from rest_framework import viewsets
from wkhtmltopdf.views import PDFTemplateView
from wkhtmltopdf import utils as pdf_tools
from django.core.mail import EmailMessage
from common_data.forms import SendMailForm
from common_data.models import GlobalConfig

def process_data(data, inv):
    print 'data'
    print data
    items = json.loads(urllib.unquote(data))
    for item in items:
        inv.add_line(item['pk'])
    
    # moved here because the invoice item data must first be 
    # saved in the database before inventory and entries 
    # can be created
    if inv.status in ['draft', 'quotation']:
        pass
    elif inv.status == 'sent': 
        pass
        #inv.create_credit_entry()
    elif inv.status == 'paid':
        pass
        #inv.create_cash_entry()
    else:
        pass


class BillListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Customer Bill List",
                    "new_link": reverse_lazy("invoicing:bill-create")}
    template_name = os.path.join("invoicing", "bill","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return Bill.objects.filter(active=True).order_by('date')
    

class BillDetailView(SalesRepCheckMixin, DetailView):
    model = Bill
    template_name = os.path.join("invoicing", "bill",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(BillDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return apply_style(context)

        
class BillCreateView(SalesRepCheckMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("invoicing","bill", "create.html")
    form_class = forms.BillForm
    success_url = reverse_lazy("invoicing:bills-list")

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(BillCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        context.update({'include_customer': True})
        return context

    def post(self, request, *args, **kwargs):
        resp = super(BillCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        inv = self.object
        data = request.POST.get("item_list", None)
        process_data(data, inv)
        return resp

class BillDraftUpdateView(SalesRepCheckMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("invoicing","bill", "create.html")
    form_class = forms.BillUpdateForm
    success_url = reverse_lazy("invoicing:bills-list")
    model = Bill

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(BillDraftUpdateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        
        return context

    def post(self, request, *args, **kwargs):
        resp = super(BillDraftUpdateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        inv = self.object
        for line in inv.billline_set.all():
            line.delete()
        data = request.POST.get("item_list", None)
        process_data(data, inv)
        return resp


class BillUpdateView(ExtraContext, SalesRepCheckMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("common_data", "create_template.html")
    form_class = forms.BillUpdateForm
    success_url = reverse_lazy("invoicing:home")
    model = Bill
    extra_context ={
        'title': 'Update Bill'
    }


class BillAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BillSerializer
    queryset = Bill.objects.all()


class BillPaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.BillPaymentForm
    success_url = reverse_lazy('invoicing:bills-list')
    extra_context= {
        'title': 'Apply Payment for Customer Bill'
    }

    def get_initial(self):
        return {
            'bill': self.kwargs['pk'],
            'payment_for': 2
            }


class BillPaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'bill', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(bill=Bill.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(BillPaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = Bill.objects.get(pk=self.kwargs['pk'])
        return context


class BillPDFView(PDFTemplateView):
    template_name = os.path.join("invoicing", "bill",
        'pdf.html')
    file_name = 'bill.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(BillPDFView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['object'] = Bill.objects.get(pk=self.kwargs['pk'])
        return apply_style(context)

class BillEmailSendView(ExtraContext, FormView):
    form_class = SendMailForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:bills-list')
    extra_context = {
        'title': 'Send Invoice as PDF attatchment'
    }

    def get_initial(self):
        inv = Bill.objects.get(pk=self.kwargs['pk'])
        
        return {
            'recepient': inv.customer.customer_email
        }
    def post(self,request, *args, **kwargs):
        resp = super(BillEmailSendView, self).post(
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

        template = os.path.join("invoicing", "bill",
            'pdf.html')
        out_file = os.path.join(os.getcwd(), 'media', 'temp','out.pdf')
    
        context = {
            'object': Bill.objects.get(pk=self.kwargs['pk'])
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