# Generated by Django 5.1.1 on 2024-10-28 07:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_remove_sales_receipt_remove_dispensinglog_receipt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.customer'),
        ),
    ]
