from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from products.models import Product
# Create your views here.
def home_view(request:HttpRequest):
  products = Product.objects.all()[0:4]
  return render(request, "main/index.html", {'products':products})