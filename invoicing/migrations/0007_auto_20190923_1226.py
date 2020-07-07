# Generated by Django 2.1 on 2019-09-23 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0006_payment_entry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenselinecomponent',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=16),
        ),
        migrations.AlterField(
            model_name='productlinecomponent',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='productlinecomponent',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='productlinecomponent',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='servicelinecomponent',
            name='flat_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='servicelinecomponent',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='servicelinecomponent',
            name='hours',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
    ]