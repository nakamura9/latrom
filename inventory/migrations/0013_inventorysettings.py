# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-20 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20180718_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventorySettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory_valuation_method', models.PositiveSmallIntegerField(choices=[(1, 'Averaging'), (2, 'FIFO'), (3, 'LIFO'), (4, 'Last order price')], default=1)),
                ('item_sales_pricing_method', models.PositiveSmallIntegerField(choices=[(1, 'Direct Pricing'), (2, 'Margin'), (3, 'Markup')], default=1)),
                ('order_template_theme', models.PositiveSmallIntegerField(choices=[(1, 'Simple'), (2, 'Blue'), (3, 'Steel'), (4, 'Verdant'), (5, 'Warm')], default=1)),
                ('inventory_check_frequency', models.PositiveSmallIntegerField(choices=[(1, 'Monthly'), (2, 'Quarterly'), (3, 'Bi-Annually'), (4, 'Annually')], default=1)),
                ('inventory_check_date', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
