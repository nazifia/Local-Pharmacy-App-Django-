# Generated by Django 5.1.1 on 2024-12-21 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0113_itemselectionhistory_subtotal_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemselectionhistory',
            name='subtotal',
        ),
        migrations.RemoveField(
            model_name='wholesaleselectionhistory',
            name='subtotal',
        ),
    ]
