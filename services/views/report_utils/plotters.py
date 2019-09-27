import pygal
from pygal.style import DefaultStyle


def plot_expense_breakdown(work_order):
    chart = pygal.Pie(print_values=True, style=DefaultStyle(
        value_font_size=30, 
        value_colors=('white', )
        ) 
    )
    chart.title = 'Work Order Expenses Breakdown'
    for exp in work_order.expenses:
        chart.add(exp.expense.category_string, exp.expense.amount)
    total_wages = sum([log.total_cost for log in work_order.time_logs])
    chart.add('Wages', total_wages)
    for con in work_order.consumables_used:
        chart.add(con.consumable.name, con.line_value)

    return chart.render(is_unicode=True)