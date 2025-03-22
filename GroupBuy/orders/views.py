from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import Order
from .forms import OrderForm
from products.models import Product
# Create your views here.
#def create_order_view(request:HttpRequest, product_id: int):
#    product = Product.objects.get(id=product_id)
#    if request.method == "POST":
#        quantity = int(request.POST['quantity'])
#        order = Order(user=request.user, product=product, quantity=quantity)
#        order.save()
#        #return redirect('orders:order_list_view')  
#    return render(request, 'orders/create_order.html', {'product': product})
def create_order_view(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.product = product
            order.save()
            #return redirect('order_success')  # أو أي صفحة أخرى
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form, 'product': product})
