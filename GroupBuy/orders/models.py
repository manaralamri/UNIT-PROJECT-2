from django.db import models
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from django.contrib.auth.models import User
from decimal import Decimal
class GroupPurchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='group_purchases', blank=True)
    is_active = models.BooleanField(default=True)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  
    expiration_time = models.DateTimeField(blank=True, null=True, default=(timezone.now() + timedelta(seconds=15)))

    def calculate_total_price(self):
        price_per_product = self.product.group_price if self.product.group_price else self.product.price
        return self.participants.count() * price_per_product

    def add_participant(self, user):
        if self.is_active and user not in self.participants.all():
            self.participants.add(user)
            self.total_price = self.calculate_total_price()
            super().save()

    def close_purchase(self):
        if self.participants.count() >= self.product.min_participants:
            self.is_active = False
            super().save()
    def is_expired(self):
        return timezone.now() > self.expiration_time if self.expiration_time else False

    def __str__(self):
        return f"Group purchase for {self.product.name}, {self.participants.count()} participants"

class Order(models.Model):
    class OrderType(models.TextChoices):
      INDIVIDUAL = 'individual', 'individual'
      GROUP = 'group', 'group'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    group_purchase = models.ForeignKey(GroupPurchase, on_delete=models.SET_NULL, null=True, blank=True)  # إضافة ارتباط بالشراء الجماعي
    participants = models.PositiveIntegerField(default=1)  
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if self.order_type == self.OrderType.GROUP:
            if self.product.group_price:
                price = self.product.group_price
            else:
                price = self.product.price

            self.total_price = self.quantity * price
        else:
            self.total_price = self.quantity * self.product.price

        super().save(*args, **kwargs)



#lass PaymentTest(models.Model):
#   name = models.CharField(max_length=250)
#   email = models.EmailField()
#   address = models.CharField(max_length=250, blank=True)
#   postal_code = models.CharField(max_length=10, blank=True)
#   phone_number = models.CharField(max_length=20, blank=True)
#   city = models.CharField(max_length=250, blank=True)
