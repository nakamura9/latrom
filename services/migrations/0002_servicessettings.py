# Generated by Django 2.2 on 2019-04-27 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicesSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_configured', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
