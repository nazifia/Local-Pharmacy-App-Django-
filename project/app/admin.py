from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Wallet)
admin.site.register(DispensingLog)
admin.site.register(TransactionHistory)
admin.site.register(Receipt)