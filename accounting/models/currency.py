import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone


class Currency(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=8)

    def __str__(self):
        return self.name

class CurrencyConversionTable(models.Model):
    name = models.CharField(max_length=255)
    reference_currency = models.ForeignKey('accounting.Currency', 
        on_delete=models.SET_NULL, null=True, related_name="reference_currency", default=1)

    def __str__(self):
        return self.name

class CurrencyConversionLine(models.Model):
    currency = models.ForeignKey('accounting.Currency', 
        on_delete=models.SET_NULL, null=True, related_name="exchange_currency")
    exchange_rate = models.DecimalField(max_digits=16, decimal_places=2)
    conversion_table = models.ForeignKey('accounting.CurrencyConversionTable',
        on_delete=models.SET_NULL, null=True)

