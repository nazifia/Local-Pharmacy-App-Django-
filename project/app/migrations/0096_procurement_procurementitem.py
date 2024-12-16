# Generated by Django 5.1.1 on 2024-12-15 15:54

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0095_remove_procurement_received_by_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Procurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='ProcurementItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('unit', models.CharField(choices=[('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Cards'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vial')], max_length=100)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app.receipt')),
            ],
        ),
    ]