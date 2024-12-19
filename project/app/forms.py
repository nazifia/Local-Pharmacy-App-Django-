from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm
from django.forms import modelformset_factory




class EditUserProfileForm(UserChangeForm):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']


class addItemForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    brand = forms.CharField(max_length=100)
    cost = forms.DecimalField(max_digits=10, decimal_places=2)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = forms.IntegerField()
    exp_date = forms.DateField()
    unit = forms.ChoiceField(choices=Item.UNIT_CHOICES)

    class Meta:
        model = Item
        fields = ('name', 'brand', 'unit', 'markup_percentage', 'cost', 'price', 'stock_quantity', 'exp_date')
        

class dispenseForm(forms.Form):
    q = forms.CharField(min_length=2, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'SEARCH  HERE...'}))


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['user']


class AddFundsForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    


class ReturnItemForm(forms.ModelForm):
    return_item_quantity = forms.IntegerField(min_value=1, label="Return Quantity")

    class Meta:
        model = Item
        fields = ['name', 'brand', 'price', 'exp_date']  # Fields to display (readonly)






class SupplierRegistrationForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),            
        }





class ProcurementForm(forms.ModelForm):
    class Meta:
        model = Procurement
        fields = ['supplier', 'date']


class ProcurementItemForm(forms.ModelForm):
    class Meta:
        model = ProcurementItem
        fields = ['item_name', 'brand', 'unit', 'quantity', 'cost_price']

    def clean_cost_price(self):
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price is None or cost_price <= 0:
            raise forms.ValidationError("Cost price must be a positive number.")
        return cost_price



ProcurementItemFormSet = modelformset_factory(ProcurementItem, form=ProcurementItemForm, extra=10)
