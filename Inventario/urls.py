from django.urls import path,include
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
    path("actualizarBodega/<pk>",modBodega,name="modBodega"),
    path("inventario/",inventarioList,name="inventario"),
    path("addInventario/<pk>",adInventario,name="addInventario"),
    path("addInventario/",adInventario,name="addInventario"),
    path("inventory/<pk>",inventarioHistoria,name="historia"),
    path("registroPresencial/",registroPresencial,name="registro"),

    path("",previous_view,name="previous_view"),
    
    
    
    path("informe_diplomas/",include("Diplomas.urls"),name='informe_diplomas'),
    
    
    
    
    
    
    path("dashboard",dashboard,name="dashboard"),
]