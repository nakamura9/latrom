# Generated by Django 2.1.1 on 2018-11-01 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceperson',
            name='employee',
            field=models.OneToOneField(on_delete=None, to='employees.Employee'),
        ),
    ]
