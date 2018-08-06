                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    # -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from rest_framework import viewsets
from django.core.mail import EmailMessage

from invoicing import forms
from common_data.utilities import ExtraContext, apply_style
from inventory.models import Item
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from invoicing.views.common import  SalesRepCheckMixin
from wkhtmltopdf.views import PDFTemplateView
from wkhtmltopdf import utils as pdf_tools
from common_data.forms import SendMailForm
from common_data.models import GlobalConfig 

def process_data(items, inv):
    if items:
        print items
        items = json.loads(urllib.unquote(items))
        print items
        for item in items:

            pk, name = item['item_name'].split('-')
            inv.add_item(Item.objects.get(pk=pk), 
                item['quantity'])
    
    # moved here because the invoice item data must first be 
    # saved in the database before inventory and entries 
    # can be created
    if inv.status in ['draft', 'quotation']:
        pass
    elif inv.status == 'sent': 
        pass
        #inv.update_inventory()
        #inv.create_credit_entry()
    elif inv.status == 'paid':
        pass
        #inv.update_inventory()
        #inv.create_cash_entry()
    else:
        pass

class SalesInvoiceListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Sales Invoice List",
                    "new_link": reverse_lazy("invoicing:create-sales-invoice")}
    template_name = os.path.join("invoicing", "sales_invoice","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return SalesInvoice.objects.filter(active=True).order_by('date')
    

class SalesInvoiceDetailView(SalesRepCheckMixin, DetailView):
    model = SalesInvoice
    template_name = os.path.join("invoicing", "sales_invoice",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['title'] = context.get('invoice_title', "Invoice")
        return apply_style(context)

        
class SalesInvoiceCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Invoice"
        }
            
    template_name = os.path.join("invoicing","sales_invoice", "create.html")
    form_class = forms.SalesInvoiceForm
    success_url = reverse_lazy("invoicing:sales-invoice-list")
    model = SalesInvoice

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(SalesInvoiceCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp

        inv = self.object
        
        items = request.POST.get("item_list", None)
        process_data(items, inv)

        return resp


class SalesDraftUpdateView(UpdateView):
    model = SalesInvoice
    form_class = forms.SalesInvoiceForm
    template_name = os.path.join('invoicing', 'sales_invoice','create.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')

    def get_context_data(self, *args, **kwargs):
        context = super(SalesDraftUpdateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(SalesDraftUpdateView, self).post(request, *args, **kwargs)

        #remove existing lines
        for line in self.object.salesinvoiceline_set.all():
            line.delete()
        #create new lines 
        items = request.POST.get("item_list", None)
        
        process_data(items, self.object)

        return resp


class SalesInvoiceUpdateView(ExtraContext, UpdateView):
    extra_context = {
        'title': 'Edit Sales Invoice Details'
    }
    model = SalesInvoice
    form_class = forms.SalesInvoiceUpdateForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')


def apply_full_payment_on_invoice(request):
    pass


class SalesInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SalesInvoiceSerializer
    queryset = SalesInvoice.objects.all()


class SalesInvoicePaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.SalesInvoicePaymentForm
    success_url = reverse_lazy('invoicing:sales-invoice-list')
    extra_context= {
        'title': 'Apply Payment to Sales Invoice'
    }

    def get_initial(self):
        return {
            'sales_invoice': self.kwargs['pk'],
            'payment_for': 0
            }


class SalesInvoicePaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'sales_invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(sales_invoice=SalesInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoicePaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class SalesInvoiceReturnsDetailView(ListView):
    template_name = os.path.join('invoicing', 'sales_invoice', 
        'credit_note', 'detail_list.html')

    def get_queryset(self):
        return CreditNote.objects.filter(invoice=SalesInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceReturnsDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class SalesInvoicePDFView(PDFTemplateView):
    template_name = os.path.join("invoicing", "sales_invoice",
        'pdf.html')
    file_name = 'sales_invoice.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoicePDFView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['object'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return apply_style(context)

class SalesInvoiceEmailSendView(ExtraContext, FormView):
    form_class = SendMailForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')
    extra_context = {
        'title': 'Send Invoice as PDF attatchment'
    }

    def get_initial(self):
        inv = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        
        return {
            'recepient': inv.customer.customer_email
        }
    def post(self,request, *args, **kwargs):
        resp = super(SalesInvoiceEmailSendView, self).post(
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
        #create pdf from the command line
        template = os.path.join("invoicing", "sales_invoice",
            'pdf.html')
        out_file = os.path.join(os.getcwd(), 'media', 'temp','out.pdf')
    
        context = {
            'object': SalesInvoice.objects.get(pk=self.kwargs['pk'])
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
        except:
            raise Exception('Error occured creating pdf')

        if os.path.isfile(out_file):
            msg.attach_file(out_file)
            msg.send()
            os.remove(out_file)

        # if the message is successful delete it.
        return resp