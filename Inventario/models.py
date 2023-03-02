from django.db import models



class warehouse(models.Model):
    nameWarehouse=models.CharField(max_length=100,null=False,blank=False)
    idLaudus=models.CharField(max_length=100,null=False,blank=False)
    def __str__(self) -> str:
        return self.nameWarehouse
    
class Inventory(models.Model):
    
    code=models.CharField(max_length=100,null=False,blank=False,primary_key=True)
    # nameProduct = models.CharField(max_length=100,null=False,blank=False)
    priceUnit=models.IntegerField(null=False,blank=False)
    resume=models.CharField(max_length=500,null=False,blank=False)
    creationDate=models.DateField(auto_now_add=True)
    updateDate=models.DateField(auto_now=True,blank=True,null=False)
    idWarehouse=models.ForeignKey(warehouse,blank=True,null=False,on_delete=models.CASCADE,default="")
    idLaudus=models.IntegerField(null=False,blank=False)
    def __str__(self) -> str:
        return self.code

    def count_inventory(self):
        stocks = Stock.objects.filter(product = self)
        stockIn = 0
        stockOut = 0
        for stock in stocks:
            if stock.type == '1':
                stockIn = int(stockIn) + int(stock.quantity)
            else:
                stockOut = int(stockOut) + int(stock.quantity)
        available  = stockIn - stockOut
        return available
    
class Stock(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    type = models.CharField(max_length=2,choices=(('1','Entrada'),('2','Salida')), default = 1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True,blank=True,null=False)
    pro=models.CharField(max_length=100,null=False,blank=False,default="")