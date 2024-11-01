import uuid
import base64
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2,)
    stock_quantity = models.IntegerField()
    exp_date = models.DateField()    
    def __str__(self):
        return f'{self.name} {self.price} {self.stock_quantity} {self.exp_date}'
    
    

class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

class DispensingLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} {self.name} {self.quantity} {self.created_at}'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f'{self.user.username if self.user else "No User"} {self.name} {self.phone} {self.address}'
    
    

class Wallet(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.customer.name}'s wallet - balance {self.balance}"
    
    def add_funds(self, amount):
        self.balance += amount
        self.save()
        # Save transaction history
        TransactionHistory.objects.create(
            customer=self.customer,
            transaction_type='deposit',
            amount=amount,
            description='Funds added to wallet'
        )
    
    def reset_wallet(self):
        self.balance = 0
        self.save()



# Ensure Sales is defined before Receipt
class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.customer.name if self.customer else "Anonymous"} - {self.total_amount}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.customer:
            # Log the transaction
            TransactionHistory.objects.create(
                customer=self.customer,
                transaction_type='purchase',
                amount=self.total_amount,
                description='Items purchased'
            )
            # Create and save a receipt for the customer
            Receipt.objects.create(
                customer=self.customer,
                sales=self,
                total_amount=self.total_amount
            )

    def calculate_total_amount(self):
        self.total_amount = sum(item.price * item.quantity for item in self.sales_items.all())
        self.save()

class Receipt(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='receipts')
    buyer_name = models.CharField(max_length=255, blank=True, null=True)  # Add buyer_name field
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    receipt_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    printed = models.BooleanField(default=False)

    def __str__(self):
        name = self.customer.name if self.customer else self.buyer_name or "Anonymous"
        return f"Receipt {self.receipt_id} - {name} - {self.total_amount} on {self.date}"

    def mark_as_printed(self):
        """Mark receipt as printed after it's printed."""
        self.printed = True
        self.save()
        
        

class SalesItem(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='sales_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.item.name} - {self.quantity} at {self.price}'
    
    @property
    def subtotal(self):
        return self.price * self.quantity




@receiver(post_save, sender=Customer)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(customer=instance)


class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('Debit', 'Debit'),
        ('deposit', 'Deposit'),
        ('refund', 'Refund'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)  # Optional field to describe the transaction

    def __str__(self):
        return f"{self.customer.name} - {self.transaction_type} - {self.amount} on {self.date}"



class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"