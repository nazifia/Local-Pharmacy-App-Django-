from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta, datetime
from decimal import Decimal
from app.models import *
from .forms import *
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
import uuid
from app.views import get_daily_sales, get_monthly_sales




# Admin check
def is_admin(user):
    return user.is_authenticated and user.is_superuser

def wholesale_page(request):
    return render(request, 'wholesale_page.html')

@login_required
def wholesales(request):
    if request.user.is_authenticated:
        items = Wholesale.objects.all().order_by('name')
        
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
        return render(request, 'wholesale/wholesales.html', context)
    else:
        return render(request, 'index.html')

@login_required
def search_wholesale_item(request):
    query = request.GET.get('search', '')
    items = Wholesale.objects.filter(name__icontains=query) if query else Wholesale.objects.all()
    return render(request, 'wholesale/wholesale_search.html', {'items': items})


@login_required
def add_to_wholesale(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = addWholesaleForm(request.POST or None)
            if form.is_valid():
                form.save()
                messages.success(request, 'Item added successfully')
                return redirect('wholesales')
        else:
            form = addWholesaleForm()
        return render(request, 'add_to_wholesale.html', {'form': form})
    else:
        return redirect('index')


@user_passes_test(is_admin)
def edit_wholesale_item(request, pk):
    if request.user.is_authenticated:
        item = get_object_or_404(Wholesale, id=pk)
        if request.method == 'POST':
            form = addWholesaleForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, f'{item.name} updated successfully')
                return redirect('wholesales')
        else:
            form = addWholesaleForm(instance=item)
        if request.headers.get('HX-Request'):
            return render(request, 'wholesale/edit_wholesale_item.html', {'form': form, 'item': item})
        else:
            return render(request, 'wholesale/wholesales.html')
    else:
        return redirect('index')



@login_required
def return_wholesale_item(request, pk):
    item = get_object_or_404(Wholesale, id=pk)

    if request.method == 'POST':
        form = ReturnWholesaleItemForm(request.POST)
        if form.is_valid():
            return_quantity = form.cleaned_data.get('return_item_quantity')

            # Validate the return quantity
            if return_quantity <= 0:
                messages.warning(request, 'Invalid return item quantity.')
                return redirect('wholesales')

            try:
                with transaction.atomic():
                    # Update item stock
                    item.stock_quantity += return_quantity
                    item.save()

                    # Find the sales item associated with the returned item
                    sales_item = WholesaleSalesItem.objects.filter(item=item).order_by('-quantity').first()
                    if not sales_item or sales_item.quantity < return_quantity:
                        messages.warning(request, f'No valid sales record found for {item.name}.')
                        return redirect('wholesales')

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
                    if sales.customer and hasattr(sales.customer, 'wholesale_customer_wallet'):
                        wallet = sales.customer.wholesale_customer_wallet
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
                    logs = DispensingLog.objects.filter(
                        user=sales.user, 
                        name=item.name, 
                        status__in=['Dispensed', 'Partially Returned']
                    ).order_by('created_at')

                    total_returned = return_quantity
                    for log in logs:
                        if total_returned <= 0:
                            break
                        if log.quantity <= total_returned:
                            total_returned -= log.quantity
                            log.delete()
                        else:
                            log.quantity -= total_returned
                            log.status = 'Partially Returned' if log.quantity > 0 else 'Returned'
                            log.save()
                            total_returned = 0

                    if total_returned > 0:
                        messages.warning(
                            request,
                            f"Some of the returned quantity could not be processed. Exceeds dispensed records."
                        )
                        return redirect('wholesales')



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
                        return render(request, 'app/dispensing_log.html', context)

                    messages.success(
                        request,
                        f'{return_quantity} of {item.name} successfully returned, sales and logs updated.'
                    )
                    return redirect('wholesales')

            except Exception as e:
                # Handle exceptions during atomic transaction
                print(f'Error during item return: {e}')
                messages.error(request, f'Error processing return: {e}')
                return redirect('wholesales')
        else:
            messages.warning(request, 'Invalid input. Please correct the form and try again.')

    else:
        # Display the return form in a modal or a page
        form = ReturnWholesaleItemForm()

    # Return appropriate response for HTMX or full-page requests
    if request.headers.get('HX-Request'):
        return render(request, 'wholesale/return_wholesale_item.html', {'form': form, 'item': item})
    else:
        return render(request, 'wholesale/wholesales.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def delete_wholesale_item(request, pk):
    if request.user.is_authenticated:
        item = get_object_or_404(Wholesale, id=pk)
        item.delete()
        messages.success(request, 'Item deleted successfully')
        return redirect('wholesales')
    else:
        return redirect('index')
    

@login_required
def dispense_wholesale(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = wholesaleDispenseForm(request.POST)
            if form.is_valid():
                q = form.cleaned_data['q']
                results = Wholesale.objects.filter(name__icontains=q)
        else:
            form = wholesaleDispenseForm()
            results = None
        return render(request, 'wholesale/wholesale_dispense_modal.html', {'form': form, 'results': results})
    else:
        return redirect('index')


from django.views.decorators.http import require_POST
@login_required
@require_POST
def add_to_wholesale_cart(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Wholesale, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        unit = request.POST.get('unit')

        if quantity <= 0:
            messages.warning(request, "Quantity must be greater than zero.")
            return redirect('cart')

        if quantity > item.stock_quantity:
            messages.warning(request, f"Not enough stock for {item.name}. Available stock: {item.stock_quantity}")
            return redirect('cart')

        # Add the item to the cart or update its quantity if it already exists
        cart_item, created = WholesaleCartItem.objects.get_or_create(
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
            cart_items = WholesaleCartItem.objects.all()
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
        return redirect('wholesale_cart')
    else:
        return redirect('index')



@transaction.atomic
@login_required
def select_wholesale_items(request, pk):
    customer = get_object_or_404(WholesaleCustomer, id=pk)
    items = Wholesale.objects.all().order_by('name')

    # Fetch wallet balance
    wallet_balance = Decimal('0.0')
    try:
        wallet_balance = customer.wholesale_customer_wallet.balance
    except WholesaleCustomerWallet.DoesNotExist:
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
            wholesale_customer=customer,
            defaults={'total_amount': Decimal('0.0')}
        )

        # Fetch or create a Receipt
        receipt, receipt_created = Receipt.objects.get_or_create(
            wholesale_customer=customer,
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
                item = Wholesale.objects.get(id=item_id)
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

                    # Update or create a WholesaleCartItem
                    cart_item, created = WholesaleCartItem.objects.get_or_create(
                        item=item,
                        defaults={'quantity': quantity, 'discount_amount': discount, 'unit': unit}
                    )
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.discount_amount += discount
                        cart_item.unit = unit
                    cart_item.save()

                    # Calculate subtotal and log dispensing
                    subtotal = (item.price * quantity) - discount
                    total_cost += subtotal
                    # DispensingLog.objects.create(
                    #     user=request.user,
                    #     name=item.name,
                    #     unit=unit,
                    #     quantity=quantity,
                    #     amount=subtotal,
                    #     status='Dispensed'
                    # )

                    # Update or create WholesaleSalesItem
                    sales_item, created = WholesaleSalesItem.objects.get_or_create(
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

                elif action == 'return':
                    # Handle return logic
                    item.stock_quantity += quantity
                    item.save()

                    try:
                        sales_item = WholesaleSalesItem.objects.get(sales=sales, item=item)

                        if sales_item.quantity < quantity:
                            messages.warning(request, f"Cannot return more {item.name} than purchased.")
                            return redirect('customer_list')

                        sales_item.quantity -= quantity
                        if sales_item.quantity == 0:
                            sales_item.delete()
                        else:
                            sales_item.save()

                        refund_amount = (item.price * quantity) - discount
                        sales.total_amount -= refund_amount
                        sales.save()

                        DispensingLog.objects.create(
                            user=request.user,
                            name=item.name,
                            unit=unit,
                            quantity=quantity,
                            amount=refund_amount,
                            status='Partially Returned' if sales_item.quantity > 0 else 'Returned'  # Status based on remaining quantity
                        )

                        total_cost -= refund_amount

                        # Update the receipt
                        receipt.total_amount -= refund_amount
                        receipt.save()

                    except WholesaleCartItem.DoesNotExist:
                        messages.warning(request, f"Item {item.name} is not part of the sales.")
                        return redirect('select_wholesale_items', pk=pk)

            except Wholesale.DoesNotExist:
                messages.warning(request, 'One of the selected items does not exist.')
                return redirect('select_wholesale_items', pk=pk)

        # Update customer's wallet balance
        try:
            wallet = customer.wholesale_customer_wallet
            if action == 'purchase':
                wallet.balance -= total_cost
            elif action == 'return':
                wallet.balance += abs(total_cost)
            wallet.save()
        except WholesaleCustomerWallet.DoesNotExist:
            messages.warning(request, 'Customer does not have a wallet.')
            return redirect('select_wholesale_items', pk=pk)

        action_message = 'added to cart' if action == 'purchase' else 'returned successfully'
        messages.success(request, f'Action completed: Items {action_message}.')
        return redirect('wholesale_cart')

    return render(request, 'wholesale/select_wholesale_items.html', {
        'customer': customer,
        'items': items,
        'wallet_balance': wallet_balance
    })






@login_required
def wholesale_cart(request):
    if request.user.is_authenticated:
        cart_items = WholesaleCartItem.objects.select_related('item').all()
        total_price, total_discount = 0, 0

        if request.method == 'POST':
            # Process each discount form submission
            for cart_item in cart_items:
                # Fetch the discount amount using cart_item.id in the input name
                discount = int(request.POST.get(f'discount_amount-{cart_item.id}', 0))
                cart_item.discount_amount = max(discount, 0)
                cart_item.save()

        # Calculate totals
        for cart_item in cart_items:
            cart_item.subtotal = cart_item.item.price * cart_item.quantity
            total_price += cart_item.subtotal
            total_discount += cart_item.discount_amount
        
        final_total = total_price - total_discount

        total_discounted_price = total_price - total_discount
        return render(request, 'wholesale/wholesale_cart.html', {
            'cart_items': cart_items,
            'total_discount': total_discount,
            'total_price': total_price,
            'total_discounted_price': total_discounted_price,
            'final_total': final_total,
        })
    else:
        return redirect('index')



@login_required
def update_wholesale_cart_quantity(request, pk):
    cart_item = get_object_or_404(WholesaleCartItem, id=pk)
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

    return redirect('wholesale_cart')





@login_required
def clear_wholesale_cart(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cart_items = WholesaleCartItem.objects.all()

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

                    # Reverse sales entry
                    sales_entry = Sales.objects.filter(
                        user=request.user,
                        total_amount=cart_item.item.price * cart_item.quantity
                    ).first()  # Replace with the correct field for items

                    if sales_entry:
                        if sales_entry.customer:
                            wallet = sales_entry.customer.wallet
                            wallet.balance += cart_item.item.price * cart_item.quantity
                            wallet.save()

                        if sales_entry.wholesale_customer:
                            wholesale_wallet = sales_entry.wholesale_customer.wholesale_customer_wallet
                            wholesale_wallet.balance += cart_item.item.price * cart_item.quantity
                            wholesale_wallet.save()

                        # Delete sales entry
                        sales_entry.delete()

                # Clear cart items
                cart_items.delete()
                messages.success(request, 'Cart cleared, items returned to stock, and wallet transactions reversed.')

        except Exception as e:
            messages.warning(request, f"An error occurred: {e}")
            print(f"Error during clear_wholesale_cart: {e}")

    return redirect('wholesale_cart')




@transaction.atomic
@login_required
def wholesale_receipt(request):
    buyer_name = request.POST.get('buyer_name', '')
    buyer_address = request.POST.get('buyer_address', '')

    # Retrieve cart items
    cart_items = WholesaleCartItem.objects.all()
    if not cart_items.exists():
        messages.warning(request, "No items in the cart.")
        return redirect('wholesale_cart')

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
        messages.warning(request, "An error occurred while processing the receipt.")
        return redirect('wholesale_cart')

    # Process cart items
    for cart_item in cart_items:
        WholesaleSalesItem.objects.get_or_create(
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

    sales_items = sales.wholesale_sales_items.all()
    
    payment_methods = ["Cash", "Wallet", "Transfer"]
    # receipt = get_object_or_404(Receipt, id=request.session.get('receipt_id'))  # Example
    
    return render(request, 'wholesale/wholesale_receipt.html', {
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





def wholesale_receipt_list(request):
    receipts = Receipt.objects.all().order_by('-date')  # Only wholesale receipts
    return render(request, 'wholesale/wholesale_receipt_list.html', {'receipts': receipts})



@login_required
def wholesale_receipt_detail(request, receipt_id):
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
        return redirect('wholesale_receipt_detail', receipt_id=receipt.receipt_id)

    # Retrieve sales and sales items linked to the receipt
    sales = receipt.sales
    sales_items = sales.wholesale_sales_items.all() if sales else []

    # Calculate totals for the receipt
    total_price = sum(item.subtotal for item in sales_items)
    total_discount = Decimal('0.0')  # Modify if a discount amount is present in `Receipt`
    total_discounted_price = total_price - total_discount

    # Update and save the receipt with calculated totals
    receipt.total_amount = total_discounted_price
    receipt.total_discount = total_discount
    receipt.save()

    return render(request, 'wholesale/wholesale_receipt_detail.html', {
        'receipt': receipt,
        'sales_items': sales_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_discounted_price': total_discounted_price,
    })




@login_required
def exp_date_alert(request):
    alert_threshold = timezone.now() + timedelta(days=90)
    expiring_items = Wholesale.objects.filter(exp_date__lte=alert_threshold, exp_date__gt=timezone.now())
    expired_items = Wholesale.objects.filter(exp_date__lt=timezone.now())

    for expired_item in expired_items:
        if expired_item.stock_quantity > 0:
            expired_item.stock_quantity = 0
            expired_item.save()

    return render(request, 'partials/exp_date_alert.html', {
        'expired_items': expired_items,
        'expiring_items': expiring_items,
    })



@login_required
def register_wholesale_customers(request):
    if request.method == 'POST':
        form = WholesaleCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer successfully registered')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': True, 'message': 'Registration successful'})
            return redirect('wholesale_customers')
    else:
        form = WholesaleCustomerForm()
    if request.headers.get('HX-Request'):
        return render(request, 'wholesale/register_wholesale_customers.html', {'form': form})
    return render(request, 'register_wholesale_customers.html', {'form': form})


def wholesale_customers(request):
    customers = WholesaleCustomer.objects.all().order_by('name')  # Order by customer name in ascending order
    return render(request, 'wholesale/wholesale_customers.html', {'customers': customers})



@login_required
def edit_wholesale_customer(request, pk):
    customer = get_object_or_404(WholesaleCustomer, id=pk)
    if request.method == 'POST':
        form = WholesaleCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'{customer.name} edited successfully.')
            return redirect('wholesale_customers')
        else:
            messages.warning(request, f'{customer.name} failed to edit, please try again')
    else:
        form = WholesaleCustomerForm(instance=customer)
    if request.headers.get('HX-Request'):
        return render(request, 'wholesale/edit_wholesale_customer.html', {'form': form, 'customer': customer})
    else:
        return render(request, 'wholesale_page.html')



@login_required
@user_passes_test(is_admin)
def delete_wholesale_customer(request, pk):
    customer = get_object_or_404(WholesaleCustomer, pk=pk)
    customer.delete()
    messages.success(request, 'Customer deleted successfully.')
    return redirect('wholesale_customers')



@login_required
def wholesale_customer_add_funds(request, pk):
    customer = get_object_or_404(WholesaleCustomer, pk=pk)
    
    # Get or create the wholesale customer's wallet
    wallet, created = WholesaleCustomerWallet.objects.get_or_create(customer=customer)
    
    if request.method == 'POST':
        form = WholesaleCustomerAddFundsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            wallet.add_funds(amount)
            messages.success(request, f'Funds successfully added to {wallet.customer.name}\'s wallet.')
            return redirect('wholesale_customers')
        else:
            messages.error(request, 'Error adding funds')
    else:
        form = WholesaleCustomerAddFundsForm()
    
    return render(request, 'wholesale/wholesale_customer_add_funds_modal.html', {'form': form, 'customer': customer})



@login_required
def wholesale_customer_wallet_details(request, pk):
    customer = get_object_or_404(WholesaleCustomer, pk=pk)
    
    # Check if the customer has a wallet; create one if it doesn't exist
    wallet, created = WholesaleCustomerWallet.objects.get_or_create(customer=customer)
    
    return render(request, 'wholesale/wholesale_customer_wallet_details.html', {
        'customer': customer,
        'wallet': wallet
    })




@login_required
@user_passes_test(is_admin)
def reset_wholesale_customer_wallet(request, pk):
    wallet = get_object_or_404(WholesaleCustomerWallet, pk=pk)
    wallet.balance = 0
    wallet.save()
    messages.success(request, f'{wallet.customer.name}\'s wallet cleared successfully.')
    return redirect('wholesale_customers')







def wholesale_transactions(request, customer_id):
    # Get the wholesale customer
    customer = get_object_or_404(WholesaleCustomer, id=customer_id)
    
    # Get the wholesale customer's wallet
    wallet = getattr(customer, 'wholesale_customer_wallet', None)
    wallet_balance = wallet.balance if wallet else 0.00  # Set to 0.00 if wallet does not exist

    # Filter sales where customer is None, since wholesale sales may not be linked to Customer
    wholesale_sales = Sales.objects.filter(customer=None).prefetch_related('sales_items__item').order_by('-date')
    
    # Pass wallet balance to the template
    return render(request, 'wholesale/wholesale_transactions.html', {
        'customer': customer,
        'sales': wholesale_sales,
        'wallet_balance': wallet_balance,
    })




