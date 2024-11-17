from django.contrib import admin
from .models import *

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'unit', 'price', 'stock_quantity', 'exp_date', 'markup_percentage')
    search_fields = ('name',)
    list_filter = ('markup_percentage', 'exp_date')
    list_editable = ('price', 'stock_quantity')

class WholesaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'cost', 'price', 'stock_quantity', 'exp_date', 'markup_percentage')
    search_fields = ('name',)
    list_filter = ('markup_percentage', 'unit', 'exp_date')
    list_editable = ('price', 'stock_quantity')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'discount_amount')
    search_fields = ('item__name',)
    list_filter = ('item',)

class WholesaleCartItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'unit', 'quantity', 'discount_amount')
    search_fields = ('item__name',)
    list_filter = ('item', 'unit')

class DispensingLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'unit', 'quantity', 'amount', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'user')
    search_fields = ('name', 'phone')
    list_filter = ('user',)

class WholesaleCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'user')
    search_fields = ('name', 'phone')
    list_filter = ('user',)

class WalletAdmin(admin.ModelAdmin):
    list_display = ('customer', 'balance')
    search_fields = ('customer__name',)

class WholesaleCustomerWalletAdmin(admin.ModelAdmin):
    list_display = ('customer', 'balance')
    search_fields = ('customer__name',)

class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'wholesale_customer', 'transaction_type', 'amount', 'date', 'description')
    list_filter = ('transaction_type', 'date')
    search_fields = ('customer__name', 'wholesale_customer__name', 'transaction_type')

class SalesAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer', 'total_amount', 'date')
    list_filter = ('user', 'date')
    search_fields = ('customer__name',)

class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('customer', 'wholesale_customer', 'sales', 'total_amount', 'date', 'receipt_id', 'printed')
    list_filter = ('printed', 'date')
    search_fields = ('customer__name', 'wholesale_customer__name', 'receipt_id')

class SalesItemAdmin(admin.ModelAdmin):
    list_display = ('sales', 'item', 'price', 'quantity', 'subtotal')
    search_fields = ('sales__customer__name', 'item__name')
    list_filter = ('sales',)

class WholesaleSalesItemAdmin(admin.ModelAdmin):
    list_display = ('sales', 'item', 'unit', 'price', 'quantity', 'subtotal')
    search_fields = ('sales__customer__name', 'item__name')
    list_filter = ('sales',)

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'action')

# Register models with custom admin configurations
admin.site.register(Item, ItemAdmin)
admin.site.register(Wholesale, WholesaleAdmin)
# admin.site.register(CartItem, CartItemAdmin)
# admin.site.register(WholesaleCartItem, WholesaleCartItemAdmin)
admin.site.register(DispensingLog, DispensingLogAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(WholesaleCustomer, WholesaleCustomerAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(WholesaleCustomerWallet, WholesaleCustomerWalletAdmin)
admin.site.register(TransactionHistory, TransactionHistoryAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(SalesItem, SalesItemAdmin)
admin.site.register(WholesaleSalesItem, WholesaleSalesItemAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
