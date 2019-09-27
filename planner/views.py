# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import os
import urllib

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin

from . import filters, forms, models, serializers


class ReactCalendar(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner','calendar.html')

class PlannerDashboard(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner', 'dashboard.html')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        today = datetime.date.today()
        context['day'] = today.day
        context['day_detail'] = "{}, {}".format(today.strftime('%B'), today.year) 
        context['calendar_url'] = '/calendar/month/{}'.format(
            datetime.date.today().strftime('%Y/%m'))

        return context

class PlannerConfigUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('planner', 'config.html')
    form_class = forms.ConfigForm
    success_url = reverse_lazy('planner:dashboard')
    model = models.PlannerConfig

class EventParticipantMixin():
    def get_initial(self):
        initial = super().get_initial()
        
        if isinstance(self, UpdateView):
            participant_mapping = {
                0: 'employee',
                1: 'customer',
                2: 'supplier'
            }
            initial['json_participants'] = urllib.parse.quote(
                json.dumps([{
                    'type': participant_mapping[i.participant_type], 
                    'pk': i.participant_pk, 
                    'name': str(i)
                    } for i in self.object.participants.all()])
            )
            

        return initial 
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args,**kwargs)

        if not self.object:
            return resp
        
        try:
            participants = json.loads(urllib.parse.unquote(request.POST['json_participants']))
        except json.JSONDecodeError:
            messages.info(request, 'This event has no participants, please provide at least one')
            return resp

        if isinstance(self, UpdateView):
            for p in self.object.participants.all():
                p.delete()

        for p in participants:
            self.object.add_participant(p['type'], p['pk'])

        return resp

class EventCreateView(LoginRequiredMixin, EventParticipantMixin, CreateView):
    template_name = os.path.join('planner', 'events','create.html')
    form_class = forms.EventForm

    def get_initial(self):
        return {
            'owner': self.request.user 
        }

class EventUpdateView(LoginRequiredMixin, EventParticipantMixin, UpdateView):
    template_name = os.path.join('planner', 'events', 'update.html')
    form_class = forms.EventForm
    model = models.Event

    def get(self, *args, **kwargs):
        resp = super().get(*args, **kwargs)
        if self.request.user != self.object.owner:
            messages.info(self.request, f'{self.request.user} is not the owner of this event and does not have permission to change it.')
            return HttpResponseRedirect(reverse_lazy('planner:event-detail',
                kwargs={
                    'pk': self.object.pk
                }))

        return resp


class EventListView(ContextMixin, 
        LoginRequiredMixin, 
        PaginationMixin, 
        FilterView):
    template_name = os.path.join('planner', 'events', 'list.html')
    filterset_class = filters.EventFilter
    extra_context = {
        'title': 'Event List',
        'new_link': reverse_lazy('planner:event-create')
    }
    def get_queryset(self):
        return models.Event.objects.filter( 
            Q(owner=self.request.user)
        ).order_by('date').reverse()

class EventDetailView(LoginRequiredMixin, DetailView):
    model = models.Event 
    template_name = os.path.join('planner', 'events', 'detail.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_string'] = self.object.date.strftime('%Y/%m/%d')
        return context

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Event 
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = "/planner/dashboard"

class AgendaView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner', 'agenda.html')
    
    def get(self, *args, **kwargs):
        if not hasattr(self.request.user, "employee"):
            from django.contrib import messages
            messages.info(self.request, "The user logged in is not linked to any employee. Please login as another user to access the agenda.")
            return HttpResponseRedirect("/login")

        return super().get(*args, **kwargs)


class AgendaAPIView(ListAPIView):
    serializer_class = serializers.EventSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        filter = None
        agenda_items = \
            models.PlannerConfig.objects.first().number_of_agenda_items
        user = User.objects.get(pk=pk)
        if not hasattr(user, "employee"):
            return None

        if user.employee:
            filter = Q(Q(owner=user) | 
                Q(eventparticipant__employee__in=[user.employee.pk]))
        else:
            filter = Q(owner=user)
        
        return models.Event.objects.filter(
            Q(date__gte=datetime.date.today()) & 
            Q(completed=False) & filter).order_by('date')[:agenda_items]

class EventAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()

def complete_event(request, pk=None):
    evt = get_object_or_404(models.Event, pk=pk)
    evt.complete()
    return HttpResponseRedirect('/planner/dashboard')