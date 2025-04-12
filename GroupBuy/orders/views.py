
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpRequest, HttpResponse, Http404
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache
from .models import Product, GroupPurchase, Order
from .forms import OrderForm, TestPaymentForm
from accounts.models import Profile_User, Profile_Seller
from django.core.mail import send_mail
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max
from collections import defaultdict


def check_group_purchase_availability(group_purchase, product):
    """Make sure the group buying room is still open and available.."""
    cache_key = f"group_purchase_{group_purchase.id}_availability"
    is_available = cache.get(cache_key)
    
    if is_available is None:
        is_available = product.quantity > 0 and group_purchase.participants.count() < product.max_participants
        cache.set(cache_key, is_available, timeout=60) 
    
    if not is_available:
        group_purchase.is_active = False
        group_purchase.save()
    
    return is_available



def create_order_view(request, product_id):
    """
    Handle creation of an individual order for a product.
    Validates:
    - User is authenticated.
    - User has a user profile.
    - Product exists and is in stock.
    """

    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to your cart.", "alert-danger")
        return redirect("accounts:sign_in")
    

    # Ensure only registered users with a Profile_User can order
    if not Profile_User.objects.filter(user=request.user).exists():
          messages.error(request, "Only User can order.", "alert-danger")
          return redirect('main:home_view')
    

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.", "alert-danger")


    # Check product availability
    if product.quantity <= 0:
        messages.error(request, "Sorry, the product is out of stock", "alert-danger")
        return redirect('products:product_detail_view', product_id=product.id)


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.product = product
                    order.order_type = Order.OrderType.INDIVIDUAL
                    order.participants = 1
                    order.save()
                    messages.success(request, "Individual order created successfully!" , "alert-success")
                    return redirect('orders:test_payment_view', order_id=order.id)
                
            except Exception as e:
                messages.error(request, "An error occurred while creating the request", "alert-danger")
                print(e)


        else:
            messages.error(request, "Please fix the errors in the form.", "alert-danger")
    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form, 'product': product})



def create_group_purchase(request, product_id):
    """
    Allows a user to create a group purchase room for a product,
    if conditions are met:
    - User is authenticated
    - User has a valid profile
    - Product exists and has enough quantity
    """

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to your cart.", "alert-danger")
        return redirect("accounts:sign_in")

    if not Profile_User.objects.filter(user=request.user).exists():
          messages.error(request, "Only User can order for group.", "alert-danger")
          return redirect('main:home_view')
    try:
        product = Product.objects.get(id=product_id)

    except  Exception as e :
        messages.error(request, "The product does not exist.", "alert-danger")
        return redirect('products:product_list_view')

    # Check stock levels
    if product.quantity <= 0:
        messages.error(request, "Unable to create a group purchase room. The product is out of stock in Database", "alert-danger")
        return redirect('products:product_detail_view', product_id=product.id)
    

    if product.quantity <= 1:
        messages.warning(request, "Group room cannot be created, only one product left.", "alert-warning")
        return redirect('products:product_detail_view', product_id=product.id)
    

    if request.method == 'POST':
        is_private = request.POST.get('is_private') == 'on'
        try:
            with transaction.atomic():
                # Final check before creating group room
                if product.quantity > 0:
                    group_purchase = GroupPurchase.objects.create(
                        product=product,
                        is_private=is_private
                        )
    
                    messages.success(request, "Group purchase room created successfully!", "alert-success")
    
                    group_purchase_link = request.build_absolute_uri(
                        reverse('orders:group_purchase_detail', args=[group_purchase.id])
                    )
    
                    return render(request, 'orders/group_purchase_detail.html', {
                        'group_purchase': group_purchase,
                        'group_purchase_link': group_purchase_link,
                    })
                else:
                    messages.error(request, "Insufficient quantity to create a group purchase room.", "alert-danger")
                    return redirect('products:product_detail_view', product_id=product.id)
                

        except Exception as e:
            messages.error(request, "An unexpected error occurred while creating the group purchase.", "alert-danger")
            return redirect('products:product_detail_view', product_id=product.id)

    return render(request, 'orders/create_group_purchase.html', {'product': product})


def join_group_purchase(request, group_purchase_id):
    """
    Allows a user to join an existing group purchase room if:
    - The group and product exist
    - The user is not already in the group
    - There's availability (quantity + max participants)
    """
    try:
        group_purchase = GroupPurchase.objects.get(id=group_purchase_id)
        product = group_purchase.product

    except ObjectDoesNotExist:
        messages.error(request, "The group purchase or product does not exist.", "alert-danger")
        return redirect('main:home_view')

    if product.group_price is None:
        messages.error(request, "This product does not have a group price set. Please contact the administrator.", "alert-danger")
        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)
    

    if not check_group_purchase_availability(group_purchase, product):
        messages.error(request, "Sorry,this product is unavailable or the group is full.", "alert-danger")
        return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)

    if request.user.is_authenticated:
        if request.user in group_purchase.participants.all():
            messages.warning(request, "You are already a participant in this group purchase!", "alert-warning")
        else:
            with transaction.atomic():
                group_purchase.add_participant(request.user)
                product.quantity -= 1
                product.save()

                group_price = product.group_price if product.group_price else Decimal('0.00')

                if group_price == Decimal('0.00'):
                    messages.error(request, "This product does not have a valid price set. Please contact the administrator.", "alert-danger")
                    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)

                order = Order.objects.create(
                    user=request.user,
                    product=product,
                    group_purchase=group_purchase,
                    quantity=1,  
                    total_price=product.group_price if product.group_price else product.price,  

                )

                messages.success(request, "You have successfully joined the group purchase!", "alert-success")

            if group_purchase.participants.count() >= product.max_participants or product.quantity <= 0:
                group_purchase.is_active = False
                group_purchase.save()

                subject = f"Group Purchase Completed: {product.name}"
                message = f"The group purchase for '{product.name}' is now complete. Thank you for joining!"
                from_email = 'noreply@yourwebsite.com'
                recipient_list = [user.email for user in group_purchase.participants.all() if user.email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return redirect('orders:test_payment_view', order_id=order.id)


    else:
        messages.error(request, "You must be logged in to participate in group buying", "alert-danger")

    return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)


def group_purchase_detail(request, group_purchase_id):
    """View group room details"""
    group_purchase = GroupPurchase.objects.get(id=group_purchase_id)
    group_purchase.save()

    return render(request, 'orders/group_purchase_detail.html', {'group_purchase': group_purchase})


def group_purchase_all(request):
    """View group room list"""
    group_purchases = GroupPurchase.objects.select_related('product').filter(is_private=False).order_by('-id')
    return render(request, 'orders/group_purchase_all.html', {'group_purchases': group_purchases})



def existing_group_choices(request, product_id):
    #Trying to get the product using the identifier (product_id) from the database
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.", "alert-danger")
        return redirect('products:all_product_view')

    open_group = GroupPurchase.objects.filter(product=product, is_active=True).first()

    return render(request, 'orders/existing_group_choices.html', {
        'product': product,
        'open_group': open_group, 
    })

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})
 


def user_orders_view(request):
    try:
        orders = Order.objects.filter(user=request.user).select_related('product')

        grouped_orders = defaultdict(lambda: defaultdict(list))
        for order in orders:
            grouped_orders[order.product][order.order_type].append(order)

        product_orders = []
        for product, order_types in grouped_orders.items():
            for order_type, orders_list in order_types.items():
                product_orders.append({
                    'product': product,
                    'order_type': order_type,  
                    'count': len(orders_list),
                    'last_order': sorted(orders_list, key=lambda x: x.created_at)[-1],
                })

        return render(request, 'orders/user_orders.html', {
            'orders_grouped': product_orders,
        })

    except Exception as e:
        messages.error(request, 'An error occurred while retrieving your requests.', 'alert-danger')
        return redirect('main:home_view')


def test_payment_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "The order does not exist.", "alert-danger")
        return redirect('main:home_view')
    
    group_purchase = order.group_purchase  
    product = order.product
    quantity = order.quantity

    if group_purchase:
        total_price = product.group_price if product.group_price else product.price
        total_price *= quantity

        if request.method == 'POST':
            form = TestPaymentForm(request.POST)
            if form.is_valid():
                test_payment = form.save(commit=False)
                test_payment.user = request.user if request.user.is_authenticated else None
                test_payment.order = order
                test_payment.group_purchase = group_purchase  
                test_payment.save()
                messages.success(request, "Thank you! This was a test payment experience. ✅", "alert-success")
                return redirect('orders:group_purchase_detail', group_purchase_id=group_purchase.id)

        else:
            form = TestPaymentForm()

        return render(request, 'orders/test_payment.html', {
            'form': form,
            'order': order,
            'product': product,
            'group_purchase': group_purchase,
            'total_price': total_price,  
        })
    
    else:
        total_price = product.price * quantity

        if request.method == 'POST':
            form = TestPaymentForm(request.POST)
            if form.is_valid():
                test_payment = form.save(commit=False)
                test_payment.user = request.user if request.user.is_authenticated else None
                test_payment.order = order
                test_payment.save()
                messages.success(request, "Thank you! This was a test payment experience. ✅", "alert-success")
                return redirect('orders:order_detail', order_id=order.id)

        else:
            form = TestPaymentForm()

        return render(request, 'orders/test_payment.html', {
            'form': form,
            'order': order,
            'product': product,
            'total_price': total_price  
        })



