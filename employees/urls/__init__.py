from django.urls import re_path, path

from .department import department_urls 
from .employee import employee_urls
from .leave import leave_urls
from .misc import other_urls
from .payroll import pay_urls
from .time import timesheet_urls
from .portal import portal_urls 
from .reports import report_urls
from employees import views

urlpatterns = [
    re_path(r'^config-wizard', views.ConfigWizard.as_view(), name='config-wizard'),
    re_path(r'^$', views.Dashboard.as_view(), name='dashboard'),
    re_path(r'^async-dashboard/$', views.AsyncDashboard.as_view(), name='async-dashboard')
] + other_urls + \
    employee_urls + \
    pay_urls + \
    timesheet_urls + \
    pay_urls + \
    leave_urls + \
    department_urls + \
    portal_urls + \
    report_urls