# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-14 19:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0006_auto_20180714_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='interest_interval',
            field=models.IntegerField(choices=[(0, 'monthly'), (1, 'annually')], default=1),
        ),
        migrations.AddField(
            model_name='account',
            name='interest_method',
            field=models.IntegerField(choices=[(0, 'Simple'), (1, 'Commpound')], default=0),
        ),
        migrations.AddField(
            model_name='account',
            name='interest_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]