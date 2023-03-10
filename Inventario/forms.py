from django.forms import ModelForm
from .models import Inventory,warehouse,Stock
from django import forms


class añadir(forms.Form):
    code = forms.CharField(
        label="Code",
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
        to_field_name="id" # opcional si desea utilizar el campo 'id' como valor de la opción en lugar del objeto completo
    )
    class Meta:
        model = Inventory
        fields = ["code", "name", "priceUnit","resume","idWarehouse"]
        help_texts ={k:"" for k in fields}
          
class actualizar(ModelForm):
    
    code = forms.CharField(
        label="Code",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        disabled=True,
        required=False
        
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
        required=False,
        disabled=True,
        help_text="bodega",
        label="Bodega",
        to_field_name="id" # opcional si desea utilizar el campo 'id' como valor de la opción en lugar del objeto completo
    )

    class Meta:
        model = Inventory
        fields = ["code", "priceUnit","resume","idWarehouse"]
        help_texts ={k:"" for k in fields}
        
        
class añadirBodega(ModelForm):
    name = forms.CharField(
        label="Nombre Bodega",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = warehouse
        fields = ["name"]
        help_texts ={k:"" for k in fields}
        excluded="code"

class updateBodega(ModelForm):
    nameWarehouse = forms.CharField(
        label="Nombre Bodega",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = warehouse
        fields = ["nameWarehouse"]
        help_texts ={k:"" for k in fields}
    
class addInventario(ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Inventory.objects.all(),
        required=True,
        help_text="producto",
        label="Producto",
        to_field_name="code" # opcional si desea utilizar el campo 'id' como valor de la opción en lugar del objeto completo
    )
    
    cantidad=forms.IntegerField(
        label="Cantidad",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    type = forms.ChoiceField(choices=[('1','Entrada'),('2','Salida')])
    pro=forms.CharField(label="Pro",
        widget=forms.TextInput(attrs={'class': 'form-control'}),required=False,help_text="Solo para registro presencial, de lo contrario dejar vacio")
    
    class Meta:
        model = Stock
        fields = ["producto", "cantidad","type","pro"]
        help_texts ={k:"" for k in fields}