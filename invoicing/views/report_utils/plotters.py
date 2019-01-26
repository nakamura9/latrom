import matplotlib as mpl
mpl.use("svg")
from matplotlib import pyplot as plt
from common_data.plot_utility import svgString
import datetime
from invoicing.models import SalesInvoice
from dateutil import relativedelta

# TODO test


def plot_sales(start, end):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    #set deltas
    y = None
    delta = None

    date_range = (end - start).days
    if abs(date_range) > 70:
        delta = 30
        

    elif abs(date_range) > 20:
        delta = 7
    
    else:

        delta = 1

    dates = mpl.dates.drange(start, end, datetime.timedelta(days=delta))
    y_query = get_queryset_list(start, end, delta)
    
    _, locator, formatter = get_date_tuples(start, end)

    y = [get_sales_totals(q) for q in y_query]

    ax.set_xlabel("Dates")
    ax.set_ylabel("Sales")

    ax.bar(dates, y, width=delta)
    ax.xaxis_date()

    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)


    fig.autofmt_xdate()


    return svgString(fig)

def get_sales_totals(queryset):
    total = 0
    for invoice in queryset:
        total += invoice.total

    return total

def get_queryset_list(start, end, delta):
    curr_date = start
    prev_date = start
    query_list = []

    while curr_date < end:
        curr_date  = curr_date + datetime.timedelta(days=delta)
        query_list.append(SalesInvoice.objects.filter(
            date__gt=prev_date, date__lte=curr_date
        ))
        prev_date = curr_date


    return query_list


def get_date_tuples(start, end):
    '''No more than 10 pieces of data must be displayed at any time'''
    date_range = abs((end- start).days)

    if date_range > 70:
        #months 
        delta = relativedelta.relativedelta(months=1)
        locator = mpl.dates.MonthLocator()
        formatter = mpl.dates.DateFormatter("%B  %Y")
    elif date_range > 10:
        delta = datetime.timedelta(days=7)
        locator = mpl.dates.WeekdayLocator(mpl.dates.MO)
        formatter = mpl.dates.DateFormatter("%d/%m/%y")
    else:
        delta = datetime.timedelta(days=1)
        locator = mpl.dates.DayLocator()
        formatter =mpl.dates.DateFormatter("%d %B '%y")

    curr_date = start
    prev_date = None
    dates = []

    while curr_date < end:
        prev_date = curr_date
        curr_date = curr_date + delta
        dates.append((prev_date, curr_date))

    if curr_date != end:
        dates.append((prev_date, end))

    return dates, locator, formatter
