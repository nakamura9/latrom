# Generated by Django 2.1 on 2019-09-13 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0019_auto_20190912_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='title',
        ),
    ]