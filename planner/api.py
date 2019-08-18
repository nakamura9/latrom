import calendar
import datetime
import time

from django.db.models import Q
from django.http import JsonResponse

from inventory.models import InventoryCheck
from invoicing.models.invoice import Invoice

from .l2d import List2D
from .models import Event


def reshape(data, shape):
    i = 0
    res = []
    for row in range(shape[0]):
        res.append(data[i * shape[1]: (1 + i) * shape[1]])
        i += 1
    return res

def get_filters(start, end, field="date"):
    lt = field + '__lte'
    gt = field + '__gte'
    return(Q(Q(**{lt: end}) & Q(**{gt: start})))

def get_calendar(request):
    TODAY = datetime.date.today()
    user = request.user
    views = {
        'month': get_month_views, 
        'week': get_week_views,
        'day': get_day_view
    }
    data_array, period = views[request.GET.get('view')](
        int(request.GET.get('current')), user
    )
    payload = {
        'data': data_array,
        'period': period
    }
    return JsonResponse(payload)


def get_month_data(array, user):
    '''benchmark later:
        1. requesting the DB every day
        2. requesting sorting the data
        3. requesting without sorting'''
    now = time.time()
    l2D = List2D(array)
    flat = l2D.flatten()
    shape = l2D.shape
    events = []
    filters = get_filters(flat[0], flat[len(flat)- 1])
    
    if hasattr(user, 'employee'):
        event_objs = Event.objects.filter(filters & Q(
            Q(owner=user) | Q(eventparticipant__employee__in=[user.employee.pk])))
    else:
        event_objs = Event.objects.filter(filters & Q(owner=user))
    events += [{
        'label': e.label,
        'icon': e.icon,
        'date': e.date,
        'id': e.pk
    } for e in event_objs]

    active_recurring = Event.objects.filter(
        Q(repeat_active=True) & Q(owner=user))
    
    for evt in active_recurring:
        for date in flat:
            if evt.repeat_on_date(date):
                events.append({
                    'label': evt.label,
                    'icon': evt.icon,
                    'date': date,
                    'id': evt.pk 
                })
    
    events = sorted(events, key=lambda x: x['date'])
    res = [{
        'date': i.strftime("%Y/%m/%d"),
        'day': i.day,
        'events' :[]
        } for i in flat]
    for e in events:
        count = 0
        for i in flat:
            if e['date'] == i:
                res[count]['events'].append(e)
                break
            else:
                count += 1 
    data = reshape(res, (shape))
    return  data

def get_month(request, year=None, month=None):
    year = int(year)
    month= int(month)
    current_date = datetime.date(year, month, 1)
    c = calendar.Calendar(calendar.MONDAY)
    array = c.monthdatescalendar(year, month)
    period_string = current_date.strftime('%B, %Y')
    user = request.user
    return JsonResponse({
        'period_string': period_string,
        'weeks': get_month_data(array, user)
    })

def get_week(request, year=None, month=None, day=None):
    year = int(year)
    month= int(month)
    day=int(day)

    current_date = datetime.date(year, month, day)
    curr_weekday = current_date.weekday()
    array = [current_date + datetime.timedelta(days=i) \
        for i in (range(0 - curr_weekday, 7-curr_weekday))]
    year, week, wkday = current_date.isocalendar()
    period_string = "%d, (%s) %d" % (week, current_date.strftime('%B'), year)
    user = request.user
        
    return JsonResponse({
        'period_string': period_string,
        'days': [_get_day(date, user) for date in array]
    })

def get_day(request, year=None, month=None, day=None):
    year = int(year)
    month= int(month)
    day=int(day)

    current_date = datetime.date(year, month, day)
    period_string = current_date.strftime("%A, %d %B %Y")
    user = request.user
        
    return JsonResponse({
        'date': period_string,
        'events': _get_day(current_date, user)
    })

def _get_day(date, user):
    if hasattr(user, 'employee'):
        qs = Event.objects.filter(Q(date=date) & 
            Q(Q(owner=user) | Q(eventparticipant__employee__in=[user.employee.pk])))
    else:
        qs = Event.objects.filter(Q(date=date) & Q(owner=user))
    events = [{
        'label': e.label,
        'icon': e.icon,
        'date': e.date,
        'start': e.start_time.strftime('%H:%M'),
        'end': e.end_time.strftime('%H:%M'),
        'id': e.pk 

    } for e in qs]

    events += [{
        'label': e.label,
        'icon': e.icon,
        'date': e.date,
        'start': e.start_time.strftime('%H:%M'),
        'end': e.end_time.strftime('%H:%M'),
        'id': e.pk 
    } for e in Event.objects.filter(Q(repeat_active=True) & Q(owner=user)) \
        if e.repeat_on_date(date)]

    return {
        'day': date.day,
        'date': date.strftime('%Y/%m/%d'),
        'events': events
    }
