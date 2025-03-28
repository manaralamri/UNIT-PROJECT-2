from django import forms
from products.models import Product

# Create the form class.
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['seller']

        widgets = {
            'name' : forms.TextInput({"class" : "form-control"})
        }