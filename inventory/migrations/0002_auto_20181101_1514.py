# Generated by Django 2.1.1 on 2018-11-01 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorycontroller',
            name='employee',
            field=models.OneToOneField(limit_choices_to=models.Q(user__isnull=False), on_delete=None, to='employees.Employee'),
        ),
    ]
