from django.db import models
from django.db.models import Q
import datetime
import os 
from latrom.settings import MEDIA_ROOT
from django.shortcuts import reverse 
from django.contrib.auth.hashers import make_password
import common_data
from messaging.email_api.secrets import get_secret_key
from cryptography.fernet import Fernet
from django.core.files import File
import imaplib
import string

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

class EmailFolder(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey('messaging.UserProfile', null=True, 
        on_delete=models.SET_NULL)
    label = models.CharField(max_length=255)

    @property
    def latest(self):
        qs = Email.objects.filter(folder=self)
        if qs.exists():
            return qs.order_by('server_id').reverse()[0]
    
    def __str__(self):
        return self.name

    @property
    def emails(self):
        return Email.objects.filter(folder=self)

class UserProfile(common_data.utilities.mixins.ContactsMixin, models.Model):
    email_fields =['email_address']

    user = models.OneToOneField('auth.user', on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='chat/', blank=True, null=True)
    email_address = models.CharField(max_length=255)
    email_password = models.CharField(max_length=255)
    outgoing_server = models.CharField(max_length=255, default='smtp.gmail.com')
    outgoing_port = models.IntegerField(default=465)
    incoming_host = models.CharField(max_length=255, default='imap.gmail.com')
    incoming_port = models.IntegerField(default=993)
    
    @property
    def get_plaintext_password(self):
        if self.email_password == "":
            return self.email_password
        encrypted = self.email_password.encode()
        crypt = Fernet(get_secret_key())
        decrypted = crypt.decrypt(encrypted)

        return decrypted.decode()

    def create_outbox(self):
        EmailFolder.objects.create(
            name='Local Outbox',
            owner=self,
            label='Local Outbox'
        )

    def create_local_drafts_folder(self):
        EmailFolder.objects.create(
            name='Local Drafts',
            owner=self,
            label='Local Drafts'
        )

    @property
    def emails(self):
        return Email.objects.filter(owner=self.user).order_by('-server_id')

    def login_incoming(self):
        mailbox = imaplib.IMAP4_SSL(self.incoming_host, self.incoming_port)
        mailbox.login(self.email_address, self.get_plaintext_password)
        return mailbox

    @property
    def folders(self):
        qs = EmailFolder.objects.filter(owner=self)
        if qs.exists():
            return qs

        self.get_folders()
        return EmailFolder.objects.filter(owner=self)

    def get_folder(self, name):
        qs = EmailFolder.objects.filter(owner=self, label__icontains=name)
        if qs.exists():
            return qs.first()
        return None


    @property
    def sent_folder(self):
        self.get_folder('sent')

    @property
    def draft_folder(self):
        self.get_folder('draft')

    @property
    def inbox_folder(self):
        self.get_folder('inbox')

    def get_folders(self):
        mailbox = self.login_incoming()
        for i in mailbox.list()[1]:
            folder_string = i.decode() if isinstance(i, bytes) else i
            folder_name = folder_string.split(' "/" ')[-1]
            folder_label = folder_name.string(string.punctuation)
            if not EmailFolder.objects.filter(
                    owner=self, name=folder_name).exists():
                EmailFolder.objects.create(owner=self, 
                                            #in case
                                           name=folder_name.split('/')[-1],
                                           label=folder_label)

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
    server_id = models.IntegerField( 
        blank=True, null=True)
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
    body = models.FileField(upload_to='messaging/', 
        blank=True, null=True)
    text = models.TextField(blank=True, default="")
    folder=models.ForeignKey('messaging.EmailFolder', null=True, 
        on_delete=models.SET_NULL)
    sent = models.BooleanField(default=False)
    attachment=models.FileField(null=True, blank=True, upload_to='messaging/'
    )
    created_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.sent_from and self.to:
            return f"From {self.sent_from.address} to {self.to.address}"
        elif self.sent_from:
            return f"From {self.sent_from.address}"
        elif self.to:
            return f"From {self.to.address}"

        else: return 'Unknown details'

    def write_body(self, body_string):
        filename = f'{self.owner.id}-{self.server_id}-' + \
            f'{datetime.datetime.now().strftime("%d%m%y%H%M%S")}.txt'
        try:
            with open(filename, 'w') as f:
                f.write(body_string)

            with open(filename, 'r') as sf:
                self.body.save(filename, File(sf)) 
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def read_body(self):
        if self.body:
            try:
                return self.body.read().decode(errors="ignore")
            except:
                return self.body


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
    attachment = models.FileField(upload_to=
        'messaging/', blank=True, null=True)
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
    icon = models.ImageField(upload_to='chat/', 
        null=True)
    active = models.BooleanField(default=True)

    @property
    def messages(self):
        return Bubble.objects.filter(Q(
            group=self
        )).order_by('pk')
        
    def get_absolute_url(self):
        return reverse("messaging:group", kwargs={"pk": self.pk})
    