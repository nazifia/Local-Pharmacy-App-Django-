# Generated by Django 5.0 on 2024-10-24 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_customer_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]