from django.db import models

# Create your models here.
class Inventory(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False)
    price=models.DecimalField(max_digits=19,decimal_places=2,null=False,blank=False)
    stock=models.IntegerField(null=False,blank=False)
    creationDate=models.DateField(auto_now_add=True)
    updateDate=models.DateField(auto_now=True)
    
    
    def __str__(self) -> str:
        return self.name