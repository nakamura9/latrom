import pygal

def plot_expense_breakdown(work_order):
    chart = pygal.Pie()
    chart.title = 'Work Order Expenses Breakdown'
    for exp in work_order.expenses:
        chart.add(exp.expense.category_string, exp.expense.amount)
    total_wages = sum([log.total_cost for log in work_order.time_logs])
    chart.add('Wages', total_wages)

    return chart.render(is_unicode=True)