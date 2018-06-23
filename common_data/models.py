from __future__ import unicode_literals

from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length =32)
    last_name = models.CharField(max_length =32)
    address = models.TextField(max_length =128, blank=True, default="")
    email = models.CharField(max_length =32, blank=True, default="")
    phone = models.CharField(max_length =16, blank=True, default="")

    class Meta:
        abstract = True