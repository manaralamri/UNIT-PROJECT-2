from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Product, Review
from .forms import ProductForm
from accounts.models import Profile_Seller
from django.contrib import messages
from orders.forms import OrderForm


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
      product_form.save()
      return redirect('main:home_view')
    else:
      return HttpResponse("Invalid form")

  return render(request, 'products/create_product.html', {'product_form':product_form})

def all_product_view(request:HttpRequest):
  # Get all products
  products = Product.objects.all()
  return render(request, 'products/all_products.html', {'products':products})

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
           # هنا يمكنك عمل إعادة توجيه أو عرض رسالة نجاح.


  return render(request, 'products/product_detail.html', {"product":product, 'reviews':reviews, 'form':form})

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