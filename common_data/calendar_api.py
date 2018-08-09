import calendar
import datetime
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse

'''
request body
{
    'current': int
    'view': str
}
'''

def get_calendar(request):
    TODAY = datetime.date.today()
    print request.GET
    views = {
        'month': get_month_views, 
        'week': get_week_views,
        'day': get_day_view
    }
    data_array = views[request.GET.get('view')](
        int(request.GET.get('current'))
    )
    payload = {
        'data': data_array
    }
    print payload
    return JsonResponse(payload)

def get_month_views(current):
    '''returns a list of weeks'''
    TODAY = datetime.date.today()
    current_date = TODAY + relativedelta(months=current)
    c = calendar.Calendar(calendar.MONDAY)
    array = c.monthdatescalendar(
        current_date.year,
        current_date.month)
    return [[get_day(date) for date in week] for week in array]

def get_week_views(current):
    '''returns a list of days'''
    TODAY = datetime.date.today()
    current_date = TODAY + relativedelta(weeks=current)
    print current_date
    curr_weekday = current_date.weekday()
    array = [current_date + datetime.timedelta(days=i) \
        for i in (range(0 - curr_weekday, 7-curr_weekday))]
    return [get_day(date) for date in array]

def get_day_view(current):
    '''returns a list of events'''
    TODAY = datetime.date.today()
    current_date = TODAY + datetime.timedelta(current)
    return get_day(current_date)


def get_day(date):
    return {
        'day': date.day,
        'events': []
    }

def get_inventory_events():
    pass


def get_sales_events():
    pass

def get_employees_events():
    pass

def get_accounting_events():
    pass