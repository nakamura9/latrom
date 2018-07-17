# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-14 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_auto_20180714_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='cycle',
            field=models.IntegerField(choices=[(1, 'Daily'), (7, 'Weekly'), (14, 'Bi- Monthly'), (30, 'Monthly'), (90, 'Quarterly'), (182, 'Bi-Annually'), (365, 'Annually')], null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='expiration_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='recurring',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='expense',
            name='start_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='adjusted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='posted_to_general_ledger',
            field=models.BooleanField(default=False),
        ),
    ]