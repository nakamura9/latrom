import os

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy



class ScrappingRecordCreateView(CreateView):
    template_name = os.path.join('inventory', 'scrapping', 'create.html')
    form_class = 
    success_url = 

class ScrappingReportListCreateView(ListView):
    pass

class ScrappingReportDetailView(DetailView):
    pass