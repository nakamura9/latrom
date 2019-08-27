import calendar
import datetime
import time

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.http import JsonResponse

from inventory.models import InventoryCheck
from invoicing.models import Invoice
from l2d import List2D


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

def get_month_data(array):
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
    invoices = Invoice.objects.filter(filters)
    checks = InventoryCheck.objects.filter(filters)
    events += [{
        'label': 'Invoice Due',
        'icon': 'receipt',
        'date': i.date
    } for i in invoices]
    events += [{
        'label': 'Inventory Check',
        'icon': 'check',
        'date': c.date 
    } for c in checks]
    events = sorted(events, lambda x,y: x['date'] < y['date'], )
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
                continue
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
    #data = [[get_day(date, user) for date in week] for week in array]

    return get_month_data(array), period_string

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
    events = []
    if hasattr(user,'employee'):
        if user.is_sales_rep:
            events += get_sales_events(date)
        if user.is_inventory_controller:
            events += get_inventory_events(date)
        if user.is_bookkeeper:
            events += get_accounting_events(date)
    elif user.is_superuser:
        events += get_accounting_events(date) + get_inventory_events(date) + \
            get_sales_events(date)
    return {
        'day': date.day,
        'date': date,
        'events': events
    }

def get_inventory_events(date):
    #order due dates 
    #inventory_checks
    #
    checks = InventoryCheck.objects.filter(date=date)
    return [{
        'label': 'Inventory Check',
        'icon': 'check'
    } for c in checks]

    pass

def get_sales_events(date):
    invoices = Invoice.objects.filter(Q(due=date))
    return [{
        'label': 'Invoice Due',
        'icon': 'receipt'
    } for c in invoices]

def get_employees_events(date):
    return []

def get_accounting_events(date):
    return []
