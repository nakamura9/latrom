
import django_filters

from . import models


class BillFilter(django_filters.FilterSet):
    class Meta:
        model = models.Bill
        fields = {
            'vendor': ['exact'],
            'date': ['exact']
        }

class JournalFilter(django_filters.FilterSet):
    class Meta:
        model = models.Journal
        fields = {
            'name': ['icontains'],
        }

class AccountFilter(django_filters.FilterSet):
    class Meta:
        model = models.Account
        fields = {
            'name': ['icontains'],
            'type': ['exact']
        }

class TaxFilter(django_filters.FilterSet):
    class Meta:
        model = models.Tax
        fields = {
            'name': ['icontains']
        }


class BookkeeperFilter(django_filters.FilterSet):
    class Meta:
        model = models.Bookkeeper
        fields = {
            'employee': ['exact']
        }


class ExpenseFilter(django_filters.FilterSet):
    class Meta:
        model = models.Expense
        fields = {
            'date': ['exact'],
            'category': ['exact'],
            'description': ['icontains'],
        }


class RecurringExpenseFilter(django_filters.FilterSet):
    class Meta:
        model = models.RecurringExpense
        fields = {
            'category': ['exact'],
            'description': ['icontains'],
        }


class AssetFilter(django_filters.FilterSet):
    class Meta:
        model = models.Asset
        fields = {
            'name': ['icontains'],
            'category': ['exact'],
            'init_date': ['gt', 'lt']

        }
        