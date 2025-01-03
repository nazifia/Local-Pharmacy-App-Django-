# Generated by Django 5.1.1 on 2024-11-18 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0056_alter_dispensinglog_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='dispensinglog',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dispensinglog',
            name='unit',
            field=models.CharField(choices=[('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ample'), ('VAIL', 'Vail'), ('UNDEFINED', 'Undefined')], default='UNDEFINED', max_length=10),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CAP', 'Capsules'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='sales',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='app.sales'),
        ),
        migrations.AlterField(
            model_name='salesitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='wholesale',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='wholesalecartitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='wholesalesalesitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
    ]
