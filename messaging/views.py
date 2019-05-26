from django.views.generic import TemplateView, DetailView, ListView

from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
import datetime 
from messaging import models, forms, serializers
from django.db.models import Q
from django.contrib.auth.models import User
import os
import json
import urllib

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('messaging', 'dashboard.html')
    
class InboxView(LoginRequiredMixin, DetailView):
    # a list of threads not messages 
    # includes a panel for notifications 
    template_name = os.path.join('messaging', 'inbox.html')
    model = models.Inbox

    def get_object(self, *args, **kwargs):
        try:
            self.object = models.Inbox.objects.get(user=self.request.user)
            return self.object
        except:
            self.object = models.Inbox.objects.create(
                user=self.request.user
            )
            return self.object
                
class MessageDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'message_detail.html')
    model = models.Message

    def get(self, *args, **kwargs):
        resp = super().get(*args, **kwargs)
        self.object.open_message()


        return resp

class NotificationDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'notification_detail.html')
    model = models.Notification

    def get(self, *args, **kwargs):
        resp = super().get(*args, **kwargs)
        self.object.open()

        return resp

class ComposeMessageView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('messaging', 'message_compose.html')
    form_class = forms.MessageForm
    model = models.Message
    success_url = "/messaging/inbox/"

    def get_initial(self):
        return {
            'sender': self.request.user.pk
        }

    def post(self, request):
        resp = super().post(request)
        if not self.object:
            return resp
        sender = models.Dispatcher(self.object)
        sender.dispatch()
        return resp

class MessageThreadAPIView(RetrieveAPIView):
    serializer_class = serializers.MessageThreadSerializer
    queryset = models.MessageThread.objects.all()
    

class MessageAPIView(RetrieveAPIView):
    serializer_class = serializers.MessageSerializer
    queryset = models.Message.objects.all()

    
def reply_message(request, pk=None):
    msg = models.Message.objects.get(pk=pk)
    reply = models.Message.objects.create(
        recipient=msg.sender,
        sender=request.user,
        subject=msg.subject,
        body=request.POST['reply'],
        thread=msg.thread
    )
    sender = models.Dispatcher(reply)
    sender.dispatch()
    return JsonResponse({'status': 'ok'})


def inbox_counter(request):
    return JsonResponse({'count': request.user.inbox.total_in})
    

def mark_as_read(request, pk=None):
    msg = models.Message.objects.get(pk=pk)
    msg.read=True
    msg.opened_timestamp = datetime.datetime.now()
    msg.save()
    return JsonResponse({'status': 'ok'})


def close_thread(request, pk=None):
    thread = models.MessageThread.objects.get(pk=pk)
    thread.closed = True
    thread.save()
    return HttpResponseRedirect('/messaging/inbox')


def notification_service(request):
    try:
        unread = models.Notification.objects.filter(read=False, user=request.user)
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
    template_name = os.path.join('messaging', 'chat','chats.html')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chats'] = models.Chat.objects.filter(
            Q(
                Q(sender=self.request.user) | 
                Q(receiver=self.request.user)
            ) & Q(archived=False)
        )
        return context

class NewChatView(TemplateView):
    template_name = os.path.join('messaging', 'chat','users.html')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        return context
    

class ChatView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'chat','thread.html')
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
        return models.Group.objects.filter(Q(admin=self.request.user) | 
            Q(participants__username=self.request.user.username))

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

def create_bubble(request):
    pass