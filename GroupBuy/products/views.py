from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from .models import Product, Review, Cart, CartItem
from .forms import ProductForm
from accounts.models import Profile_Seller
from django.contrib import messages
from orders.forms import OrderForm
from django.db.models import Avg
from django.db import transaction

def create_product_view(request:HttpRequest):
  # Create a new product
  if not request.user.is_authenticated:
      messages.error(request, "You must be logged in to add products.", "alert-danger")
      return redirect('accounts:sign_in')
  
  if not Profile_Seller.objects.filter(user=request.user).exists():
      messages.error(request, "Only sellers can add products.", "alert-danger")
      return redirect('main:home_view')


  product_form = ProductForm()
  if request.method == 'POST':
    product_form = ProductForm(request.POST, request.FILES)
    if product_form.is_valid():
      product = product_form.save(commit=False)  # لا يتم الحفظ مباشرة
      product.seller = request.user  # تعيين البائع
      product_form.save()
      return redirect('main:home_view')
    else:
      print(product_form.errors)
      return HttpResponse("Invalid form")

  return render(request, 'products/create_product.html', {'product_form':product_form})

def all_product_view(request:HttpRequest):
  # Get all products
  products = Product.objects.all()


  return render(request, 'products/all_products.html', {'products':products,})

def product_detail_view(request:HttpRequest, product_id:int):
  # Get product by id
  product = Product.objects.get(id=product_id)
  reviews = Review.objects.filter(product=product)
  form = OrderForm(request.POST or None)

  if form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.product = product
        order.save()
  avg = reviews.aggregate(Avg("rating"))
  print(avg)
   

  return render(request, 'products/product_detail.html', {"product":product, 'reviews':reviews, 'form':form, "average_rating":avg["rating__avg"]})

def product_update_view(request:HttpRequest, product_id:int):
  if not request.user.is_authenticated:
      messages.error(request, "You must be logged in to update products.", "alert-danger")
      return redirect('accounts:sign_in')
  if not Profile_Seller.objects.filter(user=request.user).exists():
      messages.error(request, "Only sellers can update products.", "alert-danger")
      return redirect('main:home_view')


  # Get product by id

  product = Product.objects.get(id=product_id)

  if request.method == "POST":
    product.name = request.POST['name']
    product.price = request.POST['price']
    product.description = request.POST['description']
    product.category = request.POST['category']
    product.brand = request.POST['brand']
    product.colour = request.POST['colour']
    product.size = request.POST['size']
    product.quantity = request.POST['quantity']
    if "image" in request.FILES:
      product.image = request.FILES['image']
    product.save()
    return redirect('products:product_detail_view', product_id=product.id)
  return render(request, 'products/product_update.html', {'product':product})


def product_delete_view(request:HttpRequest, product_id:int):
  if not request.user.is_authenticated:
    messages.error(request, "You must be logged in to delete products.", "alert-danger")
    return redirect('accounts:sign_in')
  if not Profile_Seller.objects.filter(user=request.user).exists():
      messages.error(request, "Only sellers can delete products.", "alert-danger")
      return redirect('main:home_view')

  # Delete product by id
  product = Product.objects.get(pk=product_id)
  product.delete()
  return redirect("main:home_view")


def add_review_view(request:HttpRequest, product_id):
   if not request.user.is_authenticated:
      messages.error(request, "Only registered user can add review", "alert-danger")
      return redirect("accounts:sign_in")
   if request.method == 'POST':
      product_object = Product.objects.get(pk=product_id)
      new_review = Review(product=product_object,user=request.user, comment=request.POST['comment'], rating=request.POST['rating'])
      new_review.save()
      messages.success(request,"Add Review Successfully", "alert-success")
   return redirect('products:product_detail_view', product_id=product_id)





def toggle_favorite_view(request: HttpRequest, product_id: int):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to manage favorites.", "alert-danger")
        return redirect("accounts:sign_in")

    try:
        product = Product.objects.get(id=product_id)

        if product.favorited_by.filter(id=request.user.id).exists():
            product.favorited_by.remove(request.user)
            messages.warning(request, "Product removed from favorites.", "alert-warning")
        else:
            product.favorited_by.add(request.user)
            messages.success(request, "Product added to favorites.", "alert-success")

    except Product.DoesNotExist:
        messages.error(request, "Product not found.", "alert-danger")

    except Exception as e:
        print(e)

    return redirect("products:product_detail_view", product_id=product.id)

def favorite_products_view(request: HttpRequest):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your favorites.", "alert-danger")
        return redirect("accounts:sign_in")

    try:
        favorite_products = request.user.favorite_products.all()
    except Exception as e:
        print(e)
        favorite_products = []

    return render(request, "products/favorite_products.html", {"favorite_products": favorite_products})




def cart_view(request: HttpRequest):
    """عرض محتويات السلة للمستخدم."""
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your cart.", "alert-danger")
        return redirect("accounts:sign_in")

    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart/cart_view.html", {"cart": cart})

def add_to_cart_view(request: HttpRequest, product_id: int):
    """إضافة منتج إلى السلة، وزيادة الكمية إذا كان موجودًا بالفعل."""
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to your cart.", "alert-danger")
        return redirect("accounts:sign_in")

    try:
        with transaction.atomic():  # بدء معاملة قاعدة البيانات
            product = get_object_or_404(Product, id=product_id)
            if product.quantity == 0:
                messages.warning(request, "Sorry, this product is currently out of stock.", "alert-warning")
                return redirect("products:product_detail_view", product_id=product.id)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            cart.items.add(cart_item)
            messages.success(request, "Product added to cart.", "alert-success")

    except Exception as e:
        print(e)
        messages.error(request, "An error occurred while adding the product.", "alert-danger")

    return redirect("products:cart_view")

def remove_from_cart_view(request: HttpRequest, product_id: int):
    """إزالة منتج من السلة."""
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to manage your cart.", "alert-danger")
        return redirect("accounts:sign_in")

    try:
        with transaction.atomic():
            product = get_object_or_404(Product, id=product_id)
            cart = get_object_or_404(Cart, user=request.user)
            cart_item = get_object_or_404(CartItem, user=request.user, product=product)

            cart.items.remove(cart_item)
            cart_item.delete()
            messages.warning(request, "Product removed from cart.", "alert-warning")

    except Exception as e:
        print(e)
        messages.error(request, "An error occurred while removing the product.", "alert-danger")

    return redirect("products:cart_view")

def increase_cart_quantity_view(request: HttpRequest, product_id: int):
    """زيادة كمية منتج في السلة."""
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to modify your cart.", "alert-danger")
        return redirect("accounts:sign_in")

    try:
        with transaction.atomic():
            cart = get_object_or_404(Cart, user=request.user)
            item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

            item.quantity += 1
            item.save()
            messages.success(request, "Product quantity increased.", "alert-success")

    except Exception as e:
        print(e)
        messages.error(request, "An error occurred while updating quantity.", "alert-danger")

    return redirect("products:cart_view")

def decrease_cart_quantity_view(request: HttpRequest, product_id: int):
    """تقليل كمية منتج في السلة أو حذفه إذا وصلت الكمية إلى 1."""
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to modify your cart.", "alert-danger")
        return redirect("accounts:sign_in")

    try:
        with transaction.atomic():
            cart = get_object_or_404(Cart, user=request.user)
            item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                messages.info(request, "Product quantity decreased.", "alert-info")
            else:
                item.delete()
                messages.warning(request, "Product removed from cart.", "alert-warning")

    except Exception as e:
        print(e)
        messages.error(request, "An error occurred while updating quantity.", "alert-danger")

    return redirect("products:cart_view")
