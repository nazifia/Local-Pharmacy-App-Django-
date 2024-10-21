from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm




# Create your views here.

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Perform any necessary authentication logic here
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('index')
    return render(request, 'index.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def logout_user(request):
    logout(request)
    return redirect('index')




def edit_user_profile(request):
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return render(request, 'edit_user_profile.html', {'form': form})
    else:
        form = EditUserProfileForm(request.POST, instance=request.user)
        return render(request, 'edit_user_profile.html', {'form': form})



@login_required
def change_user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('store')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_user_password.html', {'form': form})


@login_required
def store(request):
    items = Item.objects.all().order_by('name')
    return render(request, 'store.html', {'items':items})

@login_required
def search_item(request):
    query = request.GET.get('search', '')
    if query:
        items = Item.objects.filter(name__icontains=query)
    else:
        items = Item.objects.all()
    return render(request, 'partials/search.html', {'items': items})


@login_required
def add_item(request):
    if request.method == 'POST':
        form = addItemForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item added successfully')
            return redirect('store')
    else:
        form = addItemForm()
    return render(request, 'add_item.html', {'form': form})





@user_passes_test(is_admin)
def edit_item(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == 'POST':
        form = addItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully')
            return redirect('store')
        else:
            messages.error(request, 'Failed to update item')
    else:
        form = addItemForm(instance=item)
    if request.headers.get('HX-Request'):
        return render(request, 'edit_item_modal.html', {'form': form, 'item': item})
    else:
        return render(request, 'store.html')


@login_required
@user_passes_test(is_admin)
def delete_item(request, pk):
    item = get_object_or_404(Item, id=pk)
    item.delete()
    messages.success(request, 'Item deleted successfully')
    return redirect('store')

@login_required
def dispense(request):
    if request.method == 'POST':
        form = dispenseForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data['q']
            results = Item.objects.filter(name__icontains=q)
    else:
        form = dispenseForm()
        results = None
    return render(request, 'dispense_modal.html', {'form': form, 'results': results})

@login_required
def cart(request):
    return render(request, 'cart.html')

@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        
        
        if item.stock_quantity >= quantity:
            cart_item, created = CartItem.objects.get_or_create(item=item, defaults={'quantity': 1})
            
            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
                
            if item.stock_quantity >= cart_item.quantity:
                item.stock_quantity -= quantity
                item.save()
                cart_item.save()
                
            cart_items = CartItem.objects.all()
            total_price = sum(cart_item.item.price * cart_item.quantity for cart_item in cart_items)
            
            return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})
        else:
            messages.error(request, f'Quantity requested {cart_item.quantity} exceeds the available stock quantity {item.stock_quantity} for {item.name}')
    else:
        messages.error(request, f'Quantity requested {cart_item.quantity} exceeds the available stock quantity {item.stock_quantity} for {item.name}')
    return render(request, 'cart.html', {})

@login_required
def view_cart(request):
    cart_items = CartItem.objects.all()
    
    total_price = 0
    total_discount = 0
    
    if request.method == 'POST':
        for cart_item in cart_items:
            discount_input_name = f'discount_amount-{cart_item.id}'
            discount_amount_str = request.POST.get(discount_input_name, '').strip()
            
            if discount_amount_str:
                discount_amount = int(discount_amount_str)
                if discount_amount < 0:
                    messages.error(request, 'Discount amount must be positive.')
                else:
                    cart_item.discount_amount = discount_amount
                    cart_item.save()
                    
    for cart_item in cart_items:
        cart_item.subtotal = cart_item.item.price * cart_item.quantity
        total_price += cart_item.subtotal
        total_discount += cart_item.discount_amount
        
    total_discounted_price = total_price - total_discount
                    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_discount': total_discount,
        'total_price': total_price,
        'total_discounted_price': total_discounted_price,
    })
    


@login_required
def update_cart_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, id=pk)
    item = cart_item.item
    
    if request.method == 'POST':
        quantity_to_return_str = request.POST.get('quantity', '')
        
        if quantity_to_return_str:
            quantity_to_return = int(quantity_to_return_str)
        else:
            messages.error(request, 'Invalid quantity to return')
            return redirect('view_cart')
        
        if 0 < quantity_to_return <= cart_item.quantity:
            item.stock_quantity += quantity_to_return
            item.save()
                        
            cart_item.quantity -= quantity_to_return
            
            if cart_item.quantity > 0:
                cart_item.save()
            else:
                cart_item.delete()
                messages.success(request, f'{cart_item.item.name} is removed from cart')
            messages.success(request, f'{cart_item.item.name} cart quantity updated successfully.')
        else:
            messages.error(request, 'Invalid cart quantity to return')
    return redirect('view_cart')



@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter()
        for cart_item in cart_items:
            store_item = Item.objects.get(id=cart_item.item.id)
            store_item.stock_quantity += cart_item.quantity
            store_item.save()
            cart_item.delete()
        messages.success(request, 'Cart cleared successfully and item(s) returned to store')
        return redirect('view_cart')


    
@login_required
def receipt(request):
    cart_items = CartItem.objects.all()
    
    total_price = 0
    total_discount = 0
    total_discounted_price = 0
    
    for cart_item in cart_items:
        cart_item.subtotal = cart_item.item.price * cart_item.quantity
        total_price += cart_item.subtotal
        total_discount += cart_item.discount_amount
        total_discounted_price = total_price - total_discount
        
        Sales.objects.create(user=request.user, name=cart_item.item.name, quantity=cart_item.quantity, amount=cart_item.subtotal)
        
    for cart_item in cart_items:
        DispensingLog.objects.create(user=request.user, name=cart_item.item.name, quantity=cart_item.quantity, amount=cart_item.subtotal)
    
    CartItem.objects.all().delete()
    
    return render(request, 'receipt.html', {
        'date': timezone.now(),
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_discounted_price': total_discounted_price,
    })
    


@login_required
def reports(request):
    return render(request, 'reports.html')


@login_required
def manage_customers(request):
    return render(request, 'manage_customers.html')

@login_required
@user_passes_test(is_admin)
def dispensing_log(request):
    logs = DispensingLog.objects.all().order_by('-created_at')
    
    if request.GET.get('date'):
        selected_date = parse_date(request.GET.get('date'))
        if selected_date:
            logs = logs.filter(created_at__date=selected_date)
    
        return render(request, 'partials/partials_dispensing_log.html', {'logs': logs})
    
    return render(request, 'dispensing_log.html', {'logs': logs})


@login_required
def exp_date_alert(request):
    alert_threshold = timezone.now() + timedelta(days=90)
    
    expiring_items = Item.objects.filter(exp_date__lte=alert_threshold, exp_date__gt=timezone.now())
    
    expired_items = Item.objects.filter(exp_date__lt=timezone.now())
    
    for expired_item in expired_items:
        
        if expired_item.stock_quantity > 0:
            
            expired_item.stock_quantity = 0
            expired_item.save()
            
    return render(request, 'partials/exp_date_alert.html', {
        'expired_items': expired_items,
        'expiring_items': expiring_items,
    })


def get_daily_sales():
    daily_sales = Sales.objects.annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total_sales=Sum('amount')
    ).order_by('day')
    return daily_sales


def get_monthly_sales():
    monthly_sales = Sales.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_sales=Sum('amount')
    ).order_by('month')
    return monthly_sales



@user_passes_test(is_admin)
def daily_sales(request):
    daily_sales = get_daily_sales().order_by('-day')
    return render(request, 'daily_sales.html', {'daily_sales': daily_sales} )



@user_passes_test(is_admin)
def monthly_sales(request):
    monthly_sales = get_monthly_sales().order_by('-month')
    return render(request, 'monthly_sales.html', {'monthly_sales': monthly_sales} )



@login_required
def register_customers(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer successfully registered')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': True, 'message': 'Registration successful'})
            return redirect('customer_list')
    else:
        form = CustomerForm()
    if request.headers.get('HX-Request'):
        return render(request, 'partials/register_customers.html', {'form': form})
    return render(request, 'register_customers.html', {'form': form})



@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'partials/customer_list.html', {'customers': customers})



@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'{customer.name} edited successfully.')
            return redirect('customer_list')
        else:
            messages.error(request, f'{customer.name} failed to edit, please try again')
    else:
        form = CustomerForm(instance=customer)
    if request.headers.get('HX-Request'):
        return render(request, 'partials/edit_customer_modal.html', {'form': form, 'customer': customer})
    else:
        return render(request, 'manage_customers.html')




@login_required
@user_passes_test(is_admin)
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.success(request, 'Customer deleted successfully.')
    return redirect('customer_list')



@login_required
def add_funds(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    wallet = customer.wallet
    
    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            wallet.add_funds(amount)
            messages.success(request, f'Funds successfully added to {wallet.customer.name}\'s wallet.')
            return redirect('customer_list')
        else:
            messages.error(request, 'Error adding funds')
    else:
        form = AddFundsForm()
    return render(request, 'partials/add_funds.html', {'form': form, 'customer': customer})



@login_required
def wallet_details(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    wallet = customer.wallet
    return render(request, 'partials/wallet_details.html', {'customer': customer, 'wallet': wallet})



@login_required
@user_passes_test(is_admin)
def reset_wallet(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    wallet.balance = 0
    wallet.save()
    messages.success(request, f'{wallet.customer.name}\'s wallet reset successfully.')
    return redirect('customer_list')



@login_required
def select_items(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    items = Item.objects.all().order_by('name')
    
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        quantities = request.POST.getlist('quantities')
        
        total_price= 0
        for item_id, quantity in zip(item_ids, quantities):
            item = get_object_or_404(Item, id=item_id)
            quantity = int(quantity)
            total_price += item.price * quantity
            
            if item.stock_quantity >= quantity:
                item.stock_quantity -= quantity
                item.save()
            else:
                messages.error(request, f"Not enough stock for {item.name}.")
                return render(request, 'partials/select_items.html', {'items': items, 'customer': customer})
            
            customer.wallet.balance -= total_price
            customer.wallet.save()
            
            Sales.objects.create(user=request.user, name=item.name, quantity=quantity,  amount=item.price * quantity,
            )

            
            DispensingLog.objects.create(user=request.user, name=item.name, quantity=quantity, amount=total_price)
            
            return HttpResponse('<h3 style="color: green; text-align: center;">Purchase successful</h3>')
        
    return render(request, 'partials/select_items.html', {'items': items, 'customer': customer})



@login_required
def search_customer_items(request, customer_id):
    query = request.GET.get('query')
    if query:
        items = Item.objects.filter(name__icontains=query)
    
    return render(request, 'partials/item_table_body.html', {'items': items})


@login_required
def customers_on_negative(request):
    customers_on_negative = Customer.objects.filter(wallet__balance__lt=0)
    return render(request, 'partials/customers_on_negative.html', {'customers': customers_on_negative})