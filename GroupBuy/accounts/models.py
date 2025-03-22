from django.db import models
from django.contrib.auth.models import User





# Create your models here.
class Profile_User(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  avatar = models.ImageField(upload_to="images/avatars/", default="images/avatars/avatar.webp")
  address = models.CharField(max_length=250, blank=True)
  postal_code = models.CharField(max_length=10, blank=True)
  phone_number = models.CharField(max_length=20, blank=True)
  city = models.CharField(max_length=250, blank=True)

  def __str__(self) -> str:
    return f"Profile {self.user.username}"


class Profile_Seller(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  avatar = models.ImageField(upload_to="images/avatars/", default="images/avatars/avatar.webp")
  twitch_link = models.URLField(blank=True)
  CR = models.CharField(max_length=20)  
  CR_image = models.ImageField(upload_to="images/cr/") 


  def __str__(self) -> str:
    return f"Profile {self.user.username}"