# Generated by Django 5.1.1 on 2024-11-22 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0065_alter_dispensinglog_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispensinglog',
            name='status',
            field=models.CharField(choices=[('Returned', 'Returned'), ('Partially Returned', 'Partially Returned'), ('Dispensed', 'Rispensed')], default='Dispensed', max_length=20),
        ),
    ]
