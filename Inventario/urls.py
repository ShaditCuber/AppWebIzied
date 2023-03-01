from django.urls import path
from .views import *
urlpatterns = [
    path("",index,name="index"),
    path("productos/",inventoryList,name="productos"),
    path("producto/<pk>",xProductView,name="xProductView"),
    path("añadir/",addProduct,name="add"),
    path("borrar/<pk>",deleteProduct,name="borrar"),
    path("actualizar/<pk>",updateProduct,name="actualizar"),
    path("bodegas/",bodegaList,name="bodegas"),
    path("addBodega/",addBodega,name="addBodega"),
    path("deleteBodega/<pk>",deleteBodega,name="deleteBodega"),
    path("inventario/",inventarioList,name="inventario"),
    path("addInventario/",adInventario,name="addInventario"),
    path("inventory/<pk>",inventarioHistoria,name="historia"),
    
    
    
    
    
    path("dashboard",dashboard,name="dashboard"),
]