# Generated by Django 2.1.8 on 2019-05-24 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0003_auto_20190524_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bubble',
            name='created_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
