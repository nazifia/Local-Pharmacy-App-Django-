# Generated by Django 5.1.1 on 2024-11-12 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0050_alter_item_markup_percentage_alter_item_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='markup_percentage',
            field=models.IntegerField(choices=[(0, 'No markup'), (5, '5% markup'), (10, '10% markup'), (15, '15% markup'), (20, '20% markup'), (25, '25% markup'), (30, '30% markup'), (35, '35% markup'), (40, '40% markup'), (45, '45% markup'), (50, '50% markup'), (55, '55% markup'), (60, '60% markup'), (65, '65% markup'), (70, '70% markup'), (75, '75% markup'), (80, '80% markup'), (85, '85% markup'), (90, '90% markup'), (95, '95% markup'), (100, '100% markup')], default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
