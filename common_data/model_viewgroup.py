from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.conf.urls import url
import os


class ModelViewGroup(object):
    model = None
    create_form = None
    update_form = None
    create_update_form = None
    urls = []
    create_template = None
    create_update_template = None
    update_template = None
    delete_template = None
    list_template = None
    success_url = None

    def __init__(self):
        self.create_create_view()
        self.create_update_view()
        self.create_delete_view()
        self.create_list_view()
        self.create_urls()

    def create_create_view(self):
        self.create_klass = type(self.model.__name__ +'ModelCreateView', (CreateView, ), {
            'template_name': self.create_template,
            'success_url': self.success_url,
            'model': self.model,
            'fields': '__all__'
            })

    def create_list_view(self):
        self.list_klass = type(self.model.__name__ +'ModelListView', (ListView, ), {
            'template_name': self.list_template,
            'model': self.model,
            'get_queryset': lambda self: self.model.objects.all().order_by('pk'),
            })
        
    def create_update_view(self):
        self.update_klass = type(self.model.__name__  + 'ModelUpdateView', (UpdateView, ), {
            'template_name': self.create_template, # update_template
            'success_url': self.success_url,
            'model': self.model,
            'fields': "__all__"
            })

    def create_delete_view(self):
        self.delete_klass = type(self.model.__name__  + 'ModelDeleteView', (DeleteView, ), {
            'template_name': self.delete_template, # update_template
            'success_url': self.success_url,
            'model': self.model,
            })

    def create_urls(self):
        model_name = self.model.__name__.lower()
        create_view_name = "%s-create" % model_name
        update_view_name = "%s-update" % model_name
        delete_view_name = "%s-delete" % model_name
        list_view_name = "%s-list" % model_name
        self.urls.append(url(r'^%s/?' % create_view_name , 
            self.create_klass.as_view(), name=create_view_name ))
        self.urls.append(url(r'^%s/?' % list_view_name , 
            self.list_klass.as_view(), name=list_view_name ))
        self.urls.append(url(r'^%s/(?P<pk>[\w]+)/?' % update_view_name , 
            self.update_klass.as_view(), name=update_view_name ))
        self.urls.append(url(r'^%s/(?P<pk>[\w]+)/?' % delete_view_name , 
            self.delete_klass.as_view(), name=delete_view_name ))
        
        return self.urls

