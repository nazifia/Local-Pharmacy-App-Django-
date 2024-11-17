# Generated by Django 5.1.1 on 2024-11-16 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0055_salesitem_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispensinglog',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ample'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
    ]