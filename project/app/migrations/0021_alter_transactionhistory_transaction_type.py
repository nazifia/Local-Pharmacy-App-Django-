# Generated by Django 5.1.1 on 2024-10-28 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_alter_transactionhistory_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionhistory',
            name='transaction_type',
            field=models.CharField(choices=[('purchase', 'Purchase'), ('Debit', 'Debit'), ('deposit', 'Deposit'), ('refund', 'Refund')], max_length=20),
        ),
    ]
