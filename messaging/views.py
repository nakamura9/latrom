import os

from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User

from messaging import models
from messaging import forms 


class InboxView(DetailView):
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
                
class MessageDetailView(DetailView):
    template_name = os.path.join('messaging', 'message_detail.html')
    model = models.Message

class NotificationDetailView(DetailView):
    template_name = os.path.join('messaging', 'notification_detail.html')
    model = models.Notification

class ComposeMessageView(CreateView):
    template_name = os.path.join('messaging', 'message_compose.html')
    form_class = forms.MessageForm
    model = models.Message

    def get_success_url(self):
        return '/messaging/inbox/' + str(self.request.user.pk)

    def get_initial(self):
        return {
            'sender': self.request.user.pk
        }

class MessageThreadView(DetailView):
    template_name = os.path.join('messaging', 'message_thread.html')
    model = models.MessageThread