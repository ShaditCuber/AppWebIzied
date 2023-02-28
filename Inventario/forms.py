from django.forms import ModelForm
from .models import Inventory,warehouse
from django import forms


class añadir(forms.Form):
    code = forms.CharField(
        label="Code",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

    priceUnit = forms.IntegerField(
        label="Precio Unitario",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    resume = forms.CharField(
        label="Descripcion",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    
    idWarehouse = forms.ModelChoiceField(
        queryset=warehouse.objects.all(),
        required=True,
        help_text="bodega",
        label="Bodega",
        to_field_name="idWarehouse" # opcional si desea utilizar el campo 'id' como valor de la opción en lugar del objeto completo
    )
    # class Meta:
    #     model = Inventory
    #     fields = ["name", "price", "stock"]
    #     help_texts ={k:"" for k in fields}
        
        
        
class actualizar(ModelForm):
    
   

    nameProduct = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    

    priceUnit = forms.IntegerField(
        label="Precio Unitario",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    resume = forms.CharField(
        label="Descripcion",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    
    idWarehouse = forms.ModelChoiceField(
        queryset=warehouse.objects.all(),
        required=True,
        help_text="bodega",
        label="Bodega",
        to_field_name="idWarehouse" # opcional si desea utilizar el campo 'id' como valor de la opción en lugar del objeto completo
    )

    class Meta:
        model = Inventory
        fields = ["nameProduct", "priceUnit","resume","idWarehouse"]
        help_texts ={k:"" for k in fields}