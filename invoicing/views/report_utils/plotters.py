import datetime
from invoicing.models.invoice import Invoice, InvoiceLine
from invoicing.models.customer import Customer
from dateutil import relativedelta
from django.db.models import Q

import pygal
from pygal.style import DefaultStyle


def plot_sales(start, end, filters=Q()):
    y = None
    delta = None

    date_range = (end - start).days
    if abs(date_range) > 70:
        delta = 30
        

    elif abs(date_range) > 20:
        delta = 7
    
    else:
        delta = 1

    y_query = get_queryset_list(Invoice, start, end, delta, filters=Q( 
            Q(status='invoice') | 
            Q(status='paid') | 
            Q(status='paid-partially')) & 
            Q(draft=False) & filters)

    y = [get_sales_totals(q) for q in y_query]


    chart = pygal.Bar(x_title="Periods", x_label_rotation=15)
    chart.title = 'Sales Report'
    chart.x_labels = pygal_date_formatter(start, end)
    chart.add('Sales($)', y)
    

    return chart.render(is_unicode=True)


def plot_sales_by_customer(start, end):
    invs = Invoice.objects.filter(
        Q(date__gte=start) & Q(date__lte=end) &
        Q(draft=False) &
        Q(status__in=['paid', 'paid-partially', 'invoice']))

    sbc = {}
    for i in invs:
        sbc.setdefault(str(i.customer), 0) 
        sbc[str(i.customer)] += i.subtotal

    chart = pygal.Pie(print_values=True, style=DefaultStyle(
        value_font_size=30, 
        value_colors=('white', )
        ) 
    )
    chart.title = 'Sales By Customer'
    for key in sbc.keys():
        chart.add(key, sbc[key])

    return chart.render(is_unicode=True)


def plot_sales_by_products_and_services(start, end):
    lines = InvoiceLine.objects.filter(
        Q(invoice__date__gte=start) & 
        Q(invoice__date__lte=end) &
        Q(invoice__draft=False) &
        Q(expense__isnull=True) &
        Q(invoice__status__in=['paid', 'paid-partially', 'invoice']))

    sbps = {}
    for l in lines:
        sbps.setdefault(l.name, 0) 
        sbps[l.name] += l.subtotal

    chart = pygal.Pie(print_values=True, style=DefaultStyle(
        value_font_size=30, 
        value_colors=('white', )
        ) 
    )
    chart.title = 'Sales By Products and Services'
    ordered = sorted([(key, sbps[key]) for key in sbps.keys()], 
        key=lambda x: x[1], reverse=True)
    for item in ordered[:10]:
        chart.add(item[0], item[1])

    return chart.render(is_unicode=True)



def get_sales_totals(queryset):
    total = 0
    for invoice in queryset:
        total += invoice.subtotal# no tax

    return total

def get_line_totals(queryset):
    total = 0
    for invoiceline in queryset:
        total += invoiceline.subtotal# no tax

    return total

def get_queryset_list(obj, start, end, delta, filters=Q()):
    curr_date = start
    prev_date = start
    query_list = []

    while curr_date < end:
        curr_date  = curr_date + datetime.timedelta(days=delta)
        query_list.append(obj.objects.filter(
            Q(date__gt=prev_date) & 
            Q(date__lte=curr_date) & filters))
        prev_date = curr_date


    return query_list

def get_line_queryset_list(obj, start, end, delta, filters=Q()):
    '''
    List returned has elements that represent a single bar on the bar chart
    '''
    curr_date = start
    prev_date = start
    query_list = []
    while curr_date < end:
        curr_date  = curr_date + datetime.timedelta(days=delta)
        query_list.append(obj.objects.filter(
            Q(invoice__date__gt=prev_date) &
                Q(invoice__date__lte=curr_date) &
                Q(invoice__draft=False) &
                Q(
                    Q(invoice__status='invoice') | 
                    Q(invoice__status='paid') | 
                    Q(invoice__status='paid-partially')
                ) & filters))
        prev_date = curr_date


    return query_list

def pygal_date_formatter(start, end):
    date_range = abs((end- start).days)

    if date_range > 70:
        #months 
        delta = relativedelta.relativedelta(months=1)
        formatter = "%B  %Y"
    elif date_range > 10:
        delta = datetime.timedelta(days=7)
        formatter = "%d/%m/%y"
    else:
        delta = datetime.timedelta(days=1)
        formatter ="%d %B '%y"

    curr_date = start
    prev_date = None
    dates = []

    while curr_date < end:
        prev_date = curr_date
        curr_date = curr_date + delta
        dates.append(prev_date)

    if curr_date != end:
        dates.append(end)

    return [d.strftime(formatter) for d in dates]

def plot_ar_by_customer():
    chart = pygal.Pie(print_values=True, style=DefaultStyle(
        value_font_size=30, 
        value_colors=('white', )
        ) 
    )
    chart.title = 'A/R By Customer'
    for cus in Customer.objects.filter(account__balance__gt=0):
        chart.add(str(cus), cus.total_accounts_receivable)

    return chart.render(is_unicode=True)

def plot_ar_by_aging():
    chart = pygal.Pie(print_values=True, style=DefaultStyle(
        value_font_size=30, 
        value_colors=('white', )
        ) 
    )
    chart.title = 'A/R By Aging'

    invs = Invoice.objects.filter(status__in=['invoice', 'paid-partially'])


    chart.add("Current", sum([i.total for i in filter(
        lambda x: x.overdue_days == 0, invs)]))
    chart.add('0-7 Days',sum([i.total for i in filter(
        lambda x: x.overdue_days > 0 and x.overdue_days < 7, invs)]))
    chart.add('8-14 Days', sum([i.total for i in filter(
        lambda x: x.overdue_days > 6 and x.overdue_days < 15, invs)]))
    chart.add('15-30 Days', sum([i.total for i in filter(
        lambda x: x.overdue_days > 14 and x.overdue_days < 31, invs)]))
    chart.add('31-60 Days', sum([i.total for i in filter(
        lambda x: x.overdue_days > 30 and x.overdue_days < 61, invs)]))
    chart.add('61+ Days', sum([i.total for i in filter(
        lambda x: x.overdue_days > 60, invs)]))
    

    return chart.render(is_unicode=True)
