from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.IntegerField()
    address = models.CharField(max_length=200)
    
    def __str__(self):
        return f'{self.user.username} {self.name} {self.phone} {self.address}'
    
    

class Wallet(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.customer.name}'s wallet - balance{self.balance}"
    
    def add_funds(self, amount):
        self.balance += amount
        self.save()
    
    def reset_wallet(self):
        self.balance = 0
        self.save()



class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user} {self.name} {self.quantity} {self.amount}'


@receiver(post_save, sender=Customer)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(customer=instance)

