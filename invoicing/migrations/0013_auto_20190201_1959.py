# Generated by Django 2.1.4 on 2019-02-01 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0012_salesinvoice_shipping_expenses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesconfig',
            name='business_address',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='business_name',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='business_registration_number',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='contact_details',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='document_theme',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='logo',
        ),
        migrations.RemoveField(
            model_name='salesconfig',
            name='payment_details',
        ),
    ]