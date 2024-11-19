# Generated by Django 5.1.1 on 2024-11-19 09:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_receipt_unique_sales_receipt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='sales',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sales_items', to='app.sales'),
        ),
        migrations.AlterField(
            model_name='salesitem',
            name='sales',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='app.sales'),
        ),
    ]
