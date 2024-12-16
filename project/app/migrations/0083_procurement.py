# Generated by Django 5.1.1 on 2024-12-14 18:44

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0082_procurementcartitem_received_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Procurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('unit', models.CharField(choices=[('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Cards'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vial')], default='PCS', max_length=10)),
                ('quantity', models.PositiveIntegerField()),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, editable=False, max_digits=12)),
                ('procurement_date', models.DateTimeField(default=datetime.datetime.now)),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='procurement_items', to='app.supplier')),
            ],
        ),
    ]