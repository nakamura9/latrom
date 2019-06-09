from django.views.generic import TemplateView, DetailView, ListView

from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.generics import RetrieveAPIView
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

class MessagingPaginator(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 50


class BubbleAPIViewset(ModelViewSet):
    queryset = models.Bubble.objects.all()
    pagination_class = MessagingPaginator

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return serializers.BubbleReadSerializer

        return serializers.BubbleSerializer


class GroupAPIViewset(ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ChatAPIViewset(ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer



class EmailAPIViewset(ModelViewSet):
    queryset = models.Email.objects.all().order_by('-date')
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

class InboxAPIView(APIView):
    def get(self, request):
        #maybe try to sync latest emails here?
        emails = models.UserProfile.objects.get(user=self.request.user).inbox

        data = serializers.EmailRetrieveSerializer(emails, many=True).data
        return Response(data)

class DraftsAPIView(APIView):
    def get(self, request):
        emails = models.UserProfile.objects.get(user=self.request.user).drafts
        data = serializers.EmailRetrieveSerializer(emails, many=True).data
        return Response(data)


class SentAPIView(APIView):
    def get(self, request):
        emails = models.UserProfile.objects.get(user=self.request.user).sent
        data = serializers.EmailRetrieveSerializer(emails, many=True).data
        return Response(data)

def send_draft(request, pk=None):
    email = get_object_or_404(models.Email, pk=pk)
    
    profile = models.UserProfile.objects.get(user=email.sender)
    g = EmailSMTP(profile)
    g.send_html_email(email.subject, email.to.address, email.body)

    return JsonResponse({'status': 'ok'})

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


        models.Email.objects.create(
        to=email.sent_from,
        sent_from = email.to,
        subject =email.subject,
        owner=request.user,
        attachment=form.cleaned_data['attachment'],
        sent=True,
        folder='sent',
        body=body
    )
        return JsonResponse({'status': 'ok'})
        

    else:
        print(form.errors)
        return JsonResponse({'status': 'fail'})


def notification_service(request):
        try:        
            unread = models.Notification.objects.filter(            read=False, user=request.user)    
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
        latest.read = True    
        latest.save()    
        return JsonResponse(data)
        
def mark_notification_read(request, pk=None):
    notification = get_object_or_404(models.Notification, pk=pk)  
    notification.read = True
    notification.save()
    return JsonResponse({'status': 'ok'})