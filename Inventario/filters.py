import django_filters
from .models import *
from django_filters import DateFilter,NumberFilter

class OrderFilter(django_filters.FilterSet):
    name= django_filters.CharFilter(field_name='nameProduct',lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code')
    
    class Meta:
        model=Inventory
        fields=["name","code"]
        exclude=["creationDate","updateDate"]