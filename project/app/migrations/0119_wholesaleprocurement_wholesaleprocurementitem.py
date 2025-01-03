# Generated by Django 5.1.1 on 2024-12-25 14:14

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0118_receipt_status_wholesalereceipt_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WholesaleProcurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='WholesaleProcurementItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('brand', models.CharField(blank=True, default='None', max_length=225, null=True)),
                ('unit', models.CharField(choices=[('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Cards'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vial')], max_length=100)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('procurement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app.wholesaleprocurement')),
            ],
        ),
    ]
