from django import forms
from .models import Order, PaymentTest

class OrderForm(forms.ModelForm):

  class Meta:
    model = Order
    fields = ['quantity',  'order_type', 'participants']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_type'].widget = forms.HiddenInput()
        self.fields['order_type'].initial = Order.OrderType.INDIVIDUAL  

class TestPaymentForm(forms.ModelForm):
   class Meta:
      model = PaymentTest
      fields = ['name', 'email', 'phone_number', 'city', 'address', 'postal_code']
