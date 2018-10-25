# Generated by Django 2.1.1 on 2018-10-08 08:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0004_journalentry_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=None, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='expense',
            name='recorded_by',
            field=models.ForeignKey(default=1, on_delete=None, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recurringexpense',
            name='recorded_by',
            field=models.ForeignKey(default=1, on_delete=None, to=settings.AUTH_USER_MODEL),
        ),
    ]
