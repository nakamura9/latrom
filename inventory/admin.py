# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

admin.site.register(UnitOfMeasure)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Order)
admin.site.register(OrderItem)

# Register your models here.
