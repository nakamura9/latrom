from messaging.email_api.email import EmailSMTP
from messaging.models import UserProfile
from django.contrib.auth.models import User
import logging
from background_task import background
from background_task.models import Task

@background
def sync_service():
    for user in User.objects.all():
        if not UserProfile.objects.filter(user=user).exists():
            continue
            try:
                profile = UserProfile.objects.get(user=user)
                client = EmailSMTP(profile)
                client.fetch_inbox()
                client.fetch_drafts()
                client.fetch_sent()
            except: 
                logger.error('The email service failed to connect to the remote server')

try:
    sync_service(repeat=3600)
except:
    # TODO handle exceptions better
    pass