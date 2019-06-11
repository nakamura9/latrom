from django.db import models
from django.db.models import Q
import datetime
import os 
from latrom.settings import MEDIA_ROOT
from django.shortcuts import reverse 
from django.contrib.auth.hashers import make_password
import common_data


class EmailAddress(models.Model):
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address

    @staticmethod
    def get_address(address):
        if EmailAddress.objects.filter(address=address).exists():
            return EmailAddress.objects.get(address=address)

        else:
            return EmailAddress.objects.create(address=address)

class UserProfile(common_data.utilities.mixins.ContactsMixin, models.Model):
    email_fields =['email_address']

    user = models.OneToOneField('auth.user', on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to=os.path.join(MEDIA_ROOT, 'chat'), blank=True, null=True)
    email_address = models.CharField(max_length=255)
    email_password = models.CharField(max_length=255)
    smtp_server = models.CharField(max_length=255, default='smtp.gmail.com')
    smtp_port = models.IntegerField(default=465)
    pop_imap_host = models.CharField(max_length=255, default='imap.gmail.com')
    pop_port = models.IntegerField(default=993)


    @property
    def emails(self):
        return Email.objects.filter(owner=self.user)

    @property
    def inbox(self):
        if self.emails:
            return self.emails.filter(folder='inbox')
    
    @property
    def sent(self):
        if self.emails:
            return self.emails.filter(folder='sent')

    @property
    def drafts(self):
        if self.emails:
            return self.emails.filter(folder='drafts')

    @property
    def latest_inbox(self):
        if self.inbox and self.inbox.exists():
            return self.inbox.latest('server_id').server_id

        return '-1'

    @property
    def latest_sent(self):
        if self.sent and self.sent.exists():
            return self.sent.latest('server_id').server_id

        return '-1'

    @property
    def latest_drafts(self):
        if self.drafts and self.drafts.exists():
            return self.drafts.latest('server_id').server_id

        return '-1'

    '''
    def save(self):
        #prevent encrypt the password
        pwd = make_password(self.email_password)
    '''

    def __str__(self):
        return self.email_address

    @property
    def address_obj(self):
        return EmailAddress.get_address(self.email_address)

class Email(models.Model):
    '''Communication between people online using email'''
    copy = models.ManyToManyField('messaging.EmailAddress', 
        related_name='copy_email', blank=True)
    blind_copy = models.ManyToManyField('messaging.EmailAddress', 
        related_name='blind_copy_email', blank=True)
    server_id = models.CharField( 
        blank=True, 
        default='',
        max_length=16)
    to = models.ForeignKey('messaging.EmailAddress', on_delete=models.SET_NULL, 
        null=True,
        related_name='to')
    sent_from = models.ForeignKey('messaging.EmailAddress',     
        on_delete=models.SET_NULL, 
        null=True,
        related_name='email_sent_from')
    owner = models.ForeignKey('auth.user', on_delete=models.SET_NULL, 
        null=True,
        related_name='email_author')
    read = models.BooleanField(default=False)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True, default="")
    text = models.TextField(blank=True, default="")
    folder=models.CharField(max_length=16, default='inbox', choices=[
        ('inbox', 'Inbox'),
        ('sent', 'Sent'),
        ('drafts', 'Drafts'),
    ])
    sent = models.BooleanField(default=False)
    attachment=models.FileField(null=True, blank=True, upload_to=os.path.join(
        MEDIA_ROOT, 'messaging'
    ))
    created_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.sent_from and self.to:
            return f"From {self.sent_from.address} to {self.to.address}"
        elif self.sent_from:
            return f"From {self.sent_from.address}"
        elif self.to:
            return f"From {self.to.address}"

        else: return 'Unknown details'


class Notification(models.Model):
    user = models.ForeignKey('auth.user', default = 1, 
        on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    #HMTL link depending on the notification
    action = models.CharField(max_length=255, blank=True)

    def open(self):
        self.read = True
        self.save()


class Bubble(models.Model):
    sender = models.ForeignKey('auth.user', 
        on_delete=models.SET_NULL, null=True)
    created_timestamp = models.DateTimeField(null=True, blank=True)
    opened_timestamp = models.DateTimeField(blank=True, null=True)
    message_text = models.TextField()
    attachment = models.FileField(upload_to=os.path.join(MEDIA_ROOT, 
        'messaging'), blank=True, null=True)
    chat = models.ForeignKey('messaging.Chat', 
        on_delete=models.CASCADE, null=True)
    group = models.ForeignKey('messaging.Group', 
        on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.created_timestamp:
            self.created_timestamp = datetime.datetime.now()
            self.save()


class Chat(models.Model):
    sender = models.ForeignKey("auth.user", 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='chat_sender')
    receiver = models.ForeignKey("auth.user", 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='chat_receiver')
    archived = models.BooleanField(default=False)

    @staticmethod
    def user_chats(user):
        return Chat.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )
    
    @property
    def messages(self):
        return Bubble.objects.filter(Q(
            chat=self
        )).order_by('pk')

class Group(models.Model):
    admin = models.ForeignKey('auth.user', 
        null=True, 
        on_delete=models.SET_NULL,
        related_name='admin')
    participants = models.ManyToManyField('auth.user',
        related_name='group_participants')
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(blank=True, default="", max_length=255)
    icon = models.ImageField(upload_to=os.path.join(MEDIA_ROOT, 'chat'), 
        null=True)
    active = models.BooleanField(default=True)

    @property
    def messages(self):
        return Bubble.objects.filter(Q(
            group=self
        )).order_by('pk')
        
    def get_absolute_url(self):
        return reverse("messaging:group", kwargs={"pk": self.pk})
    