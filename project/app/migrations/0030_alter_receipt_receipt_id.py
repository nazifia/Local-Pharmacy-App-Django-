# Generated by Django 5.0 on 2024-11-07 10:01

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_alter_receipt_receipt_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='receipt_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
