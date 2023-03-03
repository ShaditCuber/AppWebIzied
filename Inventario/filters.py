import django_filters
from .models import *
from django_filters import DateFilter,NumberFilter

class OrderFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name='code',label='Codigo')
    
    class Meta:
        model=Inventory
        fields=["code"]
        exclude=["creationDate","updateDate"]