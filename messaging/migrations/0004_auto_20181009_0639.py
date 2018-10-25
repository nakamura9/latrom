# Generated by Django 2.1.1 on 2018-10-09 04:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0003_auto_20181009_0615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='blind_carbon_copy',
            field=models.ManyToManyField(blank=True, related_name='BCC', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='carbon_copy',
            field=models.ManyToManyField(blank=True, related_name='CC', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(on_delete=None, related_name='to', to=settings.AUTH_USER_MODEL),
        ),
    ]