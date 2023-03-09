from django.db import models
import os
from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.



class Archivo(models.Model):
    os.makedirs(f'./tmp/',exist_ok=True)
    archivo = models.FileField(upload_to='tmp/',validators=[FileExtensionValidator(allowed_extensions=['csv','pdf'])])