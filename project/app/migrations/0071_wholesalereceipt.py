# Generated by Django 5.0 on 2024-12-01 13:12

import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0070_alter_item_markup_percentage_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WholesaleReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('buyer_address', models.CharField(blank=True, max_length=255, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('receipt_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('printed', models.BooleanField(default=False)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('Wallet', 'Wallet'), ('Transfer', 'Transfer')], default='Cash', max_length=20)),
                ('sales', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wholesale_receipts', to='app.sales')),
                ('wholesale_customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.wholesalecustomer')),
            ],
        ),
    ]