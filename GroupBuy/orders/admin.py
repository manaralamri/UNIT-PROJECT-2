from django.contrib import admin
from .models import Order, GroupPurchase, PaymentTest
# Register your models here.
admin.site.register(Order)
admin.site.register(GroupPurchase)
admin.site.register(PaymentTest)