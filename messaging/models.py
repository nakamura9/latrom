from django.db import models
from django.db.models import Q

class Message(models.Model):
    '''Communication between users of the system'''
    carbon_copy = models.ManyToManyField('auth.user', 
        related_name='CC', blank=True)
    blind_carbon_copy = models.ManyToManyField('auth.user', 
        related_name='BCC', blank=True)
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
    thread = models.ForeignKey('messaging.MessageThread', 
        null=True, on_delete=None, blank=True)
    #support files?

    def assign_thread(self):
        if self.thread:
            return
        else:
            thread = MessageThread.objects.get(
                Q(participants=self.sender) &
                Q(self.recipient) & 
                Q(closed=False))
            if thread:
                self.thread = thread
            else:
                self.thread = MessageThread.objects.create()
    
            self.thread.participants.add(self.sender)
            self.thread.participants.add(self.recipient)
            self.thread.save()

    def save(self, *arg, **kwargs):
        super().save(*arg, **kwargs)
        self.assign_thread()

class MessageThread(models.Model):
    # if sender and recipeint are the same, append message to thread unless its 
    # closed manually.
    closed = models.BooleanField(default=False)
    participants = models.ManyToManyField('auth.user')

    @property
    def latest(self):
        return self.message_set.latest('created_timestamp')

class Notification(models.Model):
    user = models.ForeignKey('auth.user', default = 1, on_delete=None)
    title = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    #HMTL link depending on the notification
    action = models.CharField(max_length=255, blank=True)


class Inbox(models.Model):
    user = models.ForeignKey('auth.user', on_delete=None)


    @property
    def notifications(self):
        return Notification.objects.filter(user=self.user)

    @property
    def threads(self):
        return self.user.messagethread_set.all()

    @property
    def total_in(self):
        return self.notifications.count() + self.threads.count()