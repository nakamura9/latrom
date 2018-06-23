import json

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
    config_file = open('config.json')
    CONFIG = json.load(config_file)
    config_file.close()
    
    return CONFIG

def income_tax_calculator(gross):
    upper_limits = [0, 300, 1500, 3000, 5000, 10000, 15000, 20000]
    rates = {
        (0,300) : (0, 0),
        (300,1500) : (20, 60),
        (1500,3000) : (25, 135),
        (3000,5000) : (30, 285),
        (5000,10000) : (35, 535),
        (10000,15000) : (40, 1035),
        (15000,20000) : (45, 1785),
    }
    count = 0
    for limit in upper_limits:
        if gross >= limit:
            count += 1 
        else:
            bracket = (upper_limits[count -1], limit)
            break
    
    
    return ((gross * rates[bracket][0])/100) - rates[bracket][1]

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

    