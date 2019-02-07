import datetime
import os

from services.models import TimeLog
from django.views.generic import TemplateView
from common_data.utilities import extract_period
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from common_data.views import ContextMixin
from common_data.forms import PeriodReportForm
from functools import reduce

import matplotlib as mpl
mpl.use("svg")
from matplotlib import pyplot as plt
from common_data.plot_utility import svgString

class ServicePersonUtilizationFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    form_class = PeriodReportForm
    
    extra_context = {
        'action':reverse_lazy('services:reports-service-person-utilization'),
    }

class ServicePersonUtilizationReport(TemplateView):
    template_name = os.path.join('services', 'reports', 'service_person_utilization.html')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        kwargs =  self.request.GET
        start, end = extract_period(kwargs)

        # fix
        logs = TimeLog.objects.filter(Q(date__gte=start), Q(date__lte=end))
        histogram = {}
        for log in logs:
            histogram.setdefault(str(log.employee), [])
            histogram[str(log.employee)].append(log.normal_time)

        x = histogram.keys()
        y = [reduce(lambda x,y: x + y, x[key], datetime.timedelta(seconds=0)) for key in x]
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel("Employees")
        ax.set_ylabel("Service Hours")

        ax.bar(x, y)
        context['graph'] = svgString(fig)
        context.update({
            'start': start,
            'end': end,
            'date': datetime.date.today(),
            'number_employees': len(x),
            'average_time': sum(y) / len(y)
            })
        return context
