# Generated by Django 5.1.1 on 2024-12-16 17:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0100_rename_receipt_procurementitem_procurement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='dispensinglog',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='sales',
            name='date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
