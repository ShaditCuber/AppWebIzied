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
    return render(request,"Inventario/listaProductos.html",context=context)


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
                    nameProduct=informacion['name'],
                    priceUnit = informacion['priceUnit'],
                    code = informacion['code'],
                    resume = informacion['resume'],
                    idWarehouse = informacion['idWarehouse'],
                    
                    )
            producto.save()
            messages.success(request,"Producto Añadido Correctamente")
            return redirect('/productos/')
    else:
        addForm=añadir()
        
    return render(request,"Inventario/addProducto.html",{"form":addForm})


def deleteProduct(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    inventory.delete()
    messages.success(request,"Producto Eliminado Correctamente")
    return redirect("/productos/")

def updateProduct(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    print(inventory)
    if request.method=="POST":
        updateForm=actualizar(data=request.POST)
        if updateForm.is_valid():
            inventory.nameProduct=updateForm.data['nameProduct']
            inventory.priceUnit=updateForm.data['priceUnit']
            inventory.resume=updateForm.data['resume']
            inventory.save()
            messages.success(request,"Producto Actualizado Correctamente")
            
            return redirect(f'/producto/{pk}')
    else:
        updateForm=actualizar(instance=inventory)
    
    return render(request,"Inventario/updateProducto.html",{"form":updateForm})



def bodegaList(request):
    bodegas=warehouse.objects.all()
    context={"title":"Lista Bodegas","bodegas":bodegas}
    return render(request,"Inventario/bodegaList.html",context=context)
    

def inventarioList(request):
    inventario=Inventory.objects.all()
    context={"title":"Lista Inventario","inventario":inventario}
    return render(request,"Inventario/inventarioList.html",context=context)


def inventarioHistoria(request,pk):
    context=dict()
    product=get_object_or_404(Inventory,pk=pk)
    stocks = Stock.objects.filter(product = product).all()
    context['product'] = product
    context['stocks'] = stocks

    return render(request, 'Inventario/inventory-history.html', context )

def adInventario(request):
    if request.method=="POST":
        addForm=addInventario(request.POST)
        if addForm.is_valid():
            informacion = addForm.cleaned_data
            inventario = Stock(
                    product=informacion['producto'],
                    quantity=informacion['cantidad'],
                    type=informacion['type'],
                    
                    
                    )
            inventario.save()
            messages.success(request,"Inventario Añadida Correctamente")
            return redirect('/inventario/')
    else:
        addForm=addInventario()
        
    return render(request,"Inventario/addInventario.html",{"form":addForm})

def addBodega(request):
    if request.method=="POST":
        addForm=añadirBodega(request.POST)
        if addForm.is_valid():
            informacion = addForm.cleaned_data
            bodega = warehouse(
                    nameWarehouse=informacion['name'],
                    )
            bodega.save()
            messages.success(request,"Bodega Añadida Correctamente")
            return redirect('/bodegas/')
    else:
        addForm=añadirBodega()
        
    return render(request,"Inventario/addBodega.html",{"form":addForm})


def deleteBodega(request,pk):
    warehous=get_object_or_404(warehouse,pk=pk)
    warehous.delete()
    messages.success(request,"Bodega Eliminada Correctamente")
    return redirect("/bodegas/")

def dashboard(request):
    inventories=Inventory.objects.all()
    df= read_frame(inventories)
    name_stock = df.groupby(by="nameProduct").sum().sort_values(by="stock")
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