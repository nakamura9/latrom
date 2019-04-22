import pygal
from django.db.models import Q
from employees import models
from services.models import ServicePerson
from invoicing.models import SalesRepresentative
from accounting.models import Bookkeeper
from inventory.models import InventoryController


def employee_roles_chart():
    # take all 5 role categories and count the number of employees with each role
    # plot that count in a pie chart
    roles = {'Payroll Officers': models.PayrollOfficer, 
            'Bookkeepers':Bookkeeper, 
            'Service People':ServicePerson, 
            'Sales Representatives':SalesRepresentative, 
            'Inventory Controllers':InventoryController}

    chart = pygal.Pie()
    for role in roles.keys():
        chart.add(role, roles[role].objects.all().count())

    return chart