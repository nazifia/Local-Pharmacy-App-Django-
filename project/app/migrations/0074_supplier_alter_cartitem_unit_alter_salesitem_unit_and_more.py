# Generated by Django 5.1.1 on 2024-12-11 14:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0073_alter_dispensinglog_unit_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Card'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='salesitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Card'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='wholesale',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Card'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='wholesalecartitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Card'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.AlterField(
            model_name='wholesalesalesitem',
            name='unit',
            field=models.CharField(choices=[('unit', 'Select Unit'), ('PCS', 'Pieces'), ('TAB', 'Tablets'), ('CARD', 'Card'), ('TIN', 'Tins'), ('BTL', 'Bottles'), ('PCK', 'Packets'), ('ROLL', 'Rolls'), ('CTN', 'Cartons'), ('AMP', 'Ampules'), ('VAIL', 'Vail')], default='unit', max_length=10),
        ),
        migrations.CreateModel(
            name='ProcuredItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, editable=False, max_digits=12)),
                ('procurement_date', models.DateField(auto_now_add=True)),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='procured_items', to='app.supplier')),
            ],
        ),
    ]
