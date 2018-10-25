# Generated by Django 2.1.1 on 2018-10-24 14:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_host', models.CharField(blank=True, default='', max_length=32)),
                ('email_port', models.IntegerField(null=True)),
                ('email_user', models.CharField(blank=True, default='', max_length=32)),
                ('email_password', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('address', models.TextField(blank=True, default='', max_length=128)),
                ('email', models.CharField(blank=True, default='', max_length=32)),
                ('phone', models.CharField(blank=True, default='', max_length=16)),
                ('phone_two', models.CharField(blank=True, default='', max_length=16)),
                ('other_details', models.TextField(blank=True, default='')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('note', models.TextField()),
                ('author', models.ForeignKey(on_delete=None, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legal_name', models.CharField(max_length=255)),
                ('business_address', models.TextField(blank=True)),
                ('website', models.CharField(blank=True, max_length=255)),
                ('tax_clearance', models.CharField(blank=True, max_length=64)),
                ('email', models.CharField(blank=True, max_length=128)),
                ('phone', models.CharField(blank=True, max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='individual',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common_data.Organization'),
        ),
    ]
