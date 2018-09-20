# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from accounting import models

admin.site.register(models.Account)
admin.site.register(models.JournalEntry)
admin.site.register(models.Journal)
