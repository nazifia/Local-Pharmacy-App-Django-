# Generated by Django 5.1.1 on 2024-12-18 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0103_dispensinglog_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='brand',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='wholesalecartitem',
            name='brand',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]