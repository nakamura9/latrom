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
from django.contrib.auth.models import User
from common_data.utilities.mixins import ContextMixin
import os
import json
import urllib


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('messaging', 'dashboard.html')


class InboxView(LoginRequiredMixin, TemplateView):
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


class ComposeEmailView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('messaging', 'email', 'compose.html')
    form_class = forms.EmailForm
    model = models.Email
    success_url = "/messaging/inbox/"

    def get_initial(self):
        return {
            'sender': self.request.user.pk
        }



def notification_service(request):
    try:
        unread = models.Notification.objects.filter(
            read=False, user=request.user)
    except:
        return JsonResponse({'latest': {}, 'unread': 0})

    if unread.count() == 0:
        return JsonResponse({'latest': {}, 'unread': 0})

    latest = unread.latest('timestamp')
    data = {
        'latest': {
            'title': latest.title,
            'message': latest.message,
            'action': latest.action,
            'id': latest.pk,
            'stamp': latest.timestamp.strftime("%d, %B, %Y")
        },
        'unread': unread.count()
    }
    #latest.read = True
    latest.save()

    return JsonResponse(data)


def mark_notification_read(request, pk=None):
    notification = get_object_or_404(models.Notification, pk=pk)
    notification.read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


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
            'user': self.request.user.pk
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
        return models.Group.objects.filter(Q(Q(admin=self.request.user) |
                                           Q(
                                               participants__username=self.request.user.username)) & Q(active=True))


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


class BubbleAPIViewset(ModelViewSet):
    queryset = models.Bubble.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return serializers.BubbleReadSerializer

        return serializers.BubbleSerializer


class GroupAPIViewset(ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ChatAPIViewset(ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer

class EmailAPIViewset(ModelViewSet):
    queryset = models.Email.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return serializers.EmailRetrieveSerializer

        return serializers.EmailSerializer



def close_chat(request, pk=None):
    chat = get_object_or_404(models.Chat, pk=pk)
    chat.archived=True
    chat.save()

    return HttpResponseRedirect(reverse('messaging:chat-list'))


def close_group(request, pk=None):
    group = get_object_or_404(models.Group, pk=pk)
    group.active=False
    group.save()

    return HttpResponseRedirect(reverse('messaging:group-list'))

class InboxAPIView(APIView):
    def get(self, request):
        #maybe try to sync latest emails here?
        profile = models.UserProfile.objects.get(user=request.user)
        # include copy 
        emails = models.Email.objects.filter(to__address=profile.email_address)
        data = serializers.EmailRetrieveSerializer(emails, many=True).data
        return Response(data)

class DraftsAPIView(APIView):
    def get(self, request):
        emails = models.Email.objects.filter(
            sender=request.user,
            sent=False)
        data = serializers.EmailRetrieveSerializer(emails, many=True).data
        return Response(data)


class SentAPIView(APIView):
    def get(self, request):
        emails = models.Email.objects.filter(
            sender=request.user,
            sent=True)

        data = serializers.EmailRetrieveSerializer(emails, many=True).data
        return Response(data)