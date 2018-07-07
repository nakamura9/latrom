# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-06 10:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_auto_20180705_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=b'F:\\Documents\\code\\git\\latrom\\media'),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=models.deletion.CASCADE, to='inventory.UnitOfMeasure'),
        )
    ]