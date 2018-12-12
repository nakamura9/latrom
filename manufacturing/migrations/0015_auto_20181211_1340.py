# Generated by Django 2.1.1 on 2018-12-11 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0014_auto_20181209_1015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processequipment',
            name='machine',
        ),
        migrations.RemoveField(
            model_name='processequipment',
            name='machine_group',
        ),
        migrations.AlterField(
            model_name='process',
            name='process_equipment',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='manufacturing.ProcessMachineGroup'),
        ),
        migrations.DeleteModel(
            name='ProcessEquipment',
        ),
    ]