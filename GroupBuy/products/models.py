from django.db import models
from django.contrib.auth.models import User





class Product(models.Model):
  class CategoryChoices(models.TextChoices):
    MAKEUP = "Makeup", "Makeup"
    PERFUMES = "Perfumes", "Perfumes"
    SKINCARE = "Skincare", "Skincare "
    HAIRCARE = "Haircare", "Haircare"
    ELECTRONICS = "Electronics", "Electronics"


  seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
  name = models.CharField(max_length=255)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  group_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
  min_participants = models.PositiveIntegerField(default=2) 
  max_participants = models.PositiveIntegerField(default=5)  
  description = models.TextField()
  image = models.ImageField(upload_to="images/", default="images/default.jpg")
  category = models.CharField(max_length=250, choices=CategoryChoices.choices)
  brand = models.CharField(max_length=225)
  colour = models.CharField(max_length=225)
  size = models.CharField(max_length=225)
  quantity = models.IntegerField()
  favorited_by = models.ManyToManyField(User, related_name='favorite_products', blank=True)


  

class Review(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  rating = models.SmallIntegerField()
  comment = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} on {self.product.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def total_price(self):
        return self.product.price * self.quantity

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem, blank=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
