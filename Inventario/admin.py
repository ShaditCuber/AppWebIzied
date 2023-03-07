from django.contrib import admin
from .models import Inventory,Stock,warehouse
# Register your models here.
admin.site.register(Inventory)
admin.site.register(Stock)
admin.site.register(warehouse)

