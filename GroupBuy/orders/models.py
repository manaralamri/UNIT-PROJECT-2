from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.
class Order(models.Model):
    class OrderType(models.TextChoices):
      INDIVIDUAL = 'individual', 'individual'
      GROUP = 'group', 'group'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    participants = models.PositiveIntegerField(default=1)  
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.order_type == self.OrderType.GROUP:
            price = self.product.group_price if self.product.group_price else self.product.price

            # تطبيق خصم إذا كان عدد المشاركين أكبر من 2 (مثال)
            if self.participants > 2:
                discount = Decimal('0.1')
                self.total_price = self.quantity * price * self.participants * (1 - discount)
            else:
                self.total_price = self.quantity * price * self.participants
        else:
            self.total_price = self.quantity * self.product.price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.product.name} ({self.order_type})"


    #def save(self, *args, **kwargs):
    #    if self.order_type == self.OrderType.GROUP:
    #        if self.product.group_price: 
    #            self.total_price = self.quantity * self.product.group_price * self.participants
    #        else:
    #            self.total_price = self.quantity * self.product.price
    #    else:
    #        self.total_price = self.quantity * self.product.price
    #    super().save(*args, **kwargs)
#
    #    
    #def __str__(self):
    #    return f"Order {self.id} - {self.product.name} ({self.order_type})"
#



