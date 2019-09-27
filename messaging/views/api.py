from django.views.generic import TemplateView, DetailView, ListView

from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
import datetime
from messaging import models, forms, serializers
from django.db.models import Q
from django.contrib.auth.models import User
from latrom.settings import MEDIA_ROOT
from common_data.utilities.mixins import ContextMixin
import os
import json
import urllib
from messaging.email_api.email import EmailSMTP
from draftjs_exporter.html import HTML as exporterHTML
from rest_framework.pagination import PageNumberPagination
from common_data.serializers import UserSerializer


class MessagingPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10

class BubbleAPIViewset(ModelViewSet):
    queryset = models.Bubble.objects.all()
    pagination_class = MessagingPaginator

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return serializers.BubbleReadSerializer

        return serializers.BubbleSerializer


class UserProfileAPIViewset(ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer


class GroupAPIViewset(ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer

class ChatAPIViewset(ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer

class EmailAddressAPIViewset(ModelViewSet):
    queryset = models.EmailAddress.objects.all()
    serializer_class = serializers.EmailAddressSerializer


class EmailAPIViewset(ModelViewSet):
    queryset = models.Email.objects.all().order_by('-created_timestamp')
    pagination_class = MessagingPaginator
    
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return serializers.EmailRetrieveSerializer

        return serializers.EmailSerializer



def close_chat(request, pk=None):
    chat = get_object_or_404(models.Chat, pk=pk)
    chat.archived=True
    chat.save()

    return HttpResponseRedirect(reverse('messaging:chat-list'))


def close_group(request, pk=None):
    group = get_object_or_404(models.Group, pk=pk)
    group.active=False
    group.save()

    return HttpResponseRedirect(reverse('messaging:group-list'))

class EmailFolderAPIViewset(ModelViewSet):
    queryset = models.EmailFolder.objects.all()
    serializer_class = serializers.EmailFolderSerializer

class FolderAPIView(APIView):
    def get(self, request,folder=None):
        #maybe try to sync latest emails here?
        folder = models.EmailFolder.objects.get(pk=folder)
        emails = folder.emails
        paginator = MessagingPaginator()
        qs = paginator.paginate_queryset(emails, request)
        data = serializers.EmailRetrieveSerializer(qs, many=True, context={
            'request': request
        }).data
        
        return Response(data)


def reply_email(request, pk=None):
    email = get_object_or_404(models.Email, pk=pk)
    
    profile = models.UserProfile.objects.get(user=email.owner)
    g = EmailSMTP(profile)

    #set up 
    config = {}
    exporter = exporterHTML(config)
    form = forms.AxiosEmailForm(request.POST, request.FILES)

    if form.is_valid():
        body = exporter.render(
                json.loads(form.cleaned_data['body'])
            )
        if form.cleaned_data['attachment']:
            g.send_email_with_attachment(email.subject, 
                                            email.to.address, 
                                            body, 
                                            form.cleaned_data['attachment'],
                                            html=True)
        else:
            g.send_html_email(email.subject, email.to.address, body)


        msg =models.Email.objects.create(
        to=email.sent_from,
        sent_from = email.to,
        subject =email.subject,
        owner=request.user,
        attachment=form.cleaned_data['attachment'],
        sent=True,
        folder='sent',
    )
        msg.write_body(body)
        
        return JsonResponse({'status': 'ok'})

    else:
        return JsonResponse({'status': 'fail'})


def notification_service(request):
        try:        
            unread = models.Notification.objects.filter(read=False, 
                user=request.user)    
        except:        
            return JsonResponse({'latest': {}, 'unread': 0})    
            
        if unread.count() == 0:        
            return JsonResponse({'latest': {}, 'unread': 0})    
        
        latest = unread.latest('timestamp')    
        data = {        
            'latest': {            
                'title': latest.title,
                'message': latest.message,
                'action': latest.action,
                'id': latest.pk,            
                'stamp': latest.timestamp.strftime("%d, %B, %Y")        },      'unread': unread.count()
                    }    
        
        return JsonResponse(data)
        
def mark_notification_read(request, pk=None):
    notification = get_object_or_404(models.Notification, pk=pk)  
    notification.read = True
    notification.save()
    return JsonResponse({'status': 'ok'})

def send_draft(request, pk=None):
    email = get_object_or_404(models.Email, pk=pk)
    profile = models.UserProfile.objects.get(user=request.user)
    
    g = EmailSMTP(profile)
    g.send_html_email(
                email.subject,
                email.to.address,
                [i.address for i in email.copy.all()],
                [i.address for i in email.blind_copy.all()],
                email.body
                )
    email.folder = 'sent'
    email.save()

    return JsonResponse({'status': 'ok'})

def get_latest_chat_messages(request, chat=None):
    discussion = get_object_or_404(models.Chat, pk=chat)
    latest = json.loads(request.body.decode('utf-8'))['latest']
    if latest:
        messages = discussion.messages.filter(pk__gt=latest)
    elif discussion.messages.count() > 0:
        messages = discussion.messages
    else:
        messages= []

    data = serializers.BubbleReadSerializer(messages, many=True).data
    
    return JsonResponse({'messages': data})

def get_latest_group_messages(request, group=None):
    discussion = get_object_or_404(models.Group, pk=group)
    latest = json.loads(request.body.decode('utf-8'))['latest']
    if latest:
        messages = discussion.messages.filter(pk__gt=latest)
    elif discussion.messages.count() > 0:
        messages = discussion.messages
    else:
        messages= []

    data =  serializers.BubbleReadSerializer(messages, many=True).data
    return JsonResponse({'messages': data})

def delete_messages(request):
    ids = json.loads(request.body.decode('utf-8'))['message_ids']
    for id in ids:
        models.Bubble.objects.get(pk=id).delete()

    return JsonResponse({'status': 'ok'})

def forward_messages(request, user=None):
    #TODO support forwarding while crediting the originator
    user = get_object_or_404(User, pk=user)
    filters = Q(
        Q(
            Q(sender=request.user) &
            Q(receiver=user)
        )
        |
        Q(
            Q(receiver=request.user) &
            Q(sender=user)
        )
    )
    if models.Chat.objects.filter(filters).exists():
        chat = models.Chat.objects.filter(filters).first()

    else:
        chat = models.Chat.objects.create(
            sender=request.user,
            receiver=user
            )
    
    ids = json.loads(request.body.decode('utf-8'))['message_ids']
    for id in ids:
        bubble = models.Bubble.objects.get(pk=id)
        models.Bubble.objects.create(
            sender=request.user,
            message_text=bubble.message_text,
            attachment=bubble.attachment,
            chat=chat
        )

    return JsonResponse({
        'redirect': reverse("messaging:chat", kwargs={'pk': chat.id})})
    # return HttpResponseRedirect(
    #     reverse("messaging:chat", kwargs={'pk': chat.id}))


def forward_email_messages(request, pk=None):
    email = get_object_or_404(models.Email, pk=pk)
    data = json.loads(request.body.decode('utf-8'))

    to = models.EmailAddress.objects.get(pk=data['to'].split('-')[0])
    copy = [models.EmailAddress.objects.get(pk=addr.split('-')[0]) \
                for addr in data['copy']]
    blind_copy = [models.EmailAddress.objects.get(pk=addr.split('-')[0]) \
                for addr in data['blind_copy']]

    profile = models.UserProfile.objects.get(user=request.user)
    msg = models.Email.objects.create(
        to=to,
        sent_from=profile.address_obj,
        owner=profile.user,
        subject=email.subject,
        body=email.body,
        text=email.text,
        folder='sent',
        attachment=email.attachment
    )

    msg.copy.add(*copy)
    msg.blind_copy.add(*blind_copy)
    msg.save()

    g = EmailSMTP(profile)

    if(data.get('attachment', None)):# and os.path.exists(path):
        path = os.path.join(
            MEDIA_ROOT, 
            'messaging', 
            email.attachment.filename)
        
        g.send_email_with_attachment(
            email.subject, 
            to.address,
            [i.address for i in copy],
            [i.address for i in blind_copy],
            email.body, 
            email.attachment, html=True)
    else:
        g.send_html_email(
            email.subject, 
            to.address, 
            [i.address for i in copy],
            [i.address for i in blind_copy],
            email.body)
    
    return JsonResponse({'status': 'ok'})

def add_participant(request, grp=None, id=None):
    group = models.Group.objects.get(pk=grp)
    usr = User.objects.get(pk=id)
    group.participants.add(usr)
    group.save()

    return JsonResponse(UserSerializer(group.participants, many=True).data,
        safe=False)

def remove_participant(request, grp=None, id=None):
    group = models.Group.objects.get(pk=grp)
    usr = User.objects.get(pk=id)
    group.participants.remove(usr)
    group.save()

    return JsonResponse(UserSerializer(group.participants, many=True).data,
        safe=False)

def sync_folders(request, profile_id=None):
    profile = models.UserProfile.objects.get(pk=profile_id)
    client = EmailSMTP(profile)
    messages = client.fetch_all_folders()

    return JsonResponse({
        'status': 'ok',
        'emails': 0
    })

def get_user_icon(request):
    profile = models.UserProfile.objects.get(user=request.user)
    if profile.avatar:
        return HttpResponse(profile.avatar.url)
    return HttpResponse('')