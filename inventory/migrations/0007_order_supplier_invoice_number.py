# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-14 18:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_warehouseitem_warehouse'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='supplier_invoice_number',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]
