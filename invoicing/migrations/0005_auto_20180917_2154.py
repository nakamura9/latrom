# Generated by Django 2.1.1 on 2018-09-17 19:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0004_auto_20180814_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstractsale',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=None, to='invoicing.Customer'),
        ),
        migrations.AlterField(
            model_name='abstractsale',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='abstractsale',
            name='due',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='abstractsale',
            name='salesperson',
            field=models.ForeignKey(default=1, on_delete=None, to='invoicing.SalesRepresentative'),
        ),
        migrations.AlterField(
            model_name='abstractsale',
            name='tax',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='accounting.Tax'),
        ),
        migrations.AlterField(
            model_name='billline',
            name='bill',
            field=models.ForeignKey(on_delete=None, to='invoicing.Bill'),
        ),
        migrations.AlterField(
            model_name='billline',
            name='expense',
            field=models.ForeignKey(on_delete=None, to='accounting.Expense'),
        ),
        migrations.AlterField(
            model_name='combinedinvoiceline',
            name='expense',
            field=models.ForeignKey(null=True, on_delete=None, to='accounting.Expense'),
        ),
        migrations.AlterField(
            model_name='combinedinvoiceline',
            name='invoice',
            field=models.ForeignKey(default=1, on_delete=None, to='invoicing.CombinedInvoice'),
        ),
        migrations.AlterField(
            model_name='combinedinvoiceline',
            name='product',
            field=models.ForeignKey(null=True, on_delete=None, to='inventory.Product'),
        ),
        migrations.AlterField(
            model_name='combinedinvoiceline',
            name='service',
            field=models.ForeignKey(null=True, on_delete=None, to='services.Service'),
        ),
        migrations.AlterField(
            model_name='creditnote',
            name='invoice',
            field=models.ForeignKey(on_delete=None, to='invoicing.SalesInvoice'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='sales_rep',
            field=models.ForeignKey(on_delete=None, to='invoicing.SalesRepresentative'),
        ),
        migrations.AlterField(
            model_name='salesconfig',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='logo/'),
        ),
        migrations.AlterField(
            model_name='salesconfig',
            name='sales_tax',
            field=models.ForeignKey(blank='True', null=True, on_delete=None, to='accounting.Tax'),
        ),
        migrations.AlterField(
            model_name='salesinvoice',
            name='ship_from',
            field=models.ForeignKey(default=1, on_delete=None, to='inventory.WareHouse'),
        ),
        migrations.AlterField(
            model_name='salesinvoiceline',
            name='product',
            field=models.ForeignKey(on_delete=None, to='inventory.Product'),
        ),
        migrations.AlterField(
            model_name='salesrepresentative',
            name='employee',
            field=models.OneToOneField(on_delete=None, to='employees.Employee'),
        ),
        migrations.AlterField(
            model_name='serviceinvoiceline',
            name='service',
            field=models.ForeignKey(on_delete=None, to='services.Service'),
        ),
    ]