from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView, DetailView, DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
import os
from django.urls import reverse_lazy
from accounting.models import Journal
from invoicing.models import SalesConfig
from django_filters.views import FilterView
import filters
from utilities import ExtraContext
import models 
import forms 
from django.template import loader
from django.core.mail import send_mail

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class ReactCalendar(TemplateView):
    template_name = os.path.join('common_data','calendar.html')

#########################################################
#                  Organization Views                   #
#########################################################

class OrganizationCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.OrganizationForm
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Add Organization'
    }

class OrganizationUpdateView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.OrganizationForm
    model = models.Organization
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Update Organization details'
    }


class OrganizationDetailView(ExtraContext, DetailView):
    template_name = os.path.join('common_data', 'organization','detail.html')
    model = models.Organization
    

class OrganizationListView(ExtraContext, FilterView):
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

class IndividualCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.IndividualForm
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Add Individual'
    }

class IndividualUpdateView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.IndividualForm
    model = models.Individual
    success_url = reverse_lazy('invoicing:home')
    extra_context = {
        'title': 'Update Individual details'
    }


class IndividualDetailView(ExtraContext, DetailView):
    template_name = os.path.join('common_data', 'individual','detail.html')
    model = models.Individual
    

class IndividualListView(ExtraContext, FilterView):
    template_name = os.path.join('common_data', 'individual', 'list.html')
    queryset = models.Individual.objects.all()
    filterset_class = filters.IndividualFilter
    extra_context = {
        'title': 'List of Individuals',
        'new_link': reverse_lazy('base:organization-create')
    }


class WorkFlowView(TemplateView):
    template_name = os.path.join("common_data", "workflow.html")

class ReactTest(TemplateView):
    template_name = os.path.join("common_data", "react_test.html")

class GlobalConfigView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.GlobalConfig
    form_class = forms.GlobalConfigForm
    success_url = reverse_lazy('invoicing:home')#need a better page
    extra_context = {
        'title': 'Configure global application features'
    }

def config_JSON_API(request):
    return JsonResponse(SalesConfig.get_config_dict())

def get_logo_url(request):
    return JsonResponse({'url': SalesConfig.logo_url() })


class SendEmail(ExtraContext, FormView):
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
                [form.cleaned_data['recepient']])
            return resp
        return resp