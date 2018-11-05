import calendar
import datetime
import time

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.http import JsonResponse

from inventory.models import InventoryCheck
from invoicing.models import AbstractSale

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
    
    event_objs = Event.objects.filter(filters & Q(owner=user))
    events += [{
        'label': e.label,
        'icon': e.icon,
        'date': e.date,
        'id': e.pk
    } for e in event_objs]
    events = sorted(events, key=lambda x: x['date'])
    res = [{
        'date': i,
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

def get_month_views(current, user):
    '''returns a list of weeks'''
    TODAY = datetime.date.today()
    current_date = TODAY + relativedelta(months=current)
    c = calendar.Calendar(calendar.MONDAY)
    array = c.monthdatescalendar(
        current_date.year,
        current_date.month)
    period_string = current_date.strftime('%B, %Y')
    return get_month_data(array, user), period_string

def get_month(request, year=None, month=None):
    year = int(year)
    month= int(month)
    current_date = datetime.date(year, month, 1)
    array = c.monthdatescalendar(year, month)
    period_string = current_date.strftime('%B, %Y')
    user = request.user
    return JsonResponse({
        'period_string': period_string,
        'weeks': get_month_data(array, user)
    })

def get_week_views(current, user):
    '''returns a list of days'''
    TODAY = datetime.date.today()
    current_date = TODAY + relativedelta(weeks=current)
    curr_weekday = current_date.weekday()
    array = [current_date + datetime.timedelta(days=i) \
        for i in (range(0 - curr_weekday, 7-curr_weekday))]
    year, week, wkday = current_date.isocalendar()
    period_string = "%d, (%s) %d" % (week, current_date.strftime('%B'), year)
    return [get_day(date, user) for date in array], period_string

def get_day_view(current, user):
    '''returns a list of events'''
    TODAY = datetime.date.today()
    current_date = TODAY + datetime.timedelta(current)
    data = get_day(current_date, user)
    return data, ''


def get_day(date, user):
    events = [{
        'label': e.label,
        'icon': e.icon,
        'date': e.date,
        'id': e.pk 
    } for e in Event.objects.filter(Q(date=date) & Q(owner=user))]

    return {
        'day': date.day,
        'date': date,
        'events': events
    }
