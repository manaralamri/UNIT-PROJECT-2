from django.db import models

# Create your models here.
class Contact(models.Model):

    name = models.CharField(max_length=1024)
    email = models.EmailField()
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return self.name