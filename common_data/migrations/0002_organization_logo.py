# Generated by Django 2.1.1 on 2018-11-22 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
