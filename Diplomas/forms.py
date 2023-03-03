from django import forms
from .models import Archivo

class ArchivoForm(forms.ModelForm):
    codigoPro=forms.CharField(label='Codigo Pro')
    class Meta:
        model = Archivo
        fields = ('archivo',)