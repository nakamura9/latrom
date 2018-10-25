# Generated by Django 2.1.1 on 2018-10-08 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_auto_20180917_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceworkorder',
            name='authorized_by',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(user_isnull=False), null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee'),
        ),
    ]