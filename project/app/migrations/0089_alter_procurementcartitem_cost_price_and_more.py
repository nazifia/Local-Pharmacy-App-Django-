# Generated by Django 5.1.1 on 2024-12-15 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0088_alter_procurementcartitem_item_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procurementcartitem',
            name='cost_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='procurementcartitem',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=12),
        ),
    ]
