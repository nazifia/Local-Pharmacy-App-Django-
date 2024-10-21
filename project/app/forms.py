from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm




class EditUserProfileForm(UserChangeForm):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']


class addItemForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = forms.IntegerField()
    exp_date = forms.DateField()
    
    class Meta:
        model = Item
        fields = ('name', 'price', 'stock_quantity', 'exp_date')
        

class dispenseForm(forms.Form):
    q = forms.CharField(min_length=2, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'SEARCH  HERE...'}))


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['user']


class AddFundsForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)