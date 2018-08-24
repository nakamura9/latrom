# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os 
import json
import urllib
from django_filters.views import FilterView
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from rest_framework import viewsets 
from common_data.utilities import ExtraContext
from django.urls import reverse_lazy
from . import models
from . import serializers
from . import forms
from . import filters
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin


class ReactCalendar(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner','calendar.html')

class PlannerDashboard(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('planner', 'dashboard.html')

class PlannerConfigUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('planner', 'config.html')
    form_class = forms.ConfigForm
    success_url = reverse_lazy('planner:dashboard')
    model = models.PlannerConfig

class EventCreateView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('planner', 'events','create.html')
    form_class = forms.EventForm
    success_url = reverse_lazy('planner:event-list')

    def get_initial(self):
        return {
            'owner': self.request.user 
        }

    def post(self, request, *args,  **kwargs):
        resp = super(EventCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        
        participants = json.loads(urllib.unquote(request.POST['participants']))
        
        for p in participants:
            self.object.add_participant(p['type'], p['pk'])

        return resp

class EventUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('planner', 'events', 'update.html')
    form_class = forms.EventForm
    success_url = reverse_lazy('planner:event-list')
    model = models.Event

    def post(self, request, *args,  **kwargs):
        resp = super(EventUpdateView, self).post(request, *args, **kwargs)
        
        #remove exisiting participants
        for p in self.object.participants.all():
            p.delete()

        participants = json.loads(urllib.unquote(request.POST['participants']))
        
        for p in participants:
            self.object.add_participant(p['type'], p['pk'])

        return resp

class EventListView(ExtraContext, LoginRequiredMixin, FilterView):
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

class AgendaView(LoginRequiredMixin, ListView):
    template_name = os.path.join('planner', 'agenda.html')
    
    def get_queryset(self):
        return models.Event.objects.filter(
            Q(date__gte=datetime.date.today()) & 
            Q(owner=self.request.user))

class EventAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()