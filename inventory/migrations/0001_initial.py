# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-06 12:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        ('common_data', '0001_initial'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('next_adjustment_date', models.DateField(null=True)),
                ('comments', models.TextField()),
                ('adjusted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryController',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
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
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_name', models.CharField(max_length=32)),
                ('code', models.AutoField(primary_key=True, serialize=False)),
                ('pricing_method', models.IntegerField(choices=[(0, 'Manual'), (1, 'Margin'), (2, 'Markup')], default=0)),
                ('direct_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('margin', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('markup', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('unit_purchase_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('description', models.TextField(blank=True, default='')),
                ('image', models.FileField(blank=True, null=True, upload_to=b'F:\\Documents\\code\\git\\latrom\\media')),
                ('minimum_order_level', models.IntegerField(default=0)),
                ('maximum_stock_level', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Category')),
                ('sub_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_category', to='inventory.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_receipt_date', models.DateField()),
                ('issue_date', models.DateField()),
                ('type_of_order', models.IntegerField(choices=[(0, 'Cash Order'), (1, 'Deffered Payment Order'), (2, 'Pay on Receipt')], default=0)),
                ('deferred_date', models.DateField(blank=True, null=True)),
                ('supplier_invoice_number', models.CharField(blank=True, default='', max_length=32)),
                ('bill_to', models.CharField(blank=True, default='', max_length=128)),
                ('tracking_number', models.CharField(blank=True, default='', max_length=64)),
                ('notes', models.TextField()),
                ('status', models.CharField(choices=[('received-partially', 'Partially Received'), ('received', 'Received in Total'), ('draft', 'Internal Draft'), ('submitted', 'Submitted to Supplier')], max_length=24)),
                ('active', models.BooleanField(default=True)),
                ('received_to_date', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('order_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('received', models.FloatField(default=0.0)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Order')),
            ],
        ),
        migrations.CreateModel(
            name='StockAdjustment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjustment', models.FloatField()),
                ('note', models.TextField()),
                ('inventory_check', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryCheck')),
            ],
        ),
        migrations.CreateModel(
            name='StockReceipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receive_date', models.DateField()),
                ('note', models.TextField(blank=True, default='')),
                ('fully_received', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Order')),
                ('received_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Account')),
                ('individual', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Individual')),
                ('organization', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='TransferOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField()),
                ('expected_completion_date', models.DateField()),
                ('actual_completion_date', models.DateField(null=True)),
                ('order_issuing_notes', models.TextField(blank=True)),
                ('receive_notes', models.TextField(blank=True)),
                ('completed', models.BooleanField(default=False)),
                ('issuing_inventory_controller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issuing_inventory_controller', to='employees.Employee')),
                ('receiving_inventory_controller', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
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
        migrations.CreateModel(
            name='UnitOfMeasure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(default='')),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='WareHouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='WareHouseItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('verified', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Item')),
                ('warehouse', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse')),
            ],
        ),
        migrations.AddField(
            model_name='transferorder',
            name='receiving_warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse'),
        ),
        migrations.AddField(
            model_name='transferorder',
            name='source_warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_warehouse', to='inventory.WareHouse'),
        ),
        migrations.AddField(
            model_name='stockadjustment',
            name='warehouse_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouseItem'),
        ),
        migrations.AddField(
            model_name='order',
            name='ship_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse'),
        ),
        migrations.AddField(
            model_name='order',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Supplier'),
        ),
        migrations.AddField(
            model_name='order',
            name='tax',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.Tax'),
        ),
        migrations.AddField(
            model_name='item',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Supplier'),
        ),
        migrations.AddField(
            model_name='item',
            name='unit',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.UnitOfMeasure'),
        ),
        migrations.AddField(
            model_name='inventorycheck',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse'),
        ),
    ]
