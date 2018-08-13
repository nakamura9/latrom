# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-12 19:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0003_auto_20180807_2042'),
        ('employees', '0001_initial'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjustmet',
            name='entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.JournalEntry'),
        ),
        migrations.AddField(
            model_name='adjustmet',
            name='workbook',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.WorkBook'),
        ),
        migrations.AddField(
            model_name='asset',
            name='debit_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting.Account'),
        ),
        migrations.AddField(
            model_name='bookkeeper',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee'),
        ),
        migrations.AddField(
            model_name='credit',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.Account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='credit',
            name='entry',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.JournalEntry'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='debit',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.Account'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='debit',
            name='entry',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.JournalEntry'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expense',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invoicing.Customer'),
        ),
        migrations.AddField(
            model_name='expense',
            name='debit_account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.Account'),
            preserve_default=False,
        ),
    ]
