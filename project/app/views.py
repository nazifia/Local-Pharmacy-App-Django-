from django.db.models.functions import TruncDay, TruncMonth, TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *
from django.db.models import Sum, ExpressionWrapper, fields, F
from django.utils.dateparse import parse_date
from django.db import transaction
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
    
    # Calculate total purchase value and total stock value
    total_purchase_value = sum(item.cost * item.stock_quantity for item in items)
    total_stock_value = sum(item.price * item.stock_quantity for item in items)
    total_profit = total_stock_value - total_purchase_value
    
    context = {
        'items': items,
        'total_purchase_value': total_purchase_value,
        'total_stock_value': total_stock_value,
        'total_profit': total_profit,
    }
    return render(request, 'store.html', context)

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
            messages.success(request, f'{item.name} updated successfully')
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
def return_item(request, pk):
    item = get_object_or_404(Item, id=pk)

    if request.method == 'POST':
        form = ReturnItemForm(request.POST)
        if form.is_valid():
            return_quantity = form.cleaned_data.get('return_item_quantity')
            
            # Ensure quantity is valid
            if return_quantity <= 0:
                messages.error(request, 'Invalid return item quantity')
                return redirect('store')

            try:
                with transaction.atomic():
                    # Update item stock quantity
                    item.stock_quantity += return_quantity
                    item.save()
                    
                    # Find the associated sales item record
                    sales_item = SalesItem.objects.filter(item=item, quantity__gte=return_quantity).first()
                    if not sales_item:
                        messages.error(request, f'No matching sales record found for {item.name}.')
                        return redirect('store')

                    # Adjust or delete the sales item
                    if sales_item.quantity > return_quantity:
                        sales_item.quantity -= return_quantity
                        sales_item.save()
                    else:
                        # Remove sales item if all quantity is returned
                        sales_item.delete()

                    # Adjust sales total amount
                    sales = sales_item.sales
                    sales.calculate_total_amount()

                    # Reverse wallet deduction if applicable
                    if sales.customer and sales.customer.wallet:
                        wallet = sales.customer.wallet
                        refund_amount = return_quantity * sales_item.price
                        wallet.balance += refund_amount
                        wallet.save()

                        # Log transaction history for the refund
                        TransactionHistory.objects.create(
                            customer=sales.customer,
                            transaction_type='refund',
                            amount=refund_amount,
                            description=f'Refund for {return_quantity} of {item.name}'
                        )

                    # Remove associated dispensing log if applicable
                    dispensing_log = DispensingLog.objects.filter(
                        user=sales.user, name=item.name, quantity=return_quantity
                    ).first()
                    if dispensing_log:
                        dispensing_log.delete()

                    messages.success(request, f'{return_quantity} of {item.name} successfully returned.')
                    return redirect('store')
            
            except Exception as e:
                messages.error(request, f'Error processing return: {e}')
                return redirect('store')
        else:
            messages.error(request, 'Form is invalid, please check your input.')
    else:
        form = ReturnItemForm(instance=item)

    if request.headers.get('HX-Request'):
        return render(request, 'return_item_modal.html', {'form': form, 'item': item})
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
    cart_items = CartItem.objects.all()
    total_price = sum(item.item.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        if item.stock_quantity >= quantity:
            cart_item, created = CartItem.objects.get_or_create(item=item, defaults={'quantity': 0})
            cart_item.quantity += quantity
            item.stock_quantity -= quantity
            item.save()
            cart_item.save()
            messages.success(request, f'Added {quantity} {item.name}(s) to the cart.')
        else:
            messages.error(request, f'Not enough stock for {item.name}.')
    return redirect('cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.all()
    total_price, total_discount = 0, 0
    if request.method == 'POST':
        for cart_item in cart_items:
            discount = int(request.POST.get(f'discount_amount-{cart_item.id}', 0))
            cart_item.discount_amount = max(discount, 0)
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
    if request.method == 'POST':
        quantity_to_return = int(request.POST.get('quantity', 0))
        if 0 < quantity_to_return <= cart_item.quantity:
            cart_item.item.stock_quantity += quantity_to_return
            cart_item.item.save()
            cart_item.quantity -= quantity_to_return
            cart_item.save() if cart_item.quantity > 0 else cart_item.delete()
            messages.success(request, f'Updated quantity of {cart_item.item.name}.')
    return redirect('view_cart')

@login_required
def clear_cart(request):
    if request.method == 'POST':
        for cart_item in CartItem.objects.all():
            cart_item.item.stock_quantity += cart_item.quantity
            cart_item.item.save()
            cart_item.delete()
        messages.success(request, 'Cart cleared and items returned to stock.')
    return redirect('view_cart')



@login_required
def receipt(request):
    # Get the buyer's name from the request, if provided
    buyer_name = request.POST.get('buyer_name', '')

    # Retrieve cart items
    cart_items = CartItem.objects.all()
    total_price, total_discount = 0, 0

    # Calculate totals
    for cart_item in cart_items:
        cart_item.subtotal = cart_item.item.price * cart_item.quantity
        total_price += cart_item.subtotal
        total_discount += cart_item.discount_amount

    # Determine the total amount to record (apply discount if present)
    total_discounted_price = total_price - total_discount
    final_total = total_discounted_price if total_discount > 0 else total_price

    # Create a Sales instance for the transaction with final total
    sales = Sales.objects.create(user=request.user, total_amount=final_total)

    # Create SalesItem and DispensingLog entries for each cart item
    for cart_item in cart_items:
        SalesItem.objects.create(
            sales=sales,
            item=cart_item.item,
            quantity=cart_item.quantity,
            price=cart_item.item.price
        )
        DispensingLog.objects.create(
            user=request.user,
            name=cart_item.item.name,
            quantity=cart_item.quantity,
            amount=cart_item.subtotal
        )

    # Generate and save the receipt with a full UUID and buyer's name if no customer is linked
    receipt_id = uuid.uuid4()  # Full UUID
    receipt = Receipt.objects.create(
        receipt_id=receipt_id,
        sales=sales,
        total_amount=final_total,
        buyer_name=buyer_name if not sales.customer else None
    )

    # Clear the cart after processing
    cart_items.delete()

    # Retrieve sales items to display in the receipt
    sales_items = sales.sales_items.all()

    # Render the receipt template with necessary data
    return render(request, 'receipt.html', {
        'date': timezone.now(),
        'total_price': total_price,
        'total_discount': total_discount,
        'total_discounted_price': total_discounted_price,
        'receipt_id': receipt.receipt_id,  # Full UUID for receipt ID
        'sales_items': sales_items,
        'buyer_name': receipt.customer.name if receipt.customer else receipt.buyer_name,  # Display buyer name
    })




@login_required
def retrieve_receipt(request):
    if request.method == 'POST':
        receipt_id = request.POST.get('receipt_id')
        try:
            # Ensure the receipt ID is treated as a full UUID
            receipt = get_object_or_404(Receipt, receipt_id=uuid.UUID(receipt_id))  # Convert to UUID
            sales_items = receipt.sales.sales_items.all()
            sales_items_with_subtotal = [
                {
                    'name': item.item.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'subtotal': item.price * item.quantity
                }
                for item in sales_items
            ]
            return render(request, 'retrieve_receipt.html', {
                'receipt': receipt,
                'sales_items_with_subtotal': sales_items_with_subtotal
            })
        except (Receipt.DoesNotExist, ValueError):
            messages.error(request, 'Receipt not found or invalid receipt ID.')
    return render(request, 'retrieve_receipt.html')


@login_required
def reports(request):
    return render(request, 'reports.html')


@login_required
def manage_customers(request):
    return render(request, 'manage_customers.html')



@login_required
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
    # Get daily sales with profit calculations
    daily_sales = (
        SalesItem.objects
        .annotate(day=TruncDay('sales__date'))
        .values('day')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),  # Assuming cost is in the Item model
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=fields.DecimalField()
            )
        )
        .order_by('day')
    )
    return daily_sales



def get_monthly_sales():
    # Get monthly sales with profit calculations
    monthly_sales = (
        SalesItem.objects
        .annotate(month=TruncMonth('sales__date'))
        .values('month')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),  # Assuming cost is in the Item model
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=fields.DecimalField()
            )
        )
        .order_by('month')
    )
    return monthly_sales




@user_passes_test(is_admin)
def daily_sales(request):
    daily_sales = get_daily_sales().order_by('-day')
    return render(request, 'daily_sales.html', {'daily_sales': daily_sales})

@user_passes_test(is_admin)
def monthly_sales(request):
    monthly_sales = get_monthly_sales().order_by('-month')
    return render(request, 'monthly_sales.html', {'monthly_sales': monthly_sales})


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




from decimal import Decimal

@login_required
def select_items(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    items = Item.objects.all().order_by('name')
    
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        quantities = request.POST.getlist('quantities')
        total_price = Decimal('0.00')
        purchased_items = []

        # Create a single Sales instance for this transaction
        sale = Sales.objects.create(customer=customer, user=request.user, total_amount=Decimal('0.00'))

        for item_id, quantity in zip(item_ids, quantities):
            item = get_object_or_404(Item, id=item_id)
            quantity = int(quantity)
            item_total = item.price * quantity
            total_price += item_total
            
            # Check stock quantity
            if item.stock_quantity >= quantity:
                item.stock_quantity -= quantity
                item.save()
            else:
                messages.error(request, f"Not enough stock for {item.name}.")
                return render(request, 'partials/select_items.html', {'items': items, 'customer': customer})
            
            # Deduct from customer's wallet
            customer.wallet.balance -= item_total
            customer.wallet.save()
            
            # Create a SalesItem instance for each item in the sale
            SalesItem.objects.create(sales=sale, item=item, price=item.price, quantity=quantity)

            # Log the dispensing action
            DispensingLog.objects.create(user=request.user, name=item.name, quantity=quantity, amount=item_total)
            
            # Add item to purchased_items for receipt
            purchased_items.append({
                'name': item.name,
                'quantity': quantity,
                'price': float(item.price),
                'total': float(item_total)
            })

        # Update the total amount in the Sales instance
        sale.total_amount = total_price
        sale.save()

        # Save receipt data to session
        request.session['receipt_data'] = {
            'purchased_items': purchased_items,
            'total_price': float(total_price)
        }

        return redirect('customer_receipt', customer_id=pk)
    
    return render(request, 'partials/select_items.html', {'items': items, 'customer': customer})




@login_required
def customer_receipt(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    receipt_data = request.session.pop('receipt_data', None)
    
    if not receipt_data:
        return redirect('select_items', pk=customer_id)
    
    return render(request, 'partials/customer_receipt.html', {'customer': customer, 'receipt_data': receipt_data, 'date': timezone.now()})



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




def customer_sales_history(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    sales = Sales.objects.filter(customer=customer).prefetch_related('sales_items__item').order_by('-date')

    return render(request, 'partials/customer_transaction_history.html', {'customer': customer, 'sales': sales})



from django.shortcuts import render, get_object_or_404
from .models import Receipt, SalesItem

def retrieve_receipt(request):
    if request.method == 'POST':
        receipt_id = request.POST.get('receipt_id')
        try:
            receipt = Receipt.objects.get(receipt_id=receipt_id)
            # Calculate subtotal for each item in the sales
            sales_items_with_subtotal = [
                {
                    'name': item.item.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'subtotal': item.price * item.quantity  # Calculate subtotal here
                }
                for item in receipt.sales.sales_items.all()
            ]
            
            context = {
                'receipt': receipt,
                'sales_items_with_subtotal': sales_items_with_subtotal
            }
            return render(request, 'partials/retrieve_receipt.html', context)

        except Receipt.DoesNotExist:
            context = {'error_message': 'Receipt not found.'}
            return render(request, 'partials/retrieve_receipt.html', context)

    return render(request, 'partials/retrieve_receipt.html')



def reprint_receipt(request, receipt_id):
    receipt = get_object_or_404(Receipt, receipt_id=receipt_id)
    receipt.mark_as_printed()  # Optionally mark as printed

    # Calculate subtotals for each item in the sales items
    sales_items_with_subtotal = [
        {
            'name': item.item.name,
            'quantity': item.quantity,
            'price': item.price,
            'subtotal': item.price * item.quantity  # Calculate subtotal here
        }
        for item in receipt.sales.sales_items.all()
    ]

    return render(request, 'print_receipt.html', {
        'receipt': receipt,
        'sales_items_with_subtotal': sales_items_with_subtotal  # Pass calculated items
    })


def receipt_id(request):
    return render(request, 'partials/receipt_id.html')


@user_passes_test(is_admin)
def activity_logs(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'partials/activities.html', {'logs': logs})