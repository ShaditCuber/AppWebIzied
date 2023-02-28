from django.db import models



class warehouse(models.Model):
    idWarehouse=models.CharField(max_length=100,null=False,blank=False,primary_key=True)
    name=models.CharField(max_length=100,null=False,blank=False)

class Inventory(models.Model):
    code=models.CharField(max_length=100,null=False,blank=False,primary_key=True)
    name = models.CharField(max_length=100,null=False,blank=False)
    priceUnit=models.IntegerField(null=False,blank=False)
    resume=models.CharField(max_length=500,null=False,blank=False)
    # stock=models.IntegerField(null=False,blank=False)
    # typeUnit=models.CharField(max_length=100,null=False,blank=False)
    creationDate=models.DateField(auto_now_add=True)
    updateDate=models.DateField(auto_now=True)
    idWarehouse=models.ForeignKey(warehouse,blank=True,null=False,on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.name
    
class Inventario(models.Model):
    code = models.ForeignKey(Inventory,blank=True,null=False,on_delete=models.CASCADE)
    stock=models.IntegerField(null=False,blank=False)