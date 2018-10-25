# Generated by Django 2.1.1 on 2018-10-08 10:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=255)),
                ('body', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('sent', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now=True)),
                ('opened_timestamp', models.DateTimeField()),
                ('blind_carbon_copy', models.ManyToManyField(related_name='blind_carbon_copy', to=settings.AUTH_USER_MODEL)),
                ('carbon_copy', models.ManyToManyField(related_name='carbon_copy', to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(on_delete=None, related_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=None, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('closed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(null=True, on_delete=None, to='messaging.MessageThread'),
        ),
    ]