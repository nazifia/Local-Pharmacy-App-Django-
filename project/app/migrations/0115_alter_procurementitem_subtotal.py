# Generated by Django 5.1.1 on 2024-12-21 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0114_remove_itemselectionhistory_subtotal_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procurementitem',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10),
        ),
    ]