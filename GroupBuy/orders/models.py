from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from decimal import Decimal
class GroupPurchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='group_purchases', blank=True)
    is_active = models.BooleanField(default=True)  # حالة الشراء الجماعي (مفتوح أو مغلق)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # السعر الكلي بعد الخصم
    def calculate_total_price(self):
        """حساب السعر الكلي بناءً على عدد المشاركين والسعر المخفض"""
        price_per_product = self.product.group_price if self.product.group_price else self.product.price
        return self.participants.count() * price_per_product

    def add_participant(self, user):
        """إضافة مستخدم إلى المشاركين"""
        if self.is_active and user not in self.participants.all():
            self.participants.add(user)
            self.total_price = self.calculate_total_price()
            super().save()

    def close_purchase(self):
        """إغلاق الشراء الجماعي عند الوصول إلى العدد المطلوب من المشاركين"""
        if self.participants.count() >= self.product.min_participants:
            self.is_active = False
            super().save()

    def __str__(self):
        return f"Group purchase for {self.product.name}, {self.participants.count()} participants"

    #ef save(self, *args, **kwargs):
    #  """حساب السعر الكلي عند الحفظ"""
    #  #self.total_price = self.product.group_price * self.participants
    #  if self.product.group_price:
    #      self.total_price = self.product.group_price * self.participants
    #  else:
    #      self.total_price = self.product.price * self.participants
#
    #  super().save(*args, **kwargs)
#
    #ef add_participant(self, user):
    #  """إضافة مشارك إلى الشراء الجماعي"""
    #  if self.is_active:
    #      self.participants += 1
    #      #self.total_price = self.product.group_price * self.participants
    #      self.total_price += self.product.group_price
    #      self.save()
#
#
    #ef close_purchase(self):
    #   """إغلاق الشراء الجماعي عند الوصول إلى العدد المطلوب من المشاركين"""
    #   if self.participants >= self.product.min_participants:
    #       self.is_active = False
    #       #self.total_price = self.product.group_price * self.participants
    #       self.save()

    #ef __str__(self):
    #   return f"Group purchase for {self.product.name}, {self.participants} participants"
#
## Create your models here.
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
            # استخدام سعر الخصم (group_price) مباشرةً لحساب السعر الإجمالي
            if self.product.group_price:
                price = self.product.group_price
            else:
                price = self.product.price

            self.total_price = self.quantity * price
        else:
            # الطلب الفردي بالسعر العادي
            self.total_price = self.quantity * self.product.price

        super().save(*args, **kwargs)

    #def save(self, *args, **kwargs):
    #    if self.order_type == self.OrderType.GROUP:
    #        # إذا كان هناك سعر جماعي
    #        if self.product.group_price and self.participants >= 2:  # الحد الأدنى للمشاركين
    #            price = self.product.group_price if self.product.group_price is not None else self.product.price
    #        else:
    #            price = self.product.price if self.product.price is not None else 0  # تعيين السعر الافتراضي في حالة عدم وجود سعر
    #        
    #        # حساب السعر الإجمالي
    #        self.total_price = self.quantity * price
    #    else:
    #        # طلب فردي بالسعر العادي
    #        self.total_price = self.quantity * self.product.price if self.product.price is not None else 0  # تعيين السعر الافتراضي في حالة عدم وجود سعر
    #
    #    super().save(*args, **kwargs)

# test2
