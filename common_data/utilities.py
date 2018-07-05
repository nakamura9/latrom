import json
import os
from latrom import settings 
class ExtraContext(object):
    extra_context = {}
    
    def get_context_data(self, **kwargs):
        context = super(ExtraContext, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

def apply_style(context):
    styles = {
            "1": "simple",
            "2": "blue",
            "3": "steel",
            "4": "verdant",
            "5": "warm"
            }
    context['style'] = styles[context["invoice_template"]]
    return context 

def load_config():
    if settings.TEST_RUN_MODE:
        file_name = settings.TEST_CONFIG_FILE
    else:
        file_name = settings.CONFIG_FILE
   

    if not os.path.exists(file_name):
        f = open(file_name, 'w')
        f.close()
    config_file = open(file_name, 'r')
    try:
        CONFIG = json.load(config_file)
    except Exception as e:
        print e.message
        CONFIG = {}
    config_file.close()

    return CONFIG

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

    
class ModelTestTools(object):
    pass