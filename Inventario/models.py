from django.db import models



class warehouse(models.Model):
    nameWarehouse=models.CharField(max_length=100,null=False,blank=False)
    
    def __str__(self) -> str:
        return self.nameWarehouse
    
class Inventory(models.Model):
    
    code=models.CharField(max_length=100,null=False,blank=False,primary_key=True)
    nameProduct = models.CharField(max_length=100,null=False,blank=False)
    priceUnit=models.IntegerField(null=False,blank=False)
    resume=models.CharField(max_length=500,null=False,blank=False)
    creationDate=models.DateField(auto_now_add=True)
    updateDate=models.DateField(auto_now=True,blank=True,null=False)
    idWarehouse=models.ForeignKey(warehouse,blank=True,null=False,on_delete=models.CASCADE,default="")
    
    def __str__(self) -> str:
        return self.code
    
class Inventario(models.Model):
    code = models.ForeignKey(Inventory,blank=True,null=False,on_delete=models.CASCADE,default="")
    stock=models.IntegerField(null=False,blank=False)