# Generated by Django 2.1.8 on 2019-05-30 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common_data', '0008_auto_20190506_2026'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=16)),
            ],
        ),
    ]
