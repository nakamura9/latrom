# Generated by Django 2.1.1 on 2018-12-06 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0006_auto_20181206_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processproduct',
            name='product_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='manufacturing.ProductList'),
        ),
    ]
