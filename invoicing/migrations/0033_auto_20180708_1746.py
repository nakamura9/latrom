# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-08 15:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0032_auto_20180707_0658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invoicing.Invoice'),
        ),
    ]
