# Generated by Django 5.1.1 on 2024-12-14 20:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0084_alter_procureditem_supplier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='procurementcartitem',
            name='received_by',
        ),
        migrations.AddField(
            model_name='procurementcartitem',
            name='procurement',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='app.procurement'),
        ),
        migrations.AlterField(
            model_name='procurementcartitem',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='procurementcartitem',
            name='unit',
            field=models.CharField(choices=[('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Cards'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vial')], default='PCS', max_length=10),
        ),
    ]