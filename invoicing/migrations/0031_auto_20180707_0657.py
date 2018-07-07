# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-07 04:57
from __future__ import unicode_literals

from django.db import migrations, models
import invoicing.models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0030_auto_20180707_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='comments',
            field=models.TextField(blank=True, default=invoicing.models.get_default_comments, null=True),
        ),
    ]