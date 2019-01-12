# Generated by Django 2.1.4 on 2019-01-08 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_auto_20190104_2114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagethread',
            old_name='_from',
            new_name='initiator',
        ),
        migrations.RemoveField(
            model_name='messagethread',
            name='_to',
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='messaging.MessageThread'),
        ),
    ]