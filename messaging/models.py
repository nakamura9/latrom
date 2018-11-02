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
        return self.is_reply or MessageThread.objects.filter(
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

    @property
    def unread(self):
        return self.messages.filter(read=False)

    @property
    def read(self):
        return self.messages.filter(read=True)

    def add_message(self, message):
        self.messages.add(message)
        self.save()

    @property
    def latest(self):
        return self.messages.latest('created_timestamp')

class Notification(models.Model):
    user = models.ForeignKey('auth.user', default = 1, on_delete=None)
    title = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    #HMTL link depending on the notification
    action = models.CharField(max_length=255, blank=True)

    def open_notification(self):
        self.read = True
        self.save()


class Inbox(models.Model):
    user = models.OneToOneField('auth.user', on_delete=None)
    threads = models.ManyToManyField('messaging.messagethread')

    def receive_message(self, message):
        if message.is_reply:
            thread = MessageThread.objects.get(
                _from =message.recipient, 
                _to= message.sender)

            initiator = thread._from.inbox
            if not thread in initiator.threads.all():
                initiator.threads.add(thread)


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
            self.threads.add(thread)

            self.save()

        thread.add_message(message)
            
    @property
    def notifications(self):
        return Notification.objects.filter(user=self.user)

    @property
    def unread_notifications(self):
        return self.notifications.filter(read=False).count()

    @property
    def unread_messages(self):
        total_unread_messages = 0
        for thread in self.threads.all():
            total_unread_messages += thread.unread.exclude(
                sender=self.user).count()

        return total_unread_messages

    @property
    def total_in(self):
        return self.unread_notifications + self.unread_messages


    def __str__(self):
        return str(self.user)