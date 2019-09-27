from accounting.models import Expense, expense_choices
from invoicing.models import Invoice
from invoicing.views.report_utils.plotters import (pygal_date_formatter, 
                                                   get_sales_totals,
                                                   get_queryset_list)
import datetime
import pygal
from pygal.style import DefaultStyle
from django.db.models import Q

def expense_plot():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=30)
    expenses = Expense.objects.filter(Q(date__gte=start) & Q(date__lte=today))
    if expenses.count() == 0:
        return None

    mapping = {}

    for expense in expenses:
        mapping[expense.category] = mapping.setdefault(
            expense.category, 0) + expense.amount

    total = 0
    for key in mapping.keys():
        total += mapping[key]

    chart = pygal.Pie(print_values=True, style=DefaultStyle(
        value_font_size=30, 
        value_colors=('white', )
        ) 
    )
    chart.title = 'Expenses breakdown over the last 30 days'
    for key in mapping.keys():
        chart.add(expense_choices[key], mapping[key])


    return chart

def get_expense_totals(qset):
    total = 0
    for exp in qset:
        total += exp.amount

    return total
     
def revenue_vs_expense_plot():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=30)
    _expenses = Expense.objects.filter(Q(date__gte=start) & Q(date__lte=today))
    _revenue = Invoice.objects.filter(Q(date__gte=start) & Q(date__lte=today))

    dates = pygal_date_formatter(start, today)
    # get invoice totals for each week
    inv_query_list = get_queryset_list(Invoice, start, today, 7, filters=Q(
            Q(status='invoice') | 
            Q(status='paid') | 
            Q(status='paid-partially')) & 
            Q(draft=False))
    revenue = [get_sales_totals(q) for q in inv_query_list]
    #get expense totals for each week
    expense_query_list = get_queryset_list(Expense, start, today, 7)
    expenses = [get_expense_totals(q) for q in expense_query_list]
    #get the difference for each week
    profit = []
    for i in range(len(revenue)):
        profit.append(revenue[i] - expenses[i])
    

    chart = pygal.Bar(x_title="Week Ending", x_label_rotation=15, )
    chart.title = "Revenue vs Expenses"
    chart.x_labels = dates
    chart.add("Revenue", revenue)
    chart.add("Expenses", expenses)
    chart.add("Profit", profit)

    return chart