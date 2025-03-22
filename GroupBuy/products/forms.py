from django import forms
from products.models import Product

# Create the form class.
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'name' : forms.TextInput({"class" : "form-control"})
        }