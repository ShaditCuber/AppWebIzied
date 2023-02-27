from django.forms import ModelForm
from .models import Inventory
from django import forms


class añadir(forms.Form):
    name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    price = forms.IntegerField(
        label="Precio",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

    stock = forms.IntegerField(
        label="Stock",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

    # class Meta:
    #     model = Inventory
    #     fields = ["name", "price", "stock"]
    #     help_texts ={k:"" for k in fields}
        
        
        
class actualizar(ModelForm):
    name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    price = forms.IntegerField(
        label="Precio",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

    stock = forms.IntegerField(
        label="Stock",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

    class Meta:
        model = Inventory
        fields = ["name", "price", "stock"]
        help_texts ={k:"" for k in fields}