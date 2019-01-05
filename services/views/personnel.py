import json
import os
import urllib

from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from rest_framework.viewsets import ModelViewSet

from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin
from services import filters, forms, models, serializers
from services.views.util import ServiceCheckMixin


####################################################
#                Service Employees                 #
####################################################
class ServicePersonCreateView(ServiceCheckMixin, ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.ServicePersonForm
    success_url = reverse_lazy('services:service-person-list')
    extra_context = {
        'title': 'Add Employee to Service Personnel'
    }

class ServicePersonUpdateView(ServiceCheckMixin, ContextMixin, UpdateView):
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.ServicePersonUpdateForm
    success_url = reverse_lazy('services:service-person-list')
    model = models.ServicePerson
    extra_context = {
        'title': 'Update Service Person Details'
    }

class ServicePersonListView(ServiceCheckMixin, ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('services', 'personnel', 'list.html')
    queryset = models.ServicePerson.objects.all()
    paginate_by = 10
    extra_context = {
        'title': 'Service Personnel List',
        'new_link': reverse_lazy('services:service-person-create')
    }
    filterset_class = filters.ServicePersonFilter

class ServicePersonDashboardView(ServiceCheckMixin, DetailView):
    template_name = os.path.join('services', 'personnel', 'dashboard.html')
    model = models.ServicePerson

####################################################
#                    Service Teams                 #
####################################################
class ServiceTeamCRUDMixin(object):
    def post(self, request, *args, **kwargs):
        update_flag = isinstance(self, UpdateView)
        resp = super(ServiceTeamCRUDMixin, self).post(request, *args, **kwargs)
        if not self.object:
            return resp 
        
        if update_flag:
            self.object.members.clear()
        
        members_list = json.loads(urllib.parse.unquote(request.POST['members']))
        for data in members_list:
            pk = data['value'].split('-')[0]
            service_person = models.ServicePerson.objects.get(pk=pk)
            self.object.members.add(service_person)

        return resp

class ServiceTeamCreateView(ServiceCheckMixin, ServiceTeamCRUDMixin, CreateView):
    template_name = os.path.join('services', 'personnel', 'teams', 
        'create.html')
    form_class = forms.ServiceTeamForm
    success_url = reverse_lazy('services:team-list')

    

class ServiceTeamUpdateView(ServiceCheckMixin, ServiceTeamCRUDMixin, UpdateView):
    template_name = os.path.join('services', 'personnel', 'teams', 
        'update.html')
    form_class = forms.ServiceTeamForm
    success_url = reverse_lazy('services:team-list')
    model = models.ServiceTeam

class ServiceTeamDetailView(ServiceCheckMixin, DetailView):
    template_name = os.path.join('services', 'personnel', 'teams', 
        'detail.html')
    model = models.ServiceTeam

class ServiceTeamListView(ServiceCheckMixin, ContextMixin, ListView):
    template_name = os.path.join('services', 'personnel', 'teams', 
        'list.html')
    queryset = models.ServiceTeam.objects.all()
    extra_context = {
        'title': 'List of Service Teams',
        'new_link': reverse_lazy('services:team-create')
    }

class ServiceTeamAPIView(ModelViewSet):
    serializer_class = serializers.ServiceTeamSerializer
    queryset = models.ServiceTeam.objects.all()

class ServicePersonAPIView(ModelViewSet):
    serializer_class = serializers.ServicePersonSerializer
    queryset = models.ServicePerson.objects.all()
