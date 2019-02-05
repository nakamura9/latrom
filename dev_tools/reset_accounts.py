'''
Usage:
========
    python manage.py shell
    >>> exec(open("reset_accounts.py").read())
'''

from accounting.models import (Account, 
                                JournalEntry, 
                                Expense, 
                                RecurringExpense, 
                                Asset)

for a in Account.objects.all():
    a.balance = 0
    a.save()

JournalEntry.objects.all().delete()
Expense.objects.all().delete()
Asset.objects.all().delete()
RecurringExpense.objects.all().delete()