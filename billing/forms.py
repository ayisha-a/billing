from django.forms import ModelForm
from .models import Order,Purchase
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class OrderCreateForm(ModelForm):
    class Meta:
        model=Order
        fields=['billnumber','customer_name','phone_number']
      
class OrderLinesForm(forms.Form):
    bill_number=forms.CharField()
    product_quantity=forms.IntegerField()
    product_name = Purchase.objects.all().values_list('product__product_name')
    result = [(tp[0], tp[0]) for tp in product_name]
    product_name=forms.ChoiceField(choices=result)


class RegistrationForm(UserCreationForm):
    class Meta:
        model=User
        fields=["username","first_name","last_name","email","password1","password2"]



class LoginForm(forms.Form):
    username=forms.CharField(max_length=120)
    password=forms.CharField(max_length=120)

