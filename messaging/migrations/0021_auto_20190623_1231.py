# Generated by Django 2.1.8 on 2019-06-23 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0020_auto_20190617_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='created_timestamp',
            field=models.DateTimeField(),
        ),
    ]