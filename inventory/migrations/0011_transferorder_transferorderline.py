# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-17 19:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0005_paygrade_payroll_taxes'),
        ('inventory', '0010_warehouseitem_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField()),
                ('expected_completion_date', models.DateField()),
                ('actual_completion_date', models.DateField(null=True)),
                ('order_issuing_notes', models.TextField()),
                ('receive_notes', models.TextField()),
                ('completed', models.BooleanField(default=False)),
                ('issuing_inventory_controller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issuing_inventory_controller', to='employees.Employee')),
                ('receiving_inventory_controller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
                ('receiving_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse')),
                ('source_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_warehouse', to='inventory.WareHouse')),
            ],
        ),
        migrations.CreateModel(
            name='TransferOrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Item')),
                ('transfer_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.TransferOrder')),
            ],
        ),
    ]
