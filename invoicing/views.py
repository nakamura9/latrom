# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from rest_framework import generics, viewsets
from django_filters.views import FilterView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.conf import settings
import forms

from common_data.utilities import ExtraContext, apply_style,load_config, Modal
from inventory.forms import QuickItemForm
from accounting.forms import TaxForm
from inventory.models import Item
from models import *
import filters
import serializers

class Home(LoginRequiredMixin, TemplateView):
    template_name = os.path.join("invoicing", "home.html")

#########################################
#           Customer Views              #
#########################################

class CustomerAPIViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

#No customer list, overlooked!

class CustomerCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    extra_context = {"title": "Create New Customer"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Customer
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.CustomerForm


class QuickCustomerCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    extra_context = {"title": "Create New Customer"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Customer
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.QuickCustomerForm


class CustomerUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Customer"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Customer
    form_class = forms.CustomerForm
    success_url = reverse_lazy("invoicing:home")


class CustomerListView(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Customers",
                    "new_link": reverse_lazy("invoicing:create-customer")}
    template_name = os.path.join("invoicing", "customer_list.html")
    filterset_class = filters.CustomerFilter
    paginate_by = 10

    def get_queryset(self):
        return Customer.objects.all().order_by('name')


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = Customer
    success_url = reverse_lazy('invoicing:customer-list')

#########################################
#           Customer Views              #
#########################################

class CreditNoteCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    '''Credit notes are created along with react on the front end.
    each note tracks each invoice item and returns the quantity 
    of the item that was returned. The data is shared as a single 
    urlencoded json string. this string is an object that maps 
    keys to values where the key is the primary key of the invoice item
    and the value is the quantity returned. Django handles the return on the
    database side of things.
    '''
    extra_context = {"title": "Create New Credit Note"}
    template_name = os.path.join("invoicing", "create_credit_note.html")
    model = CreditNote
    form_class = forms.CreditNoteForm
    success_url = reverse_lazy("invoicing:home")

    def post(self, request):
        resp = super(CreditNoteCreateView, self).post(request)
        data = json.loads(urllib.unquote(request.POST['returned-items']))
        for key in data.keys():
            iitem = InvoiceItem.objects.get(pk=key)
            iitem._return(data[key])
        return resp


class CreditNoteUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Credit Note"}
    template_name = os.path.join("invoicing", "create_credit_note.html")
    model = CreditNote
    form_class = forms.CreditNoteForm
    success_url = reverse_lazy("invoicing:home")


class CreditNoteListView(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Credit Notes",
                    "new_link": reverse_lazy("invoicing:credit-note-create")}
    template_name = os.path.join("invoicing", "credit_note_list.html")
    filterset_class = filters.CreditNoteFilter
    paginate_by = 10

    def get_queryset(self):
        return CreditNote.objects.all().order_by('date')

class CreditNoteDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('invoicing', 'credit_note.html')
    model = CreditNote
    
    def get_context_data(self, *args, **kwargs):
        context = super(CreditNoteDetailView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        context['title'] = 'Credit Note'
        return apply_style(context)

        
#########################################
#               Payment Views           #
#########################################


class PaymentAPIViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentsSerializer

class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = Payment
    success_url = reverse_lazy("invoicing:invoices-list")

class PaymentCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    extra_context = {"title": "Create New Payment"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Payment
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.PaymentForm

class PaymentUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Payment"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Payment
    form_class = forms.PaymentUpdateForm #some fields missing!
    success_url = reverse_lazy("invoicing:home")

class SalesRepDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:invoices-list")

class PaymentListView(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Payments",
                    "new_link": reverse_lazy("invoicing:create-payment")}
    template_name = os.path.join("invoicing", "payment_list.html")
    filterset_class = filters.PaymentFilter
    paginate_by = 10
    
    def get_queryset(self):
        return Payment.objects.all().order_by('date')


#########################################
#           Sales Rep Views             #
#########################################

class SalesRepCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    extra_context = {"title": "Add New Sales Rep."}
    template_name = os.path.join("common_data", "create_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.SalesRepForm


class SalesRepUpdateView(LoginRequiredMixin,ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Sales Rep."}
    template_name = os.path.join("common_data", "create_template.html")
    model = SalesRepresentative
    form_class = forms.SalesRepForm
    success_url = reverse_lazy("invoicing:home")


class SalesRepListView(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Sales Representatives",
                    "new_link": reverse_lazy("invoicing:create-sales-rep")}
    template_name = os.path.join("invoicing", "sales_rep_list.html")
    filterset_class = filters.SalesRepFilter
    paginate_by = 10

    def get_queryset(self):
        return SalesRepresentative.objects.all().order_by('pk')

class SalesRepsAPIViewSet(viewsets.ModelViewSet):
    queryset = SalesRepresentative.objects.all()
    serializer_class = serializers.SalesRepsSerializer


#########################################
#               Invoice Views           #
#########################################

class InvoiceAPIViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.filter(active=True)
    serializer_class = serializers.InvoiceSerializer

class InvoiceItemAPIViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = serializers.InvoiceItemSerializer


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = Invoice
    success_url = reverse_lazy("invoicing:invoices-list")

class InvoiceListView(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {"title": "Invoice List",
                    "new_link": reverse_lazy("invoicing:create-invoice")}
    template_name = os.path.join("invoicing", "invoice_list.html")
    filterset_class = filters.InvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(active=True).order_by('date_issued')
    

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = os.path.join("invoicing", "invoice_templates",
        'invoice.html')
    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        context['title'] = context.get('invoice_title', "Invoice")
        return apply_style(context)

        
class InvoiceCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Invoice",
        'modals': [
            Modal('Quick Tax', 
                '/accounting/api/tax/',
                TaxForm),
            Modal('Quick Customer',
                reverse_lazy('invoicing:quick-customer'),
                forms.QuickCustomerForm),
            Modal('Quick Item',
                reverse_lazy('inventory:quick-item'),
                QuickItemForm),
        ]
        }
            
    template_name = os.path.join("invoicing", "invoice_create.html")
    form_class = forms.InvoiceForm
    success_url = reverse_lazy("invoicing:home")
    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        apply_style(context)
        return context

    

    def post(self, request, *args, **kwargs):
        resp = super(InvoiceCreateView, self).post(request, *args, **kwargs)
        inv = Invoice.objects.latest("pk")
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            inv.add_item(Item.objects.get(pk=data['code']), 
                data['quantity'], data['discount'])
        
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        inv.create_entry()
        inv.update_inventory()

        return resp

class InvoiceUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    '''An update view is similar to a create view but it allows the 
    user to remove existing items from a quote using the list 
    of hidden inputs called 'removed_items[]'. '''

    extra_content = {"title": "Update Invoice"}
    template_name = os.path.join("invoicing", "invoice_update.html")
    model = Invoice
    form_class = forms.InvoiceUpdateForm
    success_url = reverse_lazy("invoicing:home")

    def post(self, request, *args, **kwargs):
        # implement check for whether an entry exists
        resp = super(InvoiceUpdateView, self).post(request, *args, **kwargs)
        inv = self.get_object()
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            inv.add_item(Item.objects.get(pk=data['code']), 
                data['quantity'],data['discount'])
        for pk in request.POST.getlist("removed_items[]"):
            InvoiceItem.objects.get(pk=pk).delete()
        
        return resp

#########################################
#                 Quote Views           #
#########################################

class QuoteAPIViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = serializers.QuoteSerializer

class QuoteItemAPIViewSet(viewsets.ModelViewSet):
    queryset = QuoteItem.objects.all()
    serializer_class = serializers.QuoteItemSerializer

class QuoteCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Quotation",
        'modals': [
            Modal('Quick Tax', 
                '/accounting/api/tax/',
                TaxForm),
            Modal('Quick Customer',
                reverse_lazy('invoicing:quick-customer'),
                forms.QuickCustomerForm),
            Modal('Quick Item',
                reverse_lazy('inventory:quick-item'),
                QuickItemForm),
        ]}
    template_name = os.path.join("invoicing", "quote_create.html")
    model = Quote
    form_class = forms.QuoteForm
    success_url = reverse_lazy("invoicing:home")

    def get_context_data(self, *args, **kwargs):
        context = super(QuoteCreateView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(QuoteCreateView, self).post(request, *args, **kwargs)
        quo = Quote.objects.latest("pk")
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            quo.add_item(Item.objects.get(pk=data['code']),
                data['quantity'], data['discount'])
        
        return resp


class QuoteUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    '''An update view is similar to a create view but it allows the 
    user to remove existing items from a quote using the list 
    of hidden inputs called 'removed_items[]'. '''
    
    extra_content = {"title": "Update an existing Quotation"}
    template_name = os.path.join("invoicing", "quote_update.html")
    model = Quote
    form_class = forms.QuoteForm
    success_url = reverse_lazy("invoicing:home")

    def post(self, request, *args, **kwargs):
        resp = super(QuoteUpdateView, self).post(request, *args, **kwargs)
        quo = Quote.objects.latest("pk")
        # add update prices toggle for for each quote item item
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            quo.quoteitem_set.create(
                quantity=data['quantity'],
                item=Item.objects.get(pk=data['code']),
                discount=data['discount'])

        for pk in request.POST.getlist("removed_items[]"):
            QuoteItem.objects.get(pk=pk).delete()
        
        return resp

class QuoteDetailView(LoginRequiredMixin, DetailView):
    model = Quote
    template_name = os.path.join("invoicing", "quote_templates",
        'quote.html')
    
    def get_context_data(self, *args, **kwargs):
        context = super(QuoteDetailView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        context['title'] = 'Quotation'
        return apply_style(context)


class QuoteListView(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {
        "title": "Quotation List",
        "new_link": reverse_lazy("invoicing:create-quote")
        }
    template_name = os.path.join("invoicing", "quote_list.html")
    filterset_class = filters.QuoteFilter
    paginate_by = 10

    def get_queryset(self):
        return Quote.objects.all().order_by('date')
    
class QuoteDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = Quote
    success_url = reverse_lazy("invoicing:quote-list")


#########################################
#               Receipt Views           #
#########################################

class ReceiptDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = os.path.join("invoicing", "receipt_templates",
        'receipt.html')
    
    def get_context_data(self, *args, **kwargs):
        context = super(ReceiptDetailView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        context['title'] = 'Receipt'
        return apply_style(context)


class InvoiceReceiptDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = os.path.join("invoicing", "receipt_templates",
        'invoice_receipt.html')
    
    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceReceiptDetailView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        context['title'] = 'Receipt'
        return apply_style(context)


#########################################################
#                  Template Views                       #
#########################################################


class ConfigView(LoginRequiredMixin, FormView):
    template_name = os.path.join("invoicing", "config.html")
    form_class = forms.ConfigForm
    
    def get_context_data(self):
        context = super(ConfigView, self).get_context_data()
        config = load_config() 
        if config.get('logo', None):
            context['logo']='/media/logo/' + config['logo']
        return context

    def get_initial(self):
        return load_config()

    def post(self, request):
        data = request.POST.dict()
        del data["csrfmiddlewaretoken"]
        config = load_config()
        if config.get('logo', '') != "" and data.get('logo', '') == "":
            data['logo'] = config['logo']
        if  request.FILES.get('logo', None):
            file = request.FILES['logo']
            filename = file.name
            path = os.path.join(settings.MEDIA_ROOT, 'logo', filename)
            data['logo'] = filename
            with open(path, 'wb+') as img:
                for chunk in file.chunks():
                    img.write(chunk)
            
        json.dump(data, open("config.json", 'w'))
        return HttpResponseRedirect(reverse_lazy("invoicing:home"))

@login_required
def create_payment_from_invoice(request, pk=None):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.create_payment()
    return HttpResponseRedirect(reverse('invoicing:home'))


@login_required
def create_invoice_from_quote(request, pk=None):
    quote = get_object_or_404(Quote, pk=pk)
    quote.create_invoice()
    return HttpResponseRedirect(reverse('invoicing:home'))