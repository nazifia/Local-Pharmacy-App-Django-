# Generated by Django 5.1.1 on 2024-12-15 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0099_remove_procurement_receipt_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='procurementitem',
            old_name='receipt',
            new_name='procurement',
        ),
    ]