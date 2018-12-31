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
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from rest_framework import viewsets

from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin

from . import filters, forms, models, serializers


class ReactCalendar(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner','calendar.html')

class PlannerDashboard(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner', 'dashboard.html')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['calendar_url'] = '/calendar/month/{}'.format(
            datetime.date.today().strftime('%Y/%m'))

        return context
class PlannerConfigUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('planner', 'config.html')
    form_class = forms.ConfigForm
    success_url = reverse_lazy('planner:dashboard')
    model = models.PlannerConfig

class EventParticipantMixin(object):
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args,**kwargs)

        if not self.object:
            return resp
        
        try:
            participants = json.loads(urllib.parse.unquote(request.POST['participants']))
        except json.JSONDecodeError:
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
    success_url = reverse_lazy('planner:event-list')

    def get_initial(self):
        return {
            'owner': self.request.user 
        }


class EventUpdateView(LoginRequiredMixin, EventParticipantMixin, UpdateView):
    template_name = os.path.join('planner', 'events', 'update.html')
    form_class = forms.EventForm
    success_url = reverse_lazy('planner:event-list')
    model = models.Event


class EventListView(ContextMixin, LoginRequiredMixin, PaginationMixin, FilterView):
    template_name = os.path.join('planner', 'events', 'list.html')
    filterset_class = filters.EventFilter
    extra_context = {
        'title': 'Event List',
        'new_link': reverse_lazy('planner:event-create')
    }
    def get_queryset(self):
        return models.Event.objects.filter( 
            Q(owner=self.request.user)
        )

class EventDetailView(LoginRequiredMixin, DetailView):
    model = models.Event 
    template_name = os.path.join('planner', 'events', 'detail.html')

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Event 
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = "/planner/dashboard"

class AgendaView(LoginRequiredMixin, ListView):
    template_name = os.path.join('planner', 'agenda.html')
    
    def get_queryset(self):
        return models.Event.objects.filter(
            Q(date__gte=datetime.date.today()) & 
            Q(owner=self.request.user) &
            Q(completed=False))

class EventAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()

def complete_event(request, pk=None):
    evt = get_object_or_404(models.Event, pk=pk)
    evt.completed=True
    evt.completion_time = datetime.datetime.now()
    evt.save()
    return HttpResponseRedirect('/planner/dashboard')