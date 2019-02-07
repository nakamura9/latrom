from functools import reduce
from decimal import Decimal as D
from accounting import models 
from inventory import models as inventory_models
from django.db.models import Q

def net_profit_calculator(start, end):

    # sales
    sales_acc = models.Account.objects.get(pk=4000)
    sales_balance_carried_over = sales_acc.balance_on_date(start)
    sales = sales_acc.balance - sales_balance_carried_over
    
    #purchases
    # TODO verify if opening inventory is considered in profit and loss statement

    purchases_acc = models.Account.objects.get(pk=4006)
    purchases = purchases_acc.balance_over_period(start, end)
    
    opening_inventory = sum(
        [D(i.quantity_on_date(start)) * i.unit_value for i in inventory_models.Product.objects.all()])
    
    closing_inventory = inventory_models.Product.total_inventory_value()
    cogs = opening_inventory +  purchases - closing_inventory

    other_income = models.Account.objects.filter(type="income").exclude(
        Q(balance=0.0)).exclude(Q(pk__in=[4000]))

    other_income_total = sum([i.control_balance for i in other_income])

    total_gross_profit = sales - cogs + other_income_total


    expenses = models.Account.objects.filter(
        type="expense").exclude(
            Q(balance=0.0))

    total_expenses = sum([i.control_balance for i in expenses])
    
    return total_gross_profit - total_expenses