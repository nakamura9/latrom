from django.db import models
from django.db.models import Q
import datetime

class Dispatcher(object):
    def __init__(self, message):
        self.message = message

    def get_inbox(self, user):
        if not self.has_inbox(user):
            return Inbox.objects.create(user=user)
        return Inbox.objects.get(user=user)

    def has_inbox(self, user):
        return Inbox.objects.filter(user=user).exists()

    #check for replies
    def dispatch(self):
        #check if user has inbox
        r = self.message.recipient
        inbox = self.get_inbox(r)
        inbox.receive_message(self.message)

        for i in self.message.copy.all():
            inbox = self.get_inbox(i)
            inbox.receive_message(self.message)


class Message(models.Model):
    '''Communication between users of the system'''
    copy = models.ManyToManyField('auth.user', 
        related_name='copy', blank=True)
    recipient = models.ForeignKey('auth.user', on_delete=None,
        related_name='to')
    sender = models.ForeignKey('auth.user', on_delete=None,
        related_name='sender')
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    read = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now=True)
    opened_timestamp = models.DateTimeField(null=True, blank=True) 
    

    @property
    def is_reply(self):
        return MessageThread.objects.filter(
            Q(_from=self.recipient) &
            Q(_to=self.sender) &
            Q(closed=False)).exists()

    @property
    def has_open_thread(self):
        MessageThread.objects.filter(
            Q(_from=self.sender) &
            Q(_to=self.recipient) &
            Q(closed=False)).exists()            


    def open_message(self):
        self.read=True
        self.opened_timestamp = datetime.datetime.now()
        self.save()
class MessageThread(models.Model):
    # if sender and recipeint are the same, append message to thread unless its 
    # closed manually.
    closed = models.BooleanField(default=False)
    _from = models.ForeignKey('auth.user', on_delete=None, \
        related_name='_from', default=1)
    _to = models.ForeignKey('auth.user', related_name='_to',
        on_delete=None, default=1)
    participants = models.ManyToManyField('auth.user',
        related_name='participants',)
    messages = models.ManyToManyField('messaging.message')

    def add_message(self, message):
        self.messages.add(message)
        self.save()


class Notification(models.Model):
    user = models.ForeignKey('auth.user', default = 1, on_delete=None)
    title = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    #HMTL link depending on the notification
    action = models.CharField(max_length=255, blank=True)


class Inbox(models.Model):
    user = models.ForeignKey('auth.user', on_delete=None)
    threads = models.ManyToManyField('messaging.messagethread')

    def receive_message(self, message):
        if message.is_reply:
            thread = MessageThread.objects.get(
                _from =message.recipient, 
                _to= message.sender)

        elif message.has_open_thread:
            thread = MessageThread.objects.get(
                _from =message.sender, 
                _to= message.recipient)
        else:
            thread = MessageThread.objects.create(
                _from = message.sender,
                _to = message.recipient,
            )
            thread.participants.set(message.copy.all())

        thread.add_message(message)
            
    @property
    def notifications(self):
        return Notification.objects.filter(user=self.user)


    @property
    def total_in(self):
        return self.notifications.count() + self.threads.count()