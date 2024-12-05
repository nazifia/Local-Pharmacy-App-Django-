
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal

# Create your models here.
from django.db import models

class Item(models.Model):
    MARKUP_CHOICES = [
        (0, 'No markup'),
        (2.5, '2.5% markup'),
        (5, '5% markup'),
        (7.5, '7.5% markup'),
        (10, '10% markup'),
        (12.5, '12.5% markup'),
        (15, '15% markup'),
        (17.5, '17.5% markup'),
        (20, '20% markup'),
        (22.5, '22.5% markup'),
        (25, '25% markup'),
        (27.5, '27.5% markup'),
        (30, '30% markup'),
        (32.5, '32.5% markup'),
        (35, '35% markup'),
        (37.5, '37.5% markup'),
        (40, '40% markup'),
        (42.5, '42.5% markup'),
        (45, '45% markup'),
        (47.5, '47.5% markup'),
        (50, '50% markup'),
        (57.5, '57.5% markup'),
        (60, '60% markup'),
        (62.5, '62.5% markup'),
        (65, '65% markup'),
        (67.5, '67.5% markup'),
        (70, '70% markup'),
        (72., '72.% markup'),
        (75, '75% markup'),
        (77.5, '77.5% markup'),
        (80, '80% markup'),
        (82.5, '82.% markup'),
        (85, '85% markup'),
        (87.5, '87.5% markup'),
        (90, '90% markup'),
        (92., '92.% markup'),
        (95, '95% markup'),
        (97.5, '97.5% markup'),
        (100, '100% markup'),
    ]
    
    UNIT_CHOICES = [
        ('unit', 'Select Unit'),
        ('PCS', 'Pieces'),
        ('TAB', 'Tablets'),
        ('CAP', 'Capsules'),
        ('TIN', 'Tins'),
        ('BTL', 'Bottles'),
        ('PCK', 'Packets'),
        ('ROLL', 'Rolls'),
        ('CTN', 'Cartons'),
        ('AMP', 'Ampules'),
        ('VAIL', 'Vail'),
        # Add other units as needed
    ]

    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='unit')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    exp_date = models.DateField()
    markup_percentage = models.IntegerField(choices=MARKUP_CHOICES, default=0)

    def __str__(self):
        return f'{self.name} {self.markup_percentage} {self.price} {self.stock_quantity} {self.exp_date}'

    def save(self, *args, **kwargs):
        # Check if the price was provided; if not, calculate based on the markup
        if not self.price or self.price == self.cost + (self.cost * self.markup_percentage / 100):
            self.price = self.cost + (self.cost * self.markup_percentage / 100)
        super().save(*args, **kwargs)




class Wholesale(models.Model):
    MARKUP_CHOICES = [
        (0, 'No markup'),
        (2.5, '2.5% markup'),
        (5, '5% markup'),
        (7.5, '7.5% markup'),
        (10, '10% markup'),
        (12.5, '12.5% markup'),
        (15, '15% markup'),
        (17.5, '17.5% markup'),
        (20, '20% markup'),
        (22.5, '22.5% markup'),
        (25, '25% markup'),
        (27.5, '27.5% markup'),
        (30, '30% markup'),
        (32.5, '32.5% markup'),
        (35, '35% markup'),
        (37.5, '37.5% markup'),
        (40, '40% markup'),
        (42.5, '42.5% markup'),
        (45, '45% markup'),
        (47.5, '47.5% markup'),
        (50, '50% markup'),
        (57.5, '57.5% markup'),
        (60, '60% markup'),
        (62.5, '62.5% markup'),
        (65, '65% markup'),
        (67.5, '67.5% markup'),
        (70, '70% markup'),
        (72., '72.% markup'),
        (75, '75% markup'),
        (77.5, '77.5% markup'),
        (80, '80% markup'),
        (82.5, '82.% markup'),
        (85, '85% markup'),
        (87.5, '87.5% markup'),
        (90, '90% markup'),
        (92., '92.% markup'),
        (95, '95% markup'),
        (97.5, '97.5% markup'),
        (100, '100% markup'),
    ]

    UNIT_CHOICES = [
        ('unit', 'Select Unit'),
        ('PCS', 'Pieces'),
        ('TAB', 'Tablets'),
        ('TIN', 'Tins'),
        ('BTL', 'Bottles'),
        ('PCK', 'Packets'),
        ('ROLL', 'Rolls'),
        ('CTN', 'Cartons'),
        ('AMP', 'Ampules'),
        ('VAIL', 'Vail'),
        # Add other units as needed
    ]

    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='unit')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    exp_date = models.DateField()
    markup_percentage = models.IntegerField(choices=MARKUP_CHOICES, default=0)

    def __str__(self):
        return f'{self.name} {self.unit} {self.markup_percentage} {self.price} {self.stock_quantity} {self.exp_date}'

    def save(self, *args, **kwargs):
        # Automatically calculate the price based on the markup percentage
        self.price = self.cost + (self.cost * self.markup_percentage / 100)
        super().save(*args, **kwargs)



class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    unit = models.CharField(max_length=10, choices=Wholesale.UNIT_CHOICES, default='unit')
    quantity = models.IntegerField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class WholesaleCartItem(models.Model):
    item = models.ForeignKey(Wholesale, on_delete=models.CASCADE)
    unit = models.CharField(max_length=10, choices=Wholesale.UNIT_CHOICES, default='unit')
    quantity = models.IntegerField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class DispensingLog(models.Model):
    UNIT_CHOICES = [
        ('PCS', 'Pieces'),
        ('TAB', 'Tablets'),
        ('TIN', 'Tins'),
        ('BTL', 'Bottles'),
        ('PCK', 'Packets'),
        ('ROLL', 'Rolls'),
        ('CTN', 'Cartons'),
        ('AMP', 'Ample'),
        ('VAIL', 'Vail'),
        ('UNDEFINED', 'Undefined'),
    ]

    STATUS_CHOICES = [
        ('Returned', 'Returned'),
        ('Partially Returned', 'Partially Returned'),
        ('Dispensed', 'Dispensed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='UNDEFINED')
    quantity = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Dispensed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.name} ({self.quantity} {self.unit} {self.status})'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f'{self.user.username if self.user else "No User"} {self.name} {self.phone} {self.address}'



class WholesaleCustomer(models.Model):
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



class WholesaleCustomerWallet(models.Model):
    customer = models.OneToOneField(WholesaleCustomer, on_delete=models.CASCADE, related_name='wholesale_customer_wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.customer.name}'s wallet - balance {self.balance}"
    
    def add_funds(self, amount):
        self.balance += amount
        self.save()
        # Save transaction history
        TransactionHistory.objects.create(
            wholesale_customer=self.customer,
            transaction_type='deposit',
            amount=amount,
            description='Funds added to wallet'
        )
    
    def reset_wallet(self):
        self.balance = 0
        self.save()


# Signal to create WholesaleCustomerWallet on creation of WholesaleCustomer
@receiver(post_save, sender=WholesaleCustomer)
def create_wholesale_wallet(sender, instance, created, **kwargs):
    if created:
        WholesaleCustomerWallet.objects.create(customer=instance)


class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('debit', 'Debit'),
        ('deposit', 'Deposit'),
        ('refund', 'Refund'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    wholesale_customer = models.ForeignKey(WholesaleCustomer, on_delete=models.CASCADE, related_name='wholesale_transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)  # Optional field to describe the transaction

    def __str__(self):
        name = self.customer.name if self.customer else self.wholesale_customer.name
        return f"{name} - {self.transaction_type} - {self.amount} on {self.date}"





# Ensure Sales is defined before Receipt
class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    wholesale_customer = models.ForeignKey(WholesaleCustomer, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.customer.name if self.customer else "WALK-IN CUSTOMER"} - {self.total_amount}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.customer:
            TransactionHistory.objects.create(
            customer=self.customer,
            transaction_type='purchase',
            amount=self.total_amount,
            description='Items purchased'
        )
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
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='receipts', null=True, blank=True)
    buyer_name = models.CharField(max_length=255, blank=True, null=True)
    buyer_address = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    date = models.DateTimeField(auto_now_add=True)
    receipt_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    printed = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=[
        ('Cash', 'Cash'),
        ('Wallet', 'Wallet'),
        ('Transfer', 'Transfer'),
    ], default='Cash')

    def __str__(self):
        name = self.customer.name if self.customer else "WALK-IN CUSTOMER"
        return f"Receipt {self.receipt_id} - {name} - {self.total_amount} on {self.date}"







class WholesaleReceipt(models.Model):
    wholesale_customer = models.ForeignKey(WholesaleCustomer, on_delete=models.CASCADE, null=True, blank=True)
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='wholesale_receipts', null=True, blank=True)
    buyer_name = models.CharField(max_length=255, blank=True, null=True)
    buyer_address = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    date = models.DateTimeField(auto_now_add=True)
    receipt_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    printed = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=[
        ('Cash', 'Cash'),
        ('Wallet', 'Wallet'),
        ('Transfer', 'Transfer'),
    ], default='Cash')

    def __str__(self):
        name = self.wholesale_customer.name if self.wholesale_customer else "WALK-IN CUSTOMER"
        return f"WholesaleReceipt {self.receipt_id} - {name} - {self.total_amount} on {self.date}"



        
        

class SalesItem(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='sales_items')
    unit = models.CharField(max_length=10, choices=Wholesale.UNIT_CHOICES, default='unit')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.item.name} - {self.quantity} at {self.price}'
    
    @property
    def subtotal(self):
        return self.price * self.quantity



class WholesaleSalesItem(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='wholesale_sales_items')
    item = models.ForeignKey(Wholesale, on_delete=models.CASCADE)
    unit = models.CharField(max_length=10, choices=Wholesale.UNIT_CHOICES, default='unit')
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



class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"