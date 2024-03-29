# Generated by Django 2.1.4 on 2019-04-02 04:09

import datetime
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('invoicing', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employees', '0001_initial'),
        ('accounting', '0001_initial'),
        ('inventory', '0001_initial'),
        ('common_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumablesRequisition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('department', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('authorized_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consumable_authorized_by', to='employees.Employee')),
                ('released_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consumable_released_by', to='employees.Employee')),
                ('requested_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consumable_requested_by', to='employees.Employee')),
                ('warehouse', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConsumablesRequisitionLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('returned', models.FloatField(default=0.0)),
                ('consumable', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.InventoryItem')),
                ('requisition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.ConsumablesRequisition')),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.UnitOfMeasure')),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentRequisition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('department', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('returned_date', models.DateField(null=True)),
                ('authorized_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authorized_by', to='employees.Employee')),
                ('received_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_by', to='employees.Employee')),
                ('released_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='released_by', to='employees.Employee')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_by', to='employees.Employee')),
                ('warehouse', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.WareHouse')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EquipmentRequisitionLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('quantity_returned', models.FloatField(default=0)),
                ('requesting_condition', models.CharField(choices=[('excellent', 'Excellent'), ('good', 'Good'), ('poor', 'Poor'), ('broken', 'Not Functioning')], max_length=16)),
                ('returned_condition', models.CharField(choices=[('excellent', 'Excellent'), ('good', 'Good'), ('poor', 'Poor'), ('broken', 'Not Functioning')], max_length=16, null=True)),
                ('equipment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.InventoryItem')),
                ('requisition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.EquipmentRequisition')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('flat_fee', models.DecimalField(decimal_places=2, max_digits=6)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=6)),
                ('frequency', models.CharField(choices=[('once', 'Once off'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('fortnightly', 'Every 2 weeks'), ('monthly', 'Monthly'), ('quarterly', 'Every 3 Months'), ('bi-annually', 'Every 6 Months'), ('yearly', 'Yearly')], max_length=16)),
                ('is_listed', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServicePerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_manager', models.BooleanField(default=False)),
                ('can_authorize_equipment_requisitions', models.BooleanField(default=False)),
                ('can_authorize_consumables_requisitions', models.BooleanField(default=False)),
                ('employee', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceProcedure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('as_checklist', models.BooleanField(blank=True, default=False)),
                ('name', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('required_consumables', models.ManyToManyField(blank=True, related_name='consumables', to='inventory.InventoryItem')),
                ('required_equipment', models.ManyToManyField(blank=True, related_name='equipment', to='inventory.InventoryItem')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_team_manager', to='services.ServicePerson')),
                ('members', models.ManyToManyField(related_name='service_team_members', to='services.ServicePerson')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceWorkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField(choices=[(datetime.time(6, 0), '06:00'), (datetime.time(6, 30), '06:30'), (datetime.time(7, 0), '07:00'), (datetime.time(7, 30), '07:30'), (datetime.time(8, 0), '08:00'), (datetime.time(8, 30), '08:30'), (datetime.time(9, 0), '09:00'), (datetime.time(9, 30), '09:30'), (datetime.time(10, 0), '10:00'), (datetime.time(10, 30), '10:30'), (datetime.time(11, 0), '11:00'), (datetime.time(11, 30), '11:30'), (datetime.time(12, 0), '12:00'), (datetime.time(12, 30), '12:30'), (datetime.time(13, 0), '13:00'), (datetime.time(13, 30), '13:30'), (datetime.time(14, 0), '14:00'), (datetime.time(14, 30), '14:30'), (datetime.time(15, 0), '15:00'), (datetime.time(15, 30), '15:30'), (datetime.time(16, 0), '16:00'), (datetime.time(16, 30), '16:30'), (datetime.time(17, 0), '17:00'), (datetime.time(17, 30), '17:30'), (datetime.time(18, 0), '18:00')])),
                ('internal', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, default='')),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('expected_duration', models.DurationField(blank=True, choices=[(datetime.timedelta(0), '00:00'), (datetime.timedelta(0, 1800), '00:30'), (datetime.timedelta(0, 3600), '01:00'), (datetime.timedelta(0, 5400), '01:30'), (datetime.timedelta(0, 7200), '02:00'), (datetime.timedelta(0, 9000), '02:30'), (datetime.timedelta(0, 10800), '03:00'), (datetime.timedelta(0, 12600), '03:30'), (datetime.timedelta(0, 14400), '04:00'), (datetime.timedelta(0, 16200), '04:30'), (datetime.timedelta(0, 18000), '05:00'), (datetime.timedelta(0, 19800), '05:30'), (datetime.timedelta(0, 21600), '06:00'), (datetime.timedelta(0, 23400), '06:30'), (datetime.timedelta(0, 25200), '07:00'), (datetime.timedelta(0, 27000), '07:30')], null=True)),
                ('status', models.CharField(blank=True, choices=[('requested', 'Requested'), ('progress', 'In progress'), ('completed', 'Completed'), ('authorized', 'Authorized'), ('declined', 'Declined')], max_length=16)),
                ('progress', models.CharField(blank=True, default='', max_length=512)),
                ('authorized_by', models.ForeignKey(blank=True, limit_choices_to=models.Q(user__isnull=False), null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.Employee')),
                ('notes', models.ManyToManyField(to='common_data.Note')),
                ('service_people', models.ManyToManyField(blank=True, to='services.ServicePerson')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.ServiceTeam')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('procedure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.ServiceProcedure')),
            ],
        ),
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('normal_time', models.DurationField()),
                ('overtime', models.DurationField()),
                ('normal_time_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=8)),
                ('overtime_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=8)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.Employee')),
                ('work_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.ServiceWorkOrder')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderExpense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounting.Expense')),
                ('work_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.ServiceWorkOrder')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('request', 'Requested'), ('in-progress', 'In Progress'), ('completed', 'Completed')], max_length=16)),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.Invoice')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.Service')),
            ],
        ),
        migrations.AddField(
            model_name='serviceworkorder',
            name='works_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.WorkOrderRequest'),
        ),
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.ServiceCategory'),
        ),
        migrations.AddField(
            model_name='service',
            name='procedure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.ServiceProcedure'),
        ),
        migrations.AddField(
            model_name='equipmentrequisition',
            name='work_order',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('status', 'progress'), ('status', 'requested'), _connector='OR')), null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.ServiceWorkOrder'),
        ),
        migrations.AddField(
            model_name='consumablesrequisition',
            name='work_order',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('status', 'progress'), ('status', 'requested'), _connector='OR')), null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.ServiceWorkOrder'),
        ),
    ]
