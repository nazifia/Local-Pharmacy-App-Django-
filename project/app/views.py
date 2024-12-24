from django.db.models.functions import TruncDay, TruncMonth, TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from .models import *
from .forms import *
from django.db.models import Sum, ExpressionWrapper, fields, F
from django.db.models import DecimalField, Q
from django.utils.dateparse import parse_date
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
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
            messages.warning(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_user_password.html', {'form': form})




@login_required
def store(request):
    items = Item.objects.all().order_by('name')
    
    # Ensure correct field values for cost and price
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
        form = addItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()  # Calls the model's save method, which calculates price based on markup
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
            # Convert markup_percentage to Decimal to ensure compatible types
            markup_percentage = Decimal(form.cleaned_data.get("markup_percentage", 0))
            item.markup_percentage = markup_percentage
            
            # Calculate and update the price
            item.price = item.cost + (item.cost * markup_percentage / Decimal(100))
            
            # Save the form with updated fields
            form.save()
            
            messages.success(request, f'{item.name} updated successfully')
            return redirect('store')
        else:
            messages.warning(request, 'Failed to update item')
    else:
        form = addItemForm(instance=item)

    # Render the modal or full page based on request type
    if request.headers.get('HX-Request'):
        return render(request, 'edit_item_modal.html', {'form': form, 'item': item})
    else:
        return render(request, 'store.html', {'form': form})




@login_required
def return_item(request, pk):
    item = get_object_or_404(Item, id=pk)

    if request.method == 'POST':
        form = ReturnItemForm(request.POST)
        if form.is_valid():
            return_quantity = form.cleaned_data.get('return_item_quantity')

            # Validate the return quantity
            if return_quantity <= 0:
                messages.warning(request, 'Invalid return item quantity.')
                return redirect('store')

            try:
                with transaction.atomic():
                    # Update item stock
                    item.stock_quantity += return_quantity
                    item.save()

                    # Find the sales item associated with the returned item
                    sales_item = SalesItem.objects.filter(item=item).order_by('-quantity').first()
                    if not sales_item or sales_item.quantity < return_quantity:
                        messages.warning(request, f'No valid sales record found for {item.name}.')
                        return redirect('store')

                    # Calculate refund and update sales item
                    refund_amount = return_quantity * sales_item.price
                    if sales_item.quantity > return_quantity:
                        sales_item.quantity -= return_quantity
                        sales_item.save()
                    else:
                        sales_item.delete()

                    # Update sales total
                    sales = sales_item.sales
                    sales.total_amount -= refund_amount
                    sales.save()

                    # Process wallet refund if applicable
                    if sales.customer and hasattr(sales.customer, 'wallet'):
                        wallet = sales.customer.wallet
                        wallet.balance += refund_amount
                        wallet.save()

                        # Log the refund transaction
                        TransactionHistory.objects.create(
                            customer=sales.customer,
                            transaction_type='refund',
                            amount=refund_amount,
                            description=f'Refund for {return_quantity} of {item.name}'
                        )
                        messages.success(
                            request,
                            f'{return_quantity} of {item.name} successfully returned, and ₦{refund_amount} refunded to the wallet.'
                        )
                    else:
                        messages.warning(request, 'Customer wallet not found or not associated.')

                    # Update dispensing log
                    dispensing_log = DispensingLog.objects.filter(user=sales.user, name=item.name).last()
                    if dispensing_log:
                        if dispensing_log.quantity == return_quantity:
                            dispensing_log.quantity = 0
                            dispensing_log.status = 'Returned'
                        elif dispensing_log.quantity > return_quantity:
                            dispensing_log.quantity -= return_quantity
                            dispensing_log.status = 'Partially Returned'
                        else:
                            messages.warning(
                                request,
                                f'Returned quantity exceeds dispensed quantity for {item.name}.'
                            )
                            return redirect('store')

                        dispensing_log.save()

                    # Update daily and monthly sales data
                    daily_sales = get_daily_sales()
                    monthly_sales = get_monthly_sales()

                    # Render updated logs for HTMX requests
                    if request.headers.get('HX-Request'):
                        context = {
                            'logs': DispensingLog.objects.all().order_by('-created_at'),
                            'daily_sales': daily_sales,
                            'monthly_sales': monthly_sales
                        }
                        return render(request, 'partials/partials_dispensing_log.html', context)

                    messages.success(
                        request,
                        f'{return_quantity} of {item.name} successfully returned, sales and logs updated.'
                    )
                    return redirect('store')

            except Exception as e:
                # Handle exceptions during atomic transaction
                print(f'Error during item return: {e}')
                messages.error(request, f'Error processing return: {e}')
                return redirect('store')
        else:
            messages.warning(request, 'Invalid input. Please correct the form and try again.')

    else:
        # Display the return form in a modal or a page
        form = ReturnItemForm()

    # Return appropriate response for HTMX or full-page requests
    if request.headers.get('HX-Request'):
        return render(request, 'return_item_modal.html', {'form': form, 'item': item})
    else:
        return render(request, 'store.html', {'form': form})




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
            results = Item.objects.filter(Q(name__icontains=q) | Q(brand__icontains=q))
    else:
        form = dispenseForm()
        results = None
    return render(request, 'dispense_modal.html', {'form': form, 'results': results})



@login_required
def cart(request):
    cart_items = CartItem.objects.all()
    total_price = sum(item.item.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})



from django.views.decorators.http import require_POST
@login_required
@require_POST
def add_to_cart(request, pk):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, id=pk)
        quantity = int(request.POST.get('quantity', 1))
        unit = request.POST.get('unit')

        if quantity <= 0:
            messages.warning(request, "Quantity must be greater than zero.")
            return redirect('cart')

        if quantity > item.stock_quantity:
            messages.warning(request, f"Not enough stock for {item.name}. Available stock: {item.stock_quantity}")
            return redirect('cart')

        # Add the item to the cart or update its quantity if it already exists
        cart_item, created = CartItem.objects.get_or_create(
            item=item,
            unit=unit,
            defaults={'quantity': quantity, 'discount_amount': Decimal('0.0')}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Update stock quantity in the wholesale inventory
        item.stock_quantity -= quantity
        item.save()

        messages.success(request, f"{quantity} {item.unit} of {item.name} added to cart.")

        # Return the cart summary as JSON if this was an HTMX request
        if request.headers.get('HX-Request'):
            cart_items = CartItem.objects.all()
            total_price = sum(cart_item.item.price * cart_item.quantity for cart_item in cart_items)
            total_discount = sum(cart_item.discount_amount for cart_item in cart_items)
            total_discounted_price = total_price - total_discount

            # Return JSON data for HTMX update
            return JsonResponse({
                'cart_items_count': cart_items.count(),
                'total_price': float(total_price),
                'total_discount': float(total_discount),
                'total_discounted_price': float(total_discounted_price),
            })

        # Redirect to the wholesale cart page if not an HTMX request
        return redirect('cart')
    else:
        return redirect('index')




@login_required
def customer_history(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    histories = ItemSelectionHistory.objects.filter(customer=customer).select_related('customer__user').order_by('-date')
    
    # Add a 'subtotal' field to each history
    for history in histories:
        history.subtotal = history.quantity * history.unit_price

    return render(request, 'partials/customer_history.html', {
        'customer': customer,
        'histories': histories,
    })




@transaction.atomic
@login_required
def select_items(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    items = Item.objects.all().order_by('name')

    # Fetch wallet balance
    wallet_balance = Decimal('0.0')
    try:
        wallet_balance = customer.wallet.balance
    except Wallet.DoesNotExist:
        messages.warning(request, 'This customer does not have an associated wallet.')

    if request.method == 'POST':
        action = request.POST.get('action', 'purchase')  # Default to purchase
        item_ids = request.POST.getlist('item_ids', [])
        quantities = request.POST.getlist('quantities', [])
        discount_amounts = request.POST.getlist('discount_amounts', [])
        units = request.POST.getlist('units', [])

        if len(item_ids) != len(quantities):
            messages.warning(request, 'Mismatch between selected items and quantities.')
            return redirect('select_items', pk=pk)

        total_cost = Decimal('0.0')

        # Fetch or create a Sales record
        sales, created = Sales.objects.get_or_create(
            user=request.user,
            customer=customer,
            defaults={'total_amount': Decimal('0.0')}
        )

        # Fetch or create a Receipt
        receipt, receipt_created = Receipt.objects.get_or_create(
            customer=customer,
            sales=sales,
            defaults={
                'total_amount': Decimal('0.0'),
                'buyer_name': customer.name,
                'buyer_address': customer.address,
                'date': timezone.now(),
                'printed': False,
            }
        )

        for i, item_id in enumerate(item_ids):
            try:
                item = Item.objects.get(id=item_id)
                quantity = int(quantities[i])
                discount = Decimal(discount_amounts[i]) if i < len(discount_amounts) else Decimal('0.0')
                unit = units[i] if i < len(units) else item.unit

                if action == 'purchase':
                    # Check stock and update inventory
                    if quantity > item.stock_quantity:
                        messages.warning(request, f'Not enough stock for {item.name}.')
                        return redirect('select_items', pk=pk)

                    item.stock_quantity -= quantity
                    item.save()

                    # Update or create a CartItem
                    cart_item, created = CartItem.objects.get_or_create(
                        item=item,
                        defaults={'quantity': quantity, 'discount_amount': discount, 'unit': unit}
                    )
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.discount_amount += discount
                        cart_item.unit = unit
                    cart_item.save()

                    # Calculate subtotal
                    subtotal = (item.price * quantity) - discount
                    total_cost += subtotal

                    # Update or create SalesItem
                    sales_item, created = SalesItem.objects.get_or_create(
                        sales=sales,
                        item=item,
                        defaults={'quantity': quantity, 'price': item.price}
                    )
                    if not created:
                        sales_item.quantity += quantity
                        sales_item.save()

                    # Update the receipt
                    receipt.total_amount += subtotal
                    receipt.save()

                    # **Log Item Selection History (Purchase)**
                    ItemSelectionHistory.objects.create(
                        customer=customer,
                        user=request.user,
                        item=item,
                        quantity=quantity,
                        action=action,
                        unit_price=item.price,
                    )

                elif action == 'return':
                    # Handle return logic
                    item.stock_quantity += quantity
                    item.save()

                    try:
                        sales_item = SalesItem.objects.get(sales=sales, item=item)

                        if sales_item.quantity < quantity:
                            messages.warning(request, f"Cannot return more {item.name} than purchased.")
                            return redirect('customer_list')

                        sales_item.quantity -= quantity
                        if sales_item.quantity == 0:
                            sales_item.delete()
                        else:
                            sales_item.save()

                        refund_amount = (item.price * quantity) - discount

                        # Update sales total
                        sales.total_amount -= refund_amount
                        sales.save()

                        # Log dispensing action
                        DispensingLog.objects.create(
                            user=request.user,
                            name=item.name,
                            unit=unit,
                            quantity=quantity,
                            amount=refund_amount,
                            status='Partially Returned' if sales_item.quantity > 0 else 'Returned'
                        )

                        # **Log Item Selection History (Return)**
                        ItemSelectionHistory.objects.create(
                            customer=customer,
                            user=request.user,
                            item=item,
                            quantity=quantity,
                            action=action,
                            unit_price=item.price,
                            subtotal=quantity * item.price,
                        )

                        total_cost -= refund_amount

                        # Update the receipt
                        receipt.total_amount -= refund_amount
                        receipt.save()

                    except SalesItem.DoesNotExist:
                        messages.warning(request, f"Item {item.name} is not part of the sales.")
                        return redirect('select_items', pk=pk)

            except Item.DoesNotExist:
                messages.warning(request, 'One of the selected items does not exist.')
                return redirect('select_items', pk=pk)

        # Update customer's wallet balance
        try:
            wallet = customer.wallet
            if action == 'purchase':
                wallet.balance -= total_cost
            elif action == 'return':
                wallet.balance += abs(total_cost)
            wallet.save()
        except Wallet.DoesNotExist:
            messages.warning(request, 'Customer does not have a wallet.')
            return redirect('select_items', pk=pk)

        action_message = 'added to cart' if action == 'purchase' else 'returned successfully'
        messages.success(request, f'Action completed: Items {action_message}.')
        return redirect('cart')

    return render(request, 'partials/select_items.html', {
        'customer': customer,
        'items': items,
        'wallet_balance': wallet_balance
    })




@login_required
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.select_related('item').all()
        total_price, total_discount = 0, 0

        if request.method == 'POST':
            # Process each discount form submission
            for cart_item in cart_items:
                # Fetch the discount amount using cart_item.id in the input name
                discount = Decimal(request.POST.get(f'discount_amount-{cart_item.id}', 0))
                cart_item.discount_amount = max(discount, 0)
                cart_item.save()

        # Calculate totals
        for cart_item in cart_items:
            cart_item.subtotal = cart_item.item.price * cart_item.quantity
            total_price += cart_item.subtotal
            total_discount += cart_item.discount_amount

        
        final_total = total_price - total_discount

        total_discounted_price = total_price - total_discount
        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'total_discount': total_discount,
            'total_price': total_price,
            'total_discounted_price': total_discounted_price,
            'final_total': final_total,
        })
    else:
        return redirect('index')



@login_required
def update_cart_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, id=pk)
    if request.method == 'POST':
        quantity_to_return = int(request.POST.get('quantity', 0))
        if 0 < quantity_to_return <= cart_item.quantity:
            cart_item.item.stock_quantity += quantity_to_return
            cart_item.item.save()

            # Adjust DispensingLog entries
            DispensingLog.objects.filter(
                user=request.user,
                name=cart_item.item.name,
                quantity=quantity_to_return,
                amount=cart_item.item.price * quantity_to_return
            ).delete()

            # Update cart item quantity or remove it
            cart_item.quantity -= quantity_to_return
            cart_item.save() if cart_item.quantity > 0 else cart_item.delete()
            messages.success(request, f'Updated quantity of {cart_item.item.name}.')

    return redirect('cart')






@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.all()

        for cart_item in cart_items:
            # Return items to stock
            cart_item.item.stock_quantity += cart_item.quantity
            cart_item.item.save()

            # Remove DispensingLog entries
            DispensingLog.objects.filter(
                user=request.user,
                name=cart_item.item.name,
                quantity=cart_item.quantity,
                amount=cart_item.item.price * cart_item.quantity
            ).delete()

        # Remove associated Sales entries if no other cart items exist
        Sales.objects.filter(user=request.user).delete()

        # Clear cart items
        cart_items.delete()
        messages.success(request, 'Cart cleared and items returned to stock.')

    return redirect('cart')



@login_required
def receipt(request):
    buyer_name = request.POST.get('buyer_name', '')
    buyer_address = request.POST.get('buyer_address', '')

    # Retrieve cart items
    cart_items = CartItem.objects.all()
    if not cart_items.exists():
        messages.warning(request, "No items in the cart.")
        return redirect('cart')

    total_price, total_discount = 0, 0

    # Calculate totals
    for cart_item in cart_items:
        subtotal = cart_item.item.price * cart_item.quantity
        total_price += subtotal
        total_discount += cart_item.discount_amount

    total_discounted_price = total_price - total_discount
    final_total = total_discounted_price if total_discount > 0 else total_price

    # Ensure a unique Sales instance
    sales = Sales.objects.filter(user=request.user, total_amount=final_total).first()
    if not sales:
        sales = Sales.objects.create(user=request.user, total_amount=final_total)

    try:
        # Ensure a unique Receipt for the Sales instance
        receipt = Receipt.objects.filter(sales=sales).first()
        if not receipt:
            # receipt view
            payment_method = request.POST.get('payment_method', 'Cash')  # Default to 'Cash' if not provided
            receipt = Receipt.objects.create(
                sales=sales,
                receipt_id=uuid.uuid4(),
                total_amount=final_total,
                buyer_name=buyer_name if not sales.customer else None,
                buyer_address=buyer_address,
                date=now(),
                payment_method=payment_method  # Save payment method
                )

    except Exception as e:
        print(f"Error processing receipt: {e}")
        messages.error(request, "An error occurred while processing the receipt.")
        return redirect('cart')

    # Process cart items
    for cart_item in cart_items:
        SalesItem.objects.get_or_create(
            sales=sales,
            item=cart_item.item,
            defaults={'quantity': cart_item.quantity, 'price': cart_item.item.price}
        )

        # Create DispensingLog
        subtotal = cart_item.item.price * cart_item.quantity
        DispensingLog.objects.create(
            user=request.user,
            name=cart_item.item.name,
            unit=cart_item.item.unit,
            quantity=cart_item.quantity,
            amount=subtotal,
            status="Dispensed"
        )

    # Save receipt data in session
    request.session['receipt_data'] = {
        'total_price': float(total_price),
        'total_discount': float(total_discount),
        'buyer_address': buyer_address,
    }
    request.session['receipt_id'] = str(receipt.receipt_id)

    # Clear cart
    cart_items.delete()

    daily_sales_data = get_daily_sales()
    monthly_sales_data = get_monthly_sales()

    sales_items = sales.sales_items.all()
    
    payment_methods = ["Cash", "Wallet", "Transfer"]
    # receipt = get_object_or_404(Receipt, id=request.session.get('receipt_id'))  # Example
    
    return render(request, 'receipt.html', {
    'receipt': receipt,
    'sales_items': sales_items,
    'total_price': total_price,
    'total_discount': total_discount,
    'total_discounted_price': total_discounted_price,
    'daily_sales': daily_sales_data,
    'monthly_sales': monthly_sales_data,
    'logs': DispensingLog.objects.filter(user=request.user),
    'payment_methods': payment_methods,
})






# Receipt List View
def receipt_list(request):
    receipts = Receipt.objects.all().order_by('-date')  # Order by date, latest first
    return render(request, 'partials/receipt_list.html', {'receipts': receipts})




@login_required
def receipt_detail(request, receipt_id):
    # Retrieve the existing receipt
    receipt = get_object_or_404(Receipt, receipt_id=receipt_id)

    # If the form is submitted, update buyer details
    if request.method == 'POST':
        buyer_name = request.POST.get('buyer_name')
        buyer_address = request.POST.get('buyer_address')

        # Update receipt buyer info if provided
        if buyer_name:
            receipt.buyer_name = buyer_name
        if buyer_address:
            receipt.buyer_address = buyer_address
        
        payment_method = request.POST.get('payment_method')
        if payment_method:
            receipt.payment_method = payment_method
        receipt.save()

        # Redirect to the same page to reflect updated details
        return redirect('receipt_detail', receipt_id=receipt.receipt_id)

    # Retrieve sales and sales items linked to the receipt
    sales = receipt.sales
    sales_items = sales.sales_items.all() if sales else []

    # Calculate totals for the receipt
    total_price = sum(item.subtotal for item in sales_items)
    total_discount = Decimal('0.0')  # Modify if a discount amount is present in `Receipt`
    total_discounted_price = total_price - total_discount

    # Update and save the receipt with calculated totals
    receipt.total_amount = total_discounted_price
    receipt.total_discount = total_discount
    receipt.save()

    return render(request, 'partials/receipt_detail.html', {
        'receipt': receipt,
        'sales_items': sales_items,
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
def dispensing_log(request):
    # Retrieve all dispensing logs ordered by the most recent
    logs = DispensingLog.objects.all().order_by('-created_at')

    # Filter logs by the selected date if provided
    if date_filter := request.GET.get('date'):
        selected_date = parse_date(date_filter)
        if selected_date:
            logs = logs.filter(created_at__date=selected_date)
            return render(request, 'partials/partials_dispensing_log.html', {'logs': logs})

    # Filter logs by status if provided
    if status_filter := request.GET.get('status'):
        logs = logs.filter(status=status_filter)

        return render(request, 'partials/partials_dispensing_log.html', {'logs': logs})

    # Render the full template for non-HTMX requests
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



# Function to get daily sales, including wholesale
from collections import defaultdict
def get_daily_sales():
    # Fetch daily sales data
    regular_sales = (
        SalesItem.objects
        .annotate(day=TruncDay('sales__date'))
        .values('day')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=DecimalField()
            )
        )
    )

    wholesale_sales = (
        WholesaleSalesItem.objects
        .annotate(day=TruncDay('sales__date'))
        .values('day')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=DecimalField()
            )
        )
    )

    # Combine results
    combined_sales = defaultdict(lambda: {'total_sales': 0, 'total_cost': 0, 'total_profit': 0})

    for sale in regular_sales:
        day = sale['day']
        combined_sales[day]['total_sales'] += sale['total_sales']
        combined_sales[day]['total_cost'] += sale['total_cost']
        combined_sales[day]['total_profit'] += sale['total_profit']

    for sale in wholesale_sales:
        day = sale['day']
        combined_sales[day]['total_sales'] += sale['total_sales']
        combined_sales[day]['total_cost'] += sale['total_cost']
        combined_sales[day]['total_profit'] += sale['total_profit']

    # Convert combined sales to a sorted list by date in descending order
    sorted_combined_sales = sorted(combined_sales.items(), key=lambda x: x[0], reverse=True)

    return sorted_combined_sales



from collections import defaultdict
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth

def get_monthly_sales():
    # Fetch monthly sales data
    regular_sales = (
        SalesItem.objects
        .annotate(month=TruncMonth('sales__date'))
        .values('month')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=DecimalField()
            )
        )
    )

    wholesale_sales = (
        WholesaleSalesItem.objects
        .annotate(month=TruncMonth('sales__date'))
        .values('month')
        .annotate(
            total_sales=Sum(F('price') * F('quantity')),
            total_cost=Sum(F('item__cost') * F('quantity')),
            total_profit=ExpressionWrapper(
                Sum(F('price') * F('quantity')) - Sum(F('item__cost') * F('quantity')),
                output_field=DecimalField()
            )
        )
    )

    # Combine results
    combined_sales = defaultdict(lambda: {'total_sales': 0, 'total_cost': 0, 'total_profit': 0})

    for sale in regular_sales:
        month = sale['month']
        combined_sales[month]['total_sales'] += sale['total_sales']
        combined_sales[month]['total_cost'] += sale['total_cost']
        combined_sales[month]['total_profit'] += sale['total_profit']

    for sale in wholesale_sales:
        month = sale['month']
        combined_sales[month]['total_sales'] += sale['total_sales']
        combined_sales[month]['total_cost'] += sale['total_cost']
        combined_sales[month]['total_profit'] += sale['total_profit']

    # Sort combined sales by month in descending order (most recent first)
    return sorted(combined_sales.items(), key=lambda x: x[0], reverse=True)



@user_passes_test(is_admin)
def daily_sales(request):
    daily_sales = get_daily_sales()  # Already sorted by date in descending order
    context = {'daily_sales': daily_sales}
    return render(request, 'daily_sales.html', context)



@user_passes_test(is_admin)
def monthly_sales(request):
    monthly_sales = get_monthly_sales()  # This is already sorted
    context = {'monthly_sales': monthly_sales}
    return render(request, 'monthly_sales.html', context)


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
            messages.warning(request, f'{customer.name} failed to edit, please try again')
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
            messages.warning(request, 'Error adding funds')
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
def customer_receipt(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    receipt_data = request.session.pop('receipt_data', None)
    receipt_id = request.session.pop('receipt_id', None)

    # Redirect to 'select_items' if no receipt data exists in the session
    if not receipt_data:
        return redirect('select_items', pk=customer_id)

    # Retrieve or create a receipt to avoid duplication
    receipt, created = Receipt.objects.get_or_create(
        receipt_id=receipt_id,
        customer=customer,
        defaults={
            'total_amount': receipt_data.get('total_price', 0),
            'buyer_name': customer.name,
            'buyer_address': receipt_data.get('buyer_address', ""),
            'date': timezone.now()
        }
    )

    # Prepare context for rendering
    context = {
        'customer': customer,
        'receipt_data': receipt_data,
        'date': timezone.now(),
        'receipt': receipt,
        'created': created
    }

    return render(request, 'partials/customer_receipt.html', context)


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




def register_supplier_view(request):
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_suppliers')
    else:
        form = SupplierRegistrationForm()
    return render(request, 'partials/supplier_reg_form.html', {'form': form})


def list_suppliers_view(request):
    suppliers = Supplier.objects.all()  # Get all suppliers
    return render(request, 'partials/supplier_list.html', {'suppliers': suppliers})






@user_passes_test(is_admin)
@login_required
def add_procurement(request):
    ProcurementItemFormSet = modelformset_factory(
        ProcurementItem,
        form=ProcurementItemForm,
        extra=1,  # Allow at least one empty form to be displayed
        can_delete=True  # Allow deleting items dynamically
    )

    if request.method == 'POST':
        procurement_form = ProcurementForm(request.POST)
        formset = ProcurementItemFormSet(request.POST, queryset=ProcurementItem.objects.none())

        if procurement_form.is_valid() and formset.is_valid():
            procurement = procurement_form.save(commit=False)
            procurement.created_by = request.user  # Assuming the user is authenticated
            procurement.save()

            for form in formset:
                if form.cleaned_data.get('item_name'):  # Save only valid items
                    procurement_item = form.save(commit=False)
                    procurement_item.procurement = procurement
                    procurement_item.save()

            messages.success(request, "Procurement and items added successfully!")
            return redirect('procurement_list')  # Replace with your actual URL name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        procurement_form = ProcurementForm()
        formset = ProcurementItemFormSet(queryset=ProcurementItem.objects.none())

    return render(
        request,
        'partials/add_procurement.html',
        {
            'procurement_form': procurement_form,
            'formset': formset,
        }
    )



def procurement_form(request):
    # Create an empty formset for the items
    item_formset = ProcurementItemFormSet(queryset=ProcurementItem.objects.none())  # Replace with your model if needed

    # Get the empty form (form for the new item)
    new_form = item_formset.empty_form

    # Render the HTML for the new form
    return render(request, 'partials/procurement_form.html', {'form': new_form})


def procurement_list(request):
    procurements = (
        Procurement.objects.annotate(calculated_total=Sum('items__subtotal'))
        .order_by('-date')
    )
    return render(request, 'partials/procurement_list.html', {
        'procurements': procurements,
    })


@login_required
# def procurement_detail(request, procurement_id):
#     procurement = get_object_or_404(Procurement, id=procurement_id)
#     return render(request, 'partials/procurement_detail.html', {'procurement': procurement})
def procurement_detail(request, procurement_id):
    procurement = get_object_or_404(Procurement, id=procurement_id)

    # Calculate total from ProcurementItem objects
    total = procurement.items.aggregate(total=models.Sum('subtotal'))['total'] or 0

    return render(request, 'partials/procurement_detail.html', {
        'procurement': procurement,
        'total': total,
    })






