'''
Usage:
========
    python manage.py shell
    >>> exec(open("dev_tools/reset_accounts.py").read())
'''

from accounting.models import (Account, 
                                JournalEntry, 
                                Expense, 
                                RecurringExpense, 
                                Asset)
from inventory.models import WareHouseItem, Order, OrderItem, WareHouseItem
from invoicing.models import Invoice, InvoiceLine


for a in Account.objects.all():
    a.balance = 0
    a.save()

JournalEntry.objects.all().delete()
Expense.objects.all().delete()
Asset.objects.all().delete()
RecurringExpense.objects.all().delete()
for i in Order.objects.all():
    i.delete()
OrderItem.objects.all().delete()
for i in Invoice.objects.all():
    i.hard_delete()
InvoiceLine.objects.all().delete()
WareHouseItem.objects.all().delete()
