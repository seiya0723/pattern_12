from django import forms

from .models import Order

class OrderSetForm(forms.ModelForm):
    class Meta:
        model   = Order
        fields  = [ "user","session_id" ]

class OrderPaidForm(forms.ModelForm):
    class Meta:
        model   = Order
        fields  = [ "paid" ]


