# Generated by Django 5.1.1 on 2024-12-15 07:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0086_procurementcartitem_cost_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procurementcartitem',
            name='item_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='procurementcartitem',
            name='procurement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='app.procurement'),
        ),
    ]
