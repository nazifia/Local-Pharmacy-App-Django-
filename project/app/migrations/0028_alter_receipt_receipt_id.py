# Generated by Django 5.0 on 2024-11-07 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_activitylog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='receipt_id',
            field=models.PositiveIntegerField(editable=False, unique=True),
        ),
    ]
