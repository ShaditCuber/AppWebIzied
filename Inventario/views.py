from django.shortcuts import render,get_object_or_404,redirect
from .models import Inventory
from .forms import *
from .filters import *
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
            return redirect('/inventario/')
    else:
        addForm=añadir()
        
    return render(request,"Inventario/addProducto.html",{"form":addForm})


def deleteProduct(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    inventory.delete()
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
            return redirect(f'/producto/{pk}')
    else:
        updateForm=actualizar(instance=inventory)
    
    return render(request,"Inventario/updateProducto.html",{"form":updateForm})