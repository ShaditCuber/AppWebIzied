import django_filters
from .models import *
from django_filters import DateFilter,NumberFilter

class OrderFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name='code',label='Codigo')
    
    class Meta:
        model=Inventory
        fields=["code"]
        exclude=["creationDate","updateDate"]


class BodegaFiltro(django_filters.FilterSet):
    idWarehouse = django_filters.ModelChoiceFilter(queryset=warehouse.objects.all(),label='Bodega',initial=warehouse.objects.all().first(),empty_label=None)
    
    class Meta:
        model=Inventory
        fields=["idWarehouse"]
        
class StockFiltro(django_filters.FilterSet):
    product = django_filters.CharFilter(field_name='product',label='Codigo')
    
    class Meta:
        model=Stock
        fields=["product"]