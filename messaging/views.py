import os

from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import RetrieveAPIView
import datetime 
from messaging import models, forms, serializers


class InboxView(LoginRequiredMixin, DetailView):
    # a list of threads not messages 
    # includes a panel for notifications 
    template_name = os.path.join('messaging', 'inbox.html')
    model = models.Inbox

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        try:
            usr = User.objects.get(pk=pk)
        except:
            self.object = None
            return None
        else:
            try:
                self.object = models.Inbox.objects.get(user=usr)
                return self.object
            except:
                self.object = models.Inbox.objects.create(
                    user=usr
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
        self.object.open_notification()

        return resp

class ComposeMessageView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('messaging', 'message_compose.html')
    form_class = forms.MessageForm
    model = models.Message
    success_url = '/base/workflow'

    def get_initial(self):
        return {
            'sender': self.request.user.pk
        }

    def post(self, request):
        resp = super().post(request)
        sender = models.Dispatcher(self.object)
        sender.dispatch()
        return resp

class MessageThreadView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('messaging', 'message_thread.html')
    model = models.MessageThread

    
def reply_message(request, pk=None):
    msg = models.Message.objects.get(pk=pk)
    reply = models.Message.objects.create(
        recipient=msg.sender,
        sender=request.user,
        subject=msg.subject,
        body=request.POST['reply']
    )
    sender = models.Dispatcher(reply)
    sender.dispatch()
    return JsonResponse({'status': 'ok'})


def inbox_counter(request):
    return JsonResponse({'count': request.user.inbox.total_in})


class MessageThreadAPIView(RetrieveAPIView):
    serializer_class = serializers.MessageThreadSerializer
    queryset = models.MessageThread.objects.all()
    

class MessageAPIView(RetrieveAPIView):
    serializer_class = serializers.MessageSerializer
    queryset = models.Message.objects.all()
    

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
    return HttpResponseRedirect(
        '/messaging/inbox/{}'.format(thread.inbox_set.first().pk))