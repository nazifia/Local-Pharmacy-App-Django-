# Generated by Django 5.1.1 on 2024-12-15 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0096_procurement_procurementitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='procurementitem',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]