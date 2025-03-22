from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
  class RatingChoices(models.IntegerChoices):
     START1 = 1, "One Start"
     START2 = 2, "Two Stars"
     START3 = 3, "Three Stars"
     START4 = 4, "Four Stars"
     START5 = 5, "Five Stars"
  name = models.CharField(max_length=255)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  group_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # إضافة حقل group_price
  description = models.TextField()
  image = models.ImageField(upload_to="images/", default="images/default.jpg")
  category = models.CharField(max_length=225)
  brand = models.CharField(max_length=225)
  colour = models.CharField(max_length=225)
  size = models.CharField(max_length=225)
  quantity = models.IntegerField()
  rating = models.SmallIntegerField(choices=RatingChoices.choices)

  

class Review(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  rating = models.SmallIntegerField()
  comment = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} on {self.product.name}"
