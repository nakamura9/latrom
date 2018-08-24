import os 

from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework.generics import ListAPIView
from django.urls import reverse_lazy
from django.db.models import Q

from inventory import forms
from inventory import serializers
from inventory import models
from .common import InventoryControllerCheckMixin

#!fix prevent updates from assigining parent media to child media.

class StorageMediaCreateView(CreateView):
    template_name = os.path.join('inventory', 'storage_media', 'create.html')
    form_class = forms.StorageMediaForm
    success_url = reverse_lazy('inventory:warehouse-list')

    def get_initial(self):
        return {
            'warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        return super(StorageMediaCreateView, self).post(request, *args, **kwargs)

class StorageMediaDetailView(DetailView):
    template_name = os.path.join('inventory', 'storage_media', 'detail.html')
    model = models.StorageMedia

class StorageMediaUpdateView(InventoryControllerCheckMixin, UpdateView):
    form_class = forms.StorageMediaForm
    model = models.StorageMedia
    template_name = os.path.join('inventory', 'storage_media','update.html')

    def get_success_url(self):
        return reverse_lazy('inventory:storage-media-list', kwargs={
            'pk': self.object.warehouse.pk
        })
class StorageMediaListView(InventoryControllerCheckMixin, TemplateView):
    template_name = os.path.join('inventory', 'storage_media', 'list.html')


    def get_context_data(self, *args, **kwargs):
        context = super(StorageMediaListView, self).get_context_data(*args, **kwargs)
        return context

class StorageMediaListAPIView(ListAPIView):
    serializer_class = serializers.StorageMediaSerializer
    #queryset = models.StorageMedia.objects.all()
    def get_queryset(self):
        if self.kwargs.get('pk', None):
            w = models.WareHouse.objects.get(pk=self.kwargs['pk'])
            return models.StorageMedia.objects.filter(
                Q(warehouse=w) &
                Q(location=None)
            )
        return models.StorageMedia.objects.filter(location=None) 
    