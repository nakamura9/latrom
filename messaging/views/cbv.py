from django.views.generic import TemplateView, DetailView, ListView

from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
import datetime
from messaging import models, forms, serializers
from django.db.models import Q
from latrom.settings import MEDIA_ROOT
from common_data.utilities.mixins import ContextMixin
import os
import json
import urllib
from messaging.email_api.email import EmailSMTP
from draftjs_exporter.html import HTML as exporterHTML
from ..email_api.service import sync_service
from cryptography.fernet import Fernet
from messaging.email_api.secrets import get_secret_key


class UserEmailConfiguredMixin(object):
    def get(self, *args, **kwargs):
        if models.UserProfile.objects.filter(user=self.request.user).exists():
            return super().get(*args, **kwargs)
        return HttpResponseRedirect('/messaging/config')


class Dashboard(LoginRequiredMixin, UserEmailConfiguredMixin, TemplateView):
    template_name = os.path.join('messaging', 'dashboard.html')

    def get(self, request, *args, **kwargs):
        sync_service(request.user)
        return super().get(request, *args, **kwargs)


class InboxView(LoginRequiredMixin, UserEmailConfiguredMixin, TemplateView):
    # a list of threads not messages
    # includes a panel for notifications
    template_name = os.path.join('messaging', 'email', 'inbox.html')


class NotificationDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'notification_detail.html')
    model = models.Notification

    def get(self, *args, **kwargs):
        resp = super().get(*args, **kwargs)
        self.object.open()

        return resp

class ComposeEmailView(LoginRequiredMixin, 
                        UserEmailConfiguredMixin, 
                        CreateView):
    template_name = os.path.join('messaging', 'email', 'compose.html')
    form_class = forms.EmailForm
    model = models.Email
    success_url = "/messaging/inbox/"

    def get_initial(self):
        return {
            'owner': self.request.user.pk,
            'folder': 'sent'
        }

    def form_valid(self, form):
        data = form.cleaned_data

        #add all to addresses to email object
        # add all address to smtp send

        to_data = self.request.POST['to']
        raw_cc_data = self.request.POST['copy']
        raw_bcc_data = self.request.POST['blind_carbon_copy']
        
        to = models.EmailAddress.objects.get(pk=to_data.split('-')[0])
        
        cc_data = json.loads(urllib.parse.unquote(raw_cc_data))
        bcc_data = json.loads(urllib.parse.unquote(raw_bcc_data))
        cc = []
        bcc = []

        for addr in cc_data:
            cc.append(models.EmailAddress.objects.get(pk=addr.split('-')[0]))

        for addr in bcc_data:
            bcc.append(models.EmailAddress.objects.get(pk=addr.split('-')[0]))

        resp = super().form_valid(form)

        self.object.to = to
        self.object.copy.add(*cc)
        self.object.blind_copy.add(*bcc)
        self.object.save()

        profile = models.UserProfile.objects.get(user=self.request.user)
        g = EmailSMTP(profile)

        if data['save_as_draft']:
            self.object.folder = 'drafts'
            self.object.save()
            return resp

        if(data.get('attachment', None)):# and os.path.exists(path):
            path = os.path.join(
                MEDIA_ROOT, 
                'messaging', 
                data['attachment'].name)
            
            g.send_email_with_attachment(
                data['subject'], 
                to.address,
                [i.address for i in cc],
                [i.address for i in bcc],
                data['body'], 
                data['attachment'], html=True)
        else:
            g.send_html_email(
                data['subject'], 
                to.address, 
                [i.address for i in cc],
                [i.address for i in bcc],
                data['body'])
        
        self.object.folder='sent'
        self.object.save()

        return resp

class DraftEmailUpdateView(LoginRequiredMixin, 
                            UserEmailConfiguredMixin, 
                            UpdateView):
    
    template_name = os.path.join('messaging', 'email', 'update_draft.html')
    form_class=forms.EmailForm
    model=models.Email
    success_url = "/messaging/inbox/"

    def form_valid(self, form):
        #slightly different from compose 'form_valid'
        data = form.cleaned_data

        to_data = self.request.POST['to']
        raw_cc_data = self.request.POST['copy']
        raw_bcc_data = self.request.POST['blind_carbon_copy']
        
        #string lacking a pk 
        if('-' not in to_data):
            to = models.EmailAddress.get_address(to_data)
        else:
            #in case another receiver has been chosen
            to = models.EmailAddress.objects.get(pk=to_data.split('-')[0])

        
        cc_data = json.loads(urllib.parse.unquote(raw_cc_data))
        bcc_data = json.loads(urllib.parse.unquote(raw_bcc_data))
        
        cc = []
        bcc = []
        for addr in cc_data:
            if('-' not in addr):
                cc.append(models.EmailAddress.get_address(addr))
            else:
                address = models.EmailAddress.objects.get(pk=addr.split('-')[0])
                cc.append(address)

        for addr in bcc_data:
            if('-' not in addr):
                bcc.append(models.EmailAddress.get_address(addr))
            else:
                address = models.EmailAddress.objects.get(pk=addr.split('-')[0])
                bcc.append(address)
  
        resp = super().form_valid(form)

        self.object.to = to
        # remove all m2m before rebuilding relations 
        for a in self.object.copy.all():
            self.object.copy.remove(a)

        self.object.copy.add(*cc)
        
        for a in self.object.blind_copy.all():
            self.object.blind_copy.remove(a)

        self.object.blind_copy.add(*bcc)

        self.object.save()

        profile = models.UserProfile.objects.get(user=self.request.user)
        g = EmailSMTP(profile)

        if data['save_as_draft']:
            self.object.folder = 'drafts'
            self.object.save()
            return resp

        if(data.get('attachment', None)):# and os.path.exists(path):
            path = os.path.join(
                MEDIA_ROOT, 
                'messaging', 
                data['attachment'].name)
            
            g.send_email_with_attachment(
                data['subject'], 
                to.address,
                [i.address for i in cc],
                [i.address for i in bcc],
                data['body'], 
                data['attachment'], html=True)
        else:
            g.send_html_email(
                data['subject'], 
                to.address, 
                [i.address for i in cc],
                [i.address for i in bcc],
                data['body'])

        return resp


class ChatListView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('messaging', 'chat', 'chats.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chats'] = models.Chat.objects.filter(
            Q(
                Q(sender=self.request.user) |
                Q(receiver=self.request.user)
            ) & Q(archived=False)
        )
        return context

class UserProfileView(ContextMixin, LoginRequiredMixin, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    extra_context = {
        'title': 'Configure User Email Settings'
    }

    success_url = "/messaging/dashboard/"

    def get_initial(self):
        
        return {
            'user': self.request.user.pk,
            'email_password': self.object.get_plaintext_password()
        }

    form_class = forms.UserProfileForm

    def get_object(self, *args, **kwargs):
        usr = self.request.user
        if models.UserProfile.objects.filter(user=usr).exists():
            return models.UserProfile.objects.get(user=usr)
        
        profile = models.UserProfile.objects.create(
            user=usr,
            email_address='test@email.com',
            email_password="password"
            )

        return profile


class NewChatView(TemplateView):
    template_name = os.path.join('messaging', 'chat', 'users.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        return context


class ChatView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'chat', 'thread.html')
    model = models.Chat


class GroupCreateView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('messaging', 'chat', 'group_create.html')
    model = models.Group
    form_class = forms.GroupForm

    def get_initial(self):
        return {
            'admin': self.request.user.pk
        }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(
            request.POST['participants']))
        for person in data:
            pk = person.split('-')[0]
            self.object.participants.add(User.objects.get(pk=pk))

        self.object.save()

        return resp


class GroupView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'chat', 'group_detail.html')
    model = models.Group


class GroupListView(LoginRequiredMixin, ListView):
    template_name = os.path.join('messaging', 'chat', 'group_list.html')

    def get_queryset(self, *args, **kwargs):
        return models.Group.objects.filter(Q(
            Q(admin=self.request.user) | 
            Q(participants__username=self.request.user.username)) & 
            Q(active=True))


def create_chat(request, user=None):
    filters = Q(Q(sender=request.user) &
                Q(receiver=User.objects.get(pk=user)))
    if models.Chat.objects.filter(filters).exists():
        chat = models.Chat.objects.get(filters)

    else:
        chat = models.Chat.objects.create(
            sender=request.user,
            receiver=User.objects.get(pk=user)
        )

    return HttpResponseRedirect(reverse('messaging:chat', kwargs={
        'pk': chat.pk
    }))

class EmailAddressCreateView(ContextMixin, CreateView):
    form_class = forms.EmailAddressForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = '/messaging/dashboard/'
    extra_context = {
        'title': 'Create Email Address'
    }