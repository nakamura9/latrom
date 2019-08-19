# Generated by Django 2.2.4 on 2019-08-18 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_merge_20190818_0439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispatchrequest',
            name='debit_note',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.DebitNote'),
        ),
        migrations.AlterField(
            model_name='dispatchrequest',
            name='invoice',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='invoicing.Invoice'),
        ),
        migrations.AlterField(
            model_name='dispatchrequest',
            name='transfer_order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.TransferOrder'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='C:\\Users\\nakamura9a\\Documents\\code\\git\\latrom\\media'),
        ),
    ]
