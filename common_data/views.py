import os

from django.core.mail import EmailMessage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import (DeleteView, DetailView, FormView, ListView,
                                  TemplateView)
from django.views.generic.edit import CreateView, FormView, UpdateView
from django_filters.views import FilterView
from wkhtmltopdf import utils as pdf_tools
from wkhtmltopdf.views import PDFTemplateView

from accounting.models import Journal
from common_data import filters, models
from common_data.forms import SendMailForm
from common_data.models import GlobalConfig
from common_data.utilities import ContextMixin, apply_style
from invoicing.models import SalesConfig
from rest_framework.generics import RetrieveAPIView
from common_data import serializers 
from django.contrib.auth.models import User
from . import forms


class PaginationMixin(object):
    '''quick and dirty mixin to support pagination on filterviews '''
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        if not self.queryset and hasattr(self, 'get_queryset'):
            self.queryset = self.get_queryset()
            
        filter = self.filterset_class(self.request.GET, queryset=self.queryset)
        object_list = filter.qs
        
        
        if not self.paginate_by:
            self.paginate_by = 10

        p = Paginator(object_list, self.paginate_by)

        page = self.request.GET.get('page')
        try:
            qs_ = p.page(page)
        except PageNotAnInteger:
            #gets first page
            qs_ = p.page(1)
        except EmptyPage:
            #gets last page 
            qs_ = p.page(p.num_pages)

        context['object_list'] = qs_
        context['paginator'] = p
        context['is_paginated'] = True
        context['page_obj'] = page

        return context

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

#########################################################
#                  Organization Views                   #
#########################################################

class OrganizationCreateView(ContextMixin, LoginRequiredMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.OrganizationForm
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Add Organization'
    }

class OrganizationUpdateView(ContextMixin, LoginRequiredMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.OrganizationForm
    model = models.Organization
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Update Organization details'
    }


class OrganizationDetailView(ContextMixin, LoginRequiredMixin, DetailView):
    template_name = os.path.join('common_data', 'organization','detail.html')
    model = models.Organization
    

class OrganizationListView(ContextMixin, PaginationMixin,  LoginRequiredMixin, 
        FilterView):
    template_name = os.path.join('common_data', 'organization', 'list.html')
    queryset = models.Organization.objects.all()
    filterset_class = filters.OrganizationFilter
    extra_context = {
        'title': 'Organization List',
        'new_link': reverse_lazy('base:organization-create')
    }



#########################################################
#                    Individual Views                   #
#########################################################

class IndividualCreateView(ContextMixin,  LoginRequiredMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.IndividualForm
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Add Individual',
        'description': 'Register a human that interacts with your business either as a customer or supplier or an employee of one of the two.',
        'related_links': [{
            'name': 'Add Organization',
            'url': '/base/organization/create'
        }]
    }

class IndividualUpdateView(ContextMixin,  LoginRequiredMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.IndividualForm
    model = models.Individual
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Update Individual details',
        'description': 'Register a human that interacts with your business either as a customer or supplier or an employee of one of the two.',
        'related_links': [{
            'name': 'Add Organization',
            'url': '/base/organization/create'
        }]
    }


class IndividualDetailView(ContextMixin,  LoginRequiredMixin, DetailView):
    template_name = os.path.join('common_data', 'individual','detail.html')
    model = models.Individual
    

class IndividualListView(ContextMixin, PaginationMixin,  LoginRequiredMixin, 
        FilterView):
    template_name = os.path.join('common_data', 'individual', 'list.html')
    queryset = models.Individual.objects.all()
    filterset_class = filters.IndividualFilter
    extra_context = {
        'title': 'List of Individuals',
        'new_link': reverse_lazy('base:individual-create')
    }


class WorkFlowView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join("common_data", "workflow.html")

class ReactTestView(TemplateView):
    template_name = os.path.join("common_data", "react_test.html")

class AboutView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join("common_data", "about.html")



class GlobalConfigView(ContextMixin,  LoginRequiredMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.GlobalConfig
    form_class = forms.GlobalConfigForm
    success_url = reverse_lazy('invoicing:home')#need a better page
    extra_context = {
        'title': 'Configure global application features'
    }

class AuthenticationView(FormView):
    # TODO test, add features to use as a plugin for views that require
    # authentication
    form_class = forms.AuthenticateForm
    template_name = os.path.join('common_data', 'authenticate.html')
    success_url = "/base/workflow"


def get_logo_url(request):
    return JsonResponse({'url': SalesConfig.logo_url() })


class SendEmail(ContextMixin,  LoginRequiredMixin, FormView):
    template_name = CREATE_TEMPLATE
    form_class = forms.SendMailForm
    success_url= reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Compose New Email'
    }

    def post(self, request):
        resp = super(SendEmail, self).post(request)
        form = self.form_class(request.POST)
        config = models.GlobalConfig.objects.first()
        if form.is_valid():
            send_mail(
                form.cleaned_data['subject'],
                form.cleaned_data['content'],
                config.email_user,
                [form.cleaned_data['recipient']])
            return resp
        return resp

class EmailPlusPDFView(ContextMixin, FormView):
    form_class = SendMailForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = None
    pdf_template_name = None
    inv_class = None
    extra_context = {
        'title': 'Send Invoice as PDF attatchment'
    }

    def get_initial(self):
        if not self.inv_class:
            raise ValueError('Improperly configured, needs an inv_class attribute')
        inv = self.inv_class.objects.get(pk=self.kwargs['pk'])
        return {
            'recipient': inv.customer.customer_email
        }
    
    def post(self,request, *args, **kwargs):
        resp = super(EmailPlusPDFView, self).post(
            request, *args, **kwargs)
        form = self.form_class(request.POST)
        
        if not form.is_valid():
            return resp
        
        config = GlobalConfig.objects.get(pk=1)
        msg = EmailMessage(
            subject=form.cleaned_data['subject'],
            body = form.cleaned_data['content'],
            from_email=config.email_user,
            to=[form.cleaned_data['recipient']]
        )
        if not self.pdf_template_name:
            raise ValueError('Improperly configured. Needs pdf_template_name attribute.')

        out_file = os.path.join(os.getcwd(), 'media', 'temp','out.pdf')
    
        context = {
            'object': self.inv_class.objects.get(pk=self.kwargs['pk'])
        }
        context.update(SalesConfig.objects.first().__dict__)
        options = {
            'output': out_file
        }
        try:
            pdf_tools.render_pdf_from_template(
                self.pdf_template_name, None, None, 
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


class UserAPIView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()


def get_current_user(request):
    if request.user:
        return JsonResponse({
            'pk': request.user.pk,
            'name': request.user.username
            })

    return JsonResponse({'pk': None})

