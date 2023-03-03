from django.db import models
import os
# Create your models here.
from django.db import models

class Archivo(models.Model):
    os.makedirs(f'./tmp/',exist_ok=True)
    archivo = models.FileField(upload_to='tmp/')