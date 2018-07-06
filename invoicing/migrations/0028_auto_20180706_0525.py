# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-06 03:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0027_remove_invoice_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='comments',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='terms',
            field=models.CharField(default='', max_length=128),
        ),
    ]
