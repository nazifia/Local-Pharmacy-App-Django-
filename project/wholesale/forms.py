from django import forms
from app.models import *
from django.forms import modelformset_factory



class addWholesaleForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    brand = forms.CharField(max_length=100)
    cost = forms.DecimalField(max_digits=10, decimal_places=2)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = forms.IntegerField()
    exp_date = forms.DateField()
    markup_percentage = models.IntegerField()
    unit = forms.ChoiceField(choices=Item.UNIT_CHOICES)
    
    class Meta:
        model = Wholesale
        fields = ('name', 'brand', 'unit', 'cost', 'markup_percentage', 'price', 'stock_quantity', 'exp_date')
        


class wholesaleDispenseForm(forms.Form):
    q = forms.CharField(min_length=2, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'SEARCH  HERE...'}))



class ReturnWholesaleItemForm(forms.ModelForm):
    return_item_quantity = forms.IntegerField(min_value=1, label="Return Quantity")

    class Meta:
        model = Wholesale
        fields = ['name', 'price', 'exp_date']  # Fields to display (readonly)


class WholesaleCustomerForm(forms.ModelForm):
    class Meta:
        model = WholesaleCustomer
        exclude = ['user']


class WholesaleCustomerAddFundsForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)




class WholesaleProcurementForm(forms.ModelForm):
    class Meta:
        model = WholesaleProcurement
        fields = ['supplier', 'date']
        widgets = {
            'supplier': forms.Select(attrs={'placeholder': 'Select supplier'}),
            'date': forms.DateInput(attrs={'placeholder': 'Select date', 'type': 'date'}),
        }
        labels = {
            'supplier': 'Supplier',
            'date': 'Date',
        }




class WholesaleProcurementItemForm(forms.ModelForm):
    class Meta:
        model = WholesaleProcurementItem
        fields = ['item_name', 'brand', 'unit', 'quantity', 'cost_price']
        widgets = {
            'item_name': forms.TextInput(attrs={'placeholder': 'Enter item name'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Enter brand name'}),
            'unit': forms.Select(attrs={'placeholder': 'Select unit'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'cost_price': forms.NumberInput(attrs={'placeholder': 'Enter cost price'}),
        }
        labels = {
            'item_name': 'Item Name',
            'brand': 'Brand',
            'unit': 'Unit',
            'quantity': 'Quantity',
            'cost_price': 'Cost Price',
        }

ProcurementItemFormSet = modelformset_factory(ProcurementItem, form=WholesaleProcurementItemForm, extra=0)
