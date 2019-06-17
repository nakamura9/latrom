from .email import EmailSMTP
from messaging.models import UserProfile
import logging

def sync_service(user):
    try:
        profile = UserProfile.objects.get(user=user)
        client = EmailSMTP(profile)
        client.fetch_inbox()
        client.fetch_drafts()
        client.fetch_sent()
    except: 
        logger.error('The email service failed to connect to the remote server')
        