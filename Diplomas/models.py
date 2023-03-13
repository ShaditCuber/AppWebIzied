from django.db import models
import os
from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.



class Archivo(models.Model):
    os.makedirs(f'./tmp/',exist_ok=True)
    archivo = models.FileField(upload_to='tmp/',validators=[FileExtensionValidator(allowed_extensions=['csv','pdf'])])
    
    
    
    
# class Maleta(models.Model):
#     nombre = models.CharField(max_length=100)

# class Producto(models.Model):
#     nombre = models.CharField(max_length=100)

# class Salida(models.Model):
#     pro = models.TextField()
#     fecha_salida = models.DateField()
#     relator = models.TextField()
#     maleta = models.ManyToManyField(Maleta, on_delete=models.PROTECT)
#     productos = models.ManyToManyField(Producto, blank=True)
#     contenido_fuera_maleta = models.ManyToManyField(Producto, blank=True)