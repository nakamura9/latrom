# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-14 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0007_auto_20180714_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='last_created_date',
            field=models.DateField(null=True),
        ),
    ]
