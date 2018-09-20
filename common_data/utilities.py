import datetime
import json
import os

from django.urls import re_path
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework.pagination import PageNumberPagination

import invoicing
from latrom import settings


class ConfigMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(ConfigMixin, self).get_context_data(*args, **kwargs)
        context.update(invoicing.models.SalesConfig.objects.first().__dict__)
        return apply_style(context)

class PDFMixin(object):
    pass

class EmailMixin(object):
    pass

class WareHousePaginator(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_description = 'page_size'

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
            'form_class': self.create_form
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
            'form_class': self.create_form
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
        self.urls.append(re_path(r'^%s/?' % create_view_name , 
            self.create_klass.as_view(), name=create_view_name ))
        self.urls.append(re_path(r'^%s/?' % list_view_name , 
            self.list_klass.as_view(), name=list_view_name ))
        self.urls.append(re_path(r'^%s/(?P<pk>[\w]+)/?' % update_view_name , 
            self.update_klass.as_view(), name=update_view_name ))
        self.urls.append(re_path(r'^%s/(?P<pk>[\w]+)/?' % delete_view_name , 
            self.delete_klass.as_view(), name=delete_view_name ))
        
        return self.urls


class ExtraContext(object):
    extra_context = {}
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.extra_context)
        return context

def apply_style(context):
    styles = {
            1: "simple",
            2: "blue",
            3: "steel",
            4: "verdant",
            5: "warm"
            }
    context['style'] = styles[context["document_theme"]]
    return context 


class Modal(object):
    '''for every modal use a object that contains the trigger link id, the modal form the modal action
extra_context = {
    'modals' : [Modal(
        {'title':''
        'action' : '',
        'form' : ''
    }
    )
        ]
}'''
    def __init__(self, title, action, form):
        self.title= title
        self.link= 'id'  + '-' + title.lower().replace(' ', '-')
        self.action= action
        self.form = form

    
def extract_period(kwargs):
    n = kwargs.get('default_periods', None)
    if n and n != '0':
        deltas = {
                '1': 30,
                '2': 90,
                '3': 180
            }
        end = datetime.date.today()
        start = end - datetime.timedelta(
                days=deltas[n])
    else:
        start = datetime.datetime.strptime(
            kwargs['start_period'], "%m/%d/%Y")
        end = datetime.datetime.strptime(
            kwargs['end_period'], "%m/%d/%Y")

    return (start, end)

def time_choices(start, stop, interval, delta=False):
    """
    Creates a list of times between start and stop separated by interval.

    Inputs
    =======
        start and stop are strings that represent time in the format H:M:00.
        interval is the time to be incremented between start and stop in the
        same format as above.
        delta, boolean, whether return elements are timedeltas
    Returns:
    =======
    The function returns a list of tuples in human readable format from
    the start time up to but not including the end time. 
    either 
        [(timedelta, string), ...]
    or
        [(time, string), ...] 
    """

    times = []
    try:
        _start = datetime.datetime.strptime(start, "%H:%M:%S").time()
        _stop = datetime.datetime.strptime(stop, "%H:%M:%S").time()
        _interval = datetime.datetime.strptime(interval, "%H:%M:%S").time()
    except:
        raise Exception("the times supplied do not match the required format")

    current_time = _start
    while current_time < _stop:
        if delta:
            times.append((datetime.timedelta(hours=current_time.hour,
                                            minutes=current_time.minute),
                                                current_time.strftime("%H:%M")))
        else:
            times.append((current_time ,current_time.strftime("%H:%M")))
        
        current_time = (datetime.datetime.combine(datetime.date.today(), current_time) \
                        + datetime.timedelta(hours = _interval.hour,
                                            minutes=_interval.minute,
                                            seconds=_interval.second)).time()
    return times
