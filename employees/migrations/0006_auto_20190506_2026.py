# Generated by Django 2.1.8 on 2019-05-06 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0005_employeessettings_service_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeessettings',
            name='payroll_officer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payroll_officer', to='employees.PayrollOfficer'),
        ),
    ]
