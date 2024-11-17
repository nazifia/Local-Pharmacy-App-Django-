# Generated by Django 5.1.1 on 2024-11-10 08:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_alter_wholesalecustomerwallet_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionhistory',
            name='wholesale_customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wholesale_transactions', to='app.wholesalecustomer'),
        ),
        migrations.AlterField(
            model_name='transactionhistory',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='app.customer'),
        ),
        migrations.AlterField(
            model_name='transactionhistory',
            name='transaction_type',
            field=models.CharField(choices=[('purchase', 'Purchase'), ('debit', 'Debit'), ('deposit', 'Deposit'), ('refund', 'Refund')], max_length=20),
        ),
    ]
