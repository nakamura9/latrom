# Generated by Django 2.1.4 on 2019-01-27 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0018_auto_20190126_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountingsettings',
            name='default_accounting_period',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Annually'), (1, 'Monthly'), (2, 'Weekly')], default=1),
        ),
        migrations.AlterField(
            model_name='account',
            name='balance_sheet_category',
            field=models.CharField(choices=[('current-assets', 'Current Assets'), ('non-current-assets', 'Long Term Assets'), ('current-liabilites', 'Current Liabilites'), ('long-term-liabilites', 'Long Term Liabilites'), ('expense', 'Expense'), ('current-assets', 'Current Assets'), ('not-included', 'Not Included')], default='current-assets', max_length=16),
        ),
        migrations.AlterField(
            model_name='interestbearingaccount',
            name='balance_sheet_category',
            field=models.CharField(choices=[('current-assets', 'Current Assets'), ('non-current-assets', 'Long Term Assets'), ('current-liabilites', 'Current Liabilites'), ('long-term-liabilites', 'Long Term Liabilites'), ('expense', 'Expense'), ('current-assets', 'Current Assets'), ('not-included', 'Not Included')], default='current-assets', max_length=16),
        ),
    ]
