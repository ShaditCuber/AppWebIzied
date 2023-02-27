from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django_pandas.io import read_frame
from .models import Inventory
from .forms import *
from .filters import *
import plotly
import plotly.express as px
import json
# Create your views here.

def index(request):
    context={"title":"Inicio"}
    return render(request,"Inventario/index.html",context=context)


def inventoryList(request):
    inventories=Inventory.objects.all()
    filtro=OrderFilter(request.GET,queryset=inventories)
    inventories=filtro.qs
    context={"title":"Lista Inventario","inventories":inventories,"filtro":filtro}
    return render(request,"Inventario/inventario.html",context=context)


def xProductView(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    context={"inventory":inventory}
    return render(request,"Inventario/vistaProducto.html",context=context)


def addProduct(request):
            
    if request.method=="POST":
        addForm=añadir(request.POST)
        if addForm.is_valid():
            informacion = addForm.cleaned_data
            producto = Inventory(
                    name=informacion['name'],
                    price = informacion['price'],
                    stock = informacion['stock'])
            producto.save()
            messages.success(request,"Producto Añadido Correctamente")
            return redirect('/inventario/')
    else:
        addForm=añadir()
        
    return render(request,"Inventario/addProducto.html",{"form":addForm})


def deleteProduct(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    inventory.delete()
    messages.success(request,"Producto Eliminado Correctamente")
    return redirect("/inventario/")

def updateProduct(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    if request.method=="POST":
        updateForm=actualizar(data=request.POST)
        if updateForm.is_valid():
            inventory.name=updateForm.data['name']
            inventory.price=updateForm.data['price']
            inventory.stock=updateForm.data['stock']
            inventory.save()
            messages.success(request,"Producto Actualizado Correctamente")
            
            return redirect(f'/producto/{pk}')
    else:
        updateForm=actualizar(instance=inventory)
    
    return render(request,"Inventario/updateProducto.html",{"form":updateForm})



def dashboard(request):
    inventories=Inventory.objects.all()
    df= read_frame(inventories)
    name_stock = df.groupby(by="name").sum().sort_values(by="stock")
    nameStock = px.bar(name_stock, 
                                    x = name_stock.index, 
                                    y = name_stock.stock, 
                                    title="Nombre Stock"
                                )
    nameStock = json.dumps(nameStock, cls=plotly.utils.PlotlyJSONEncoder)
    
    most_product_in_stock_df = df.groupby(by="name").sum().sort_values(by="stock")
    most_product_in_stock = px.pie(most_product_in_stock_df, 
                                    names = most_product_in_stock_df.index, 
                                    values = most_product_in_stock_df.stock, 
                                    title="Productos en Stock"
                                )
    most_product_in_stock = json.dumps(most_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)
    context={"nameStock":nameStock,"most_product_in_stock":most_product_in_stock}
    return render(request,"Inventario/dashboard.html", context=context)