# Generated by Django 5.1.1 on 2024-12-15 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0089_alter_procurementcartitem_cost_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='procurementcartitem',
            name='item_name',
        ),
        migrations.RemoveField(
            model_name='procurement',
            name='received_by',
        ),
        migrations.RemoveField(
            model_name='procurement',
            name='supplier',
        ),
        migrations.RemoveField(
            model_name='procurementcartitem',
            name='procurement',
        ),
        migrations.RemoveField(
            model_name='procurementreceipt',
            name='supplier',
        ),
        migrations.DeleteModel(
            name='ProcuredItem',
        ),
        migrations.DeleteModel(
            name='Procurement',
        ),
        migrations.DeleteModel(
            name='ProcurementCartItem',
        ),
        migrations.DeleteModel(
            name='ProcurementReceipt',
        ),
        migrations.DeleteModel(
            name='Supplier',
        ),
    ]
