# Generated by Django 2.1.8 on 2019-08-14 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_stockreceiptline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='C:\\Users\\Conrad\\Documents\\code\\latrom\\media'),
        ),
    ]