import os

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from inventory import forms, models, serializers

from common_data.utilities import ContextMixin

# TODO prevent updates from assigining parent media to child media.

class StorageMediaCreateView( CreateView):
    template_name = os.path.join('inventory', 'storage_media', 'create.html')
    form_class = forms.StorageMediaForm

    def get_initial(self):
        return {
            'warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        return super(StorageMediaCreateView, self).post(request, *args, **kwargs)

class StorageMediaDetailView( DetailView):
    template_name = os.path.join('inventory', 'storage_media', 'detail.html')
    model = models.StorageMedia

class StorageMediaUpdateView( UpdateView):
    form_class = forms.StorageMediaForm
    model = models.StorageMedia
    template_name = os.path.join('inventory', 'storage_media','update.html')

class StorageMediaListView( TemplateView):
    template_name = os.path.join('inventory', 'storage_media', 'list.html')


    def get_context_data(self, *args, **kwargs):
        context = super(StorageMediaListView, self).get_context_data(*args, **kwargs)
        context['warehouse'] = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return context

class StorageMediaRetrieveAPIView(RetrieveAPIView):
    queryset = models.StorageMedia.objects.all()
    serializer_class = serializers.StorageMediaSerializer

class StorageMediaListAPIView(ListAPIView):
    serializer_class = serializers.StorageMediaSerializer
    #queryset = models.StorageMedia.objects.all()
    def get_queryset(self):
        if self.kwargs.get('pk', None):
            w = models.WareHouse.objects.get(pk=self.kwargs['pk'])
            return models.StorageMedia.objects.filter(
                Q(warehouse=w)
            )
        return models.StorageMedia.objects.filter(location=None)

class StorageMediaNestedListAPIView(ListAPIView):
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

class AutogenerateStorageMediaView( ContextMixin, FormView):
    form_class = forms.AutoStorageMedia
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('inventory:home')
    extra_context = {
        'title': 'Generate Storage Media System'
    }

    def get_initial(self):
        return {
            'warehouse': self.kwargs['warehouse']
        }

    def form_valid(self, form):
        resp= super().form_valid(form)
        wh = form.cleaned_data['warehouse']

        for i in range(int(form.cleaned_data['number_of_corridors'])):
            corridor = models.StorageMedia.objects.create(
                name='CORRIDOR_{}'.format(i),
                warehouse=wh,
                description="corridor"
            )
            for j in range(int(form.cleaned_data['number_of_aisles_per_corridor'])):
                aisle = models.StorageMedia.objects.create(
                     name='CORRIDOR_{}_AISLE_{}'.format(i, j),
                    warehouse=wh,
                    description="aisle",
                    location=corridor
                )
                for k in range(int(form.cleaned_data['number_of_shelves_per_aisle'])):
                    shelf = models.StorageMedia.objects.create(
                         name='CORRIDOR_{}_AISLE_{}_SHELF_{}'.format(i, j, k),
                        warehouse=wh,
                        description="shelf",
                        location=aisle
                    )

        return resp