from django import forms
from .models import Archivo

class ArchivoForm(forms.ModelForm):
    archivo = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    codigoPro=forms.CharField(label='Codigo Pro')
    class Meta:
        model = Archivo
        fields = ('archivo',)