# Generated by Django 2.2 on 2019-04-26 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0003_invoice_is_configured'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='is_configured',
        ),
        migrations.AddField(
            model_name='salesconfig',
            name='is_configured',
            field=models.BooleanField(default=False),
        ),
    ]
