import django_filters
from .models import *
from django_filters import DateFilter,NumberFilter

class OrderFilter(django_filters.FilterSet):
    name= django_filters.CharFilter(field_name='name',lookup_expr='icontains')
    price = django_filters.NumberFilter(field_name='price')
    stock = django_filters.NumberFilter(field_name='stock')
    
    class Meta:
        model=Inventory
        fields=["name","price","stock"]
        exclude=["creationDate","updateDate"]