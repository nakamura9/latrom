# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-15 06:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20180814_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagemedia',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.UnitOfMeasure'),
        ),
    ]