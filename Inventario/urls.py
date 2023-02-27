from django.urls import path
from .views import *
urlpatterns = [
    path("",index,name="index"),
    path("inventario/",inventoryList,name="inventario"),
    path("producto/<int:pk>",xProductView,name="xProductView"),
    path("añadir/",addProduct,name="add"),
    path("borrar/<int:pk>",deleteProduct,name="borrar"),
    path("actualizar/<int:pk>",updateProduct,name="actualizar"),

    
    

]