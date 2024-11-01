# Generated by Django 5.1.1 on 2024-10-30 15:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_receipt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipt',
            name='printed',
        ),
        migrations.AddField(
            model_name='receipt',
            name='receipt_short_id',
            field=models.CharField(editable=False, max_length=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.customer'),
        ),
    ]