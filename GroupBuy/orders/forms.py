from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

  class Meta:
    model = Order
    fields = ['quantity',  'order_type', 'participants']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # نريد إخفاء حقل `order_type` من النموذج 
        self.fields['order_type'].widget = forms.HiddenInput()
        self.fields['order_type'].initial = Order.OrderType.INDIVIDUAL  # تعيينه تلقائيًا كـ فردي

