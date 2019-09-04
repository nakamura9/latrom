import random

import os
import datetime
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
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
from messaging.views import UserEmailConfiguredMixin
from messaging.models import Email, UserProfile
from messaging.forms import AxiosEmailForm

from accounting.models import Journal
from common_data import filters, models, serializers, forms
from common_data.forms import SendMailForm
from common_data.models import GlobalConfig, Organization
from common_data.utilities import (ContextMixin, 
                                    apply_style, 
                                    MultiPageDocument, 
                                    MultiPagePDFDocument,
                                    ConfigWizardBase)
from invoicing.models import SalesConfig
from rest_framework.generics import RetrieveAPIView, ListAPIView
from django.contrib.auth.models import User
from django.apps import apps
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from background_task.models_completed import CompletedTask
import services
from messaging.email_api.email import EmailSMTP
from messaging.forms import EmailForm, PrePopulatedEmailForm
import json 

class PaginationMixin(object):
    '''quick and dirty mixin to support pagination on filterviews '''
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        if not self.queryset and hasattr(self, 'get_queryset'):
            self.queryset = self.get_queryset()
            
        filter = self.filterset_class(self.request.GET, queryset=self.queryset)
        object_list = filter.qs
        
        
        if not self.paginate_by:
            self.paginate_by = 20

        p = Paginator(object_list, self.paginate_by)

        page_str = self.request.GET.get('page')
        try:
            page = p.page(page_str)
        except PageNotAnInteger:
            #gets first page
            page = p.page(1)
        except EmptyPage:
            #gets last page 
            page = p.page(p.num_pages)

        context['object_list'] = page
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
    extra_context = {
        'title': 'Add Organization'
    }


class OrganizationUpdateView(ContextMixin, LoginRequiredMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.OrganizationForm
    model = models.Organization
    extra_context = {
        'title': 'Update Organization details'
    }


class OrganizationDetailView(ContextMixin, LoginRequiredMixin, DetailView):
    template_name = os.path.join('common_data', 'organization','detail.html')
    model = models.Organization
    

class OrganizationListView(ContextMixin, 
                            PaginationMixin,  
                            LoginRequiredMixin, 
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

    def get(self, *args, **kwargs):
        if not GlobalConfig.objects.first().is_configured:
            return HttpResponseRedirect(reverse_lazy('base:config-wizard'))
        else:
            return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        date = datetime.date.today()
        context["month"] = "{}/{}".format(date.year, date.month)
        return context

class ReactTestView(TemplateView):
    template_name = os.path.join("common_data", "react_test.html")


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join("common_data", "about.html")



class GlobalConfigView(ContextMixin,  LoginRequiredMixin, UpdateView):
    template_name = os.path.join("common_data", "config.html")
    model = models.GlobalConfig
    form_class = forms.GlobalConfigForm
    success_url = '/base/workflow'
    extra_context = {
        'title': 'Configure global application features'
    }

    def get_initial(self):
        if self.object.organization:
            return {
                'organization_name': self.object.organization.legal_name,
                'organization_logo': self.object.logo,
                'organization_address': \
                    self.object.organization.business_address,
                'organization_email': self.object.organization.email,
                'organization_phone': self.object.organization.phone,
                'organization_website': self.object.organization.website,
                'organization_business_partner_number': \
                    self.object.organization.bp_number
            }

        return None

    def form_valid(self, form):
        resp = super().form_valid(form)

        if self.object.organization:
            org = self.object.organization
        else:
            org = Organization()

        org.legal_name = form.cleaned_data['organization_name'] 
        org.business_address = form.cleaned_data['organization_address']
        org.website = form.cleaned_data['organization_website']
        org.bp_number = \
            form.cleaned_data['organization_business_partner_number']
        org.email = form.cleaned_data['organization_email']
        org.phone = form.cleaned_data['organization_phone']
        org.logo = form.cleaned_data['organization_logo']

        org.save()
        self.object.organization = org
        self.object.save()

        return resp

class AuthenticationView(FormView):
    # TODO add features to use as a plugin for views that require
    # authentication
    form_class = forms.AuthenticateForm
    template_name = os.path.join('common_data', 'authenticate.html')
    success_url = "/base/workflow"


def get_logo_url(request):
    return JsonResponse({'url': models.GlobalConfig.logo_url() })


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

class PDFException(Exception):
    pass

class EmailPlusPDFView(UserEmailConfiguredMixin,
                       CreateView, 
                       MultiPagePDFDocument):
    '''THe pagination is optional, it will be ignored '''
    form_class = PrePopulatedEmailForm #SendMailForm
    template_name = os.path.join('messaging', 'email', 'compose.html')
    success_url = None
    pdf_template_name = None
    inv_class = None
    
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
        
        try:
            return super().get(*args, **kwargs)
        except PDFException:
            return HttpResponse('<p>An error occurred rendering the PDF</p>')
        
        except Exception as e:
            raise e

    def get_initial(self):
        if not self.inv_class:
            raise ValueError('Improperly configured, needs an inv_class attribute')

        inv = self.inv_class.objects.get(pk=self.kwargs['pk'])
        

        out_file = os.path.join(os.getcwd(), 'media', 'temp','out.pdf')
        if os.path.exists(out_file):
            out_file = os.path.join(
                os.getcwd(), 
                'media', 
                'temp',
                f'out_{random.randint(1, 100000)}.pdf')
            
        #use the context for pagination and the object
        obj = self.inv_class.objects.get(pk=self.kwargs['pk'])
        context = {
            'object': obj,
        }
        config = GlobalConfig.objects.first()
        context.update(config.__dict__)
        context.update({
            'logo': config.logo,
            'logo_width': config.logo_width,
            'business_name': config.business_name,
            'business_address': config.business_address
        })
        options = {
            'output': out_file
        }
        try:
            pdf_tools.render_pdf_from_template(
                self.pdf_template_name, None, None, 
                apply_style(context),
                cmd_options=options)

        except Exception as e:
            print('Error occured creating pdf %s' % e )
            raise PDFException()
        
        return {
            'owner': self.request.user.pk,
            'folder': 'sent',
            'attachment_path': out_file
        }
    
    def post(self,request, *args, **kwargs):
        resp = super(EmailPlusPDFView, self).post(
            request, *args, **kwargs)
        form = self.form_class(request.POST)
        
        if not form.is_valid():
            return resp

        
        u = UserProfile.objects.get(user=self.request.user)
        e = EmailSMTP(u)

        self.object.attachment.name = form.cleaned_data['attachment_path']
        self.object.save()

        e.send_email_with_attachment(
            form.cleaned_data['subject'],
            form.cleaned_data['to'].address,
            form.cleaned_data['body'],
            open(form.cleaned_data['attachment_path'], 'rb'),
            html=True
            )

        if not self.pdf_template_name:
            raise ValueError('Improperly configured. Needs pdf_template_name attribute.')

        if os.path.exists(form.cleaned_data['attachment_path']):
            os.remove(form.cleaned_data['attachment_path'])

        return resp


class UserAPIView(ListAPIView):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    model = User

class UserDetailAPIView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    model = User


def get_current_user(request):
    if request.user:
        return JsonResponse({
            'pk': request.user.pk,
            'name': request.user.username
            })

    return JsonResponse({'pk': None})

class LicenseErrorPage(TemplateView):
    template_name = os.path.join('common_data', 'licenses_error.html')

class LicenseFeaturesErrorPage(TemplateView):
    template_name = os.path.join('common_data', 'license_error_features.html')

class UsersErrorPage(TemplateView):
    template_name = os.path.join('common_data', 'users_error.html')

NOTE_TARGET = {
    'work_order': services.models.ServiceWorkOrder
}

def create_note(request):
    global NOTE_TARGET 
    '''This simple function allows a large variety of objects to support 
    notes without modification. The global note target dictionary mapps 
    strings of notes with their corresponding objects to which the notes are 
    applied. Thus each note request must have an author, a message and 
    identification for the target namely its classname and the objects primary 
    key'''
    author = User.objects.get(pk=request.POST['author'])
    note = models.Note.objects.create(
        author = author,
        note = request.POST['note']
    )

    NOTE_TARGET[request.POST['target']].objects.get(
        pk=request.POST['target_id']
    ).notes.add(note)

    return JsonResponse({'status': 'ok'})


class PDFDetailView(PDFTemplateView):
    model = None
    context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.model.objects.get(pk=self.kwargs['pk'])
        context.update(self.context)
        return context

def get_model_latest(request, app=None, model_name=None):
    try:
        model = apps.get_model(app_label=app, model_name=model_name)
        latest = model.objects.latest('pk')
    except:
        return JsonResponse({'data': -1})

    
    return JsonResponse({'data': [latest.pk, str(latest)]})


class ConfigWizard(ConfigWizardBase):
    template_name = os.path.join('common_data', 'wizard.html')
    form_list = [forms.GlobalConfigForm]
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'logo'))
    config_class = GlobalConfig
    success_url = reverse_lazy('base:workflow')
    
    #TODO fix logo and file handling
    def post(self, request, *args, **kwargs):

        return super().post(request, *args, **kwargs)
    def done(self, form_list, **kwargs):
        """Because there is only one form"""
        for form in form_list:
            form.save()
        return super().done(form_list, **kwargs)
    

def reset_license_check(request):
    #delete the hash
    config = GlobalConfig.objects.first()
    
    #remove all the completed tasks
    CompletedTask.objects.filter(
        task_hash=config.verification_task_id).delete()

    config.verification_task_id = ''
    config.save()

    return HttpResponseRedirect('/login')

def document_notes_api(request, document=None, id=None):
    notes =[]
    
    if document == 'service':
        doc = services.models.ServiceWorkOrder.objects.get(pk=id)
        notes = [{'note': i.note, 'author': i.author.pk} \
                    for i in doc.notes.all()]
    
    return JsonResponse(notes, safe=False)


class ReportBlankView(TemplateView):
    template_name = os.path.join('common_data', 'reports', 'blank.html')

def current_db(request):
    #TODO support other database types
    with open(os.path.join('database', 'config.json')) as fil:
        config = json.load(fil)
        return JsonResponse({
            'db': config['current'].strip('sqlite3')
        })