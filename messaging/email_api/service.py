from .email import EmailSMTP
from messaging.models import UserProfile

def sync_service(user):
    profile = UserProfile.objects.get(user=user)
    client = EmailSMTP(profile)
    client.fetch_inbox()
    client.fetch_drafts()
    client.fetch_sent()