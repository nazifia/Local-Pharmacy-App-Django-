# Generated by Django 5.1.1 on 2024-12-18 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0104_cartitem_brand_wholesalecartitem_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='procurementitem',
            name='brand',
            field=models.CharField(blank=True, default='None', max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='salesitem',
            name='brand',
            field=models.CharField(blank=True, default='None', max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='wholesalesalesitem',
            name='brand',
            field=models.CharField(blank=True, default='None', max_length=225, null=True),
        ),
    ]