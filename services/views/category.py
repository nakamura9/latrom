from services.models import ServiceCategory
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView, ListView
from common_data.utilities import ContextMixin
import os
from django.urls import reverse_lazy
from services import forms

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class ServiceCategoryCreateView( ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ServiceCategoryForm
    success_url = reverse_lazy('services:category-list')
    extra_context = {
        'title': 'Create New Service Category'
    }

class ServiceCategoryUpdateView( ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ServiceCategoryForm
    model = ServiceCategory
    success_url = reverse_lazy('services:category-list')
    extra_context = {
        'title': 'Update Service Category'
    }

class ServiceCategoryDetailView( DetailView):
    template_name = os.path.join('services', 'category', 'detail.html')
    model = ServiceCategory

class ServiceCategoryListView( ContextMixin, ListView):
    template_name = os.path.join('services', 'category', 'list.html')
    model = ServiceCategory
    extra_context = {
        'title': "List of Service Categories",
        'new_link': reverse_lazy('services:create-category')
    }