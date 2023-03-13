from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django_pandas.io import read_frame
from django.urls import reverse
from .models import Inventory
from .forms import *
from .filters import *
import plotly
import plotly.express as px
import json
from .laudus import *
import datetime
import pytz
from monday import MondayClient
KEY='eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI'
mon=MondayClient(KEY)
# Create your views here.
now_utc = datetime.datetime.now(datetime.timezone.utc)
# Ajustar a la zona horaria de Chile
timezone = pytz.timezone('America/Santiago')
now_cl = now_utc.astimezone(timezone)
actualChile=now_cl.strftime('%Y-%m-%d')
def previous_view(request):
    previous_view_name = request.GET.get('prev', None)
    if previous_view_name is not None:
        previous_view_url = reverse(previous_view_name)
        return redirect(previous_view_url)
    else:
        # Si no se proporciona una vista anterior, redirige a una página predeterminada
        return redirect('index')

def index(request):
    context={"title":"Inicio"}
    return render(request,"Inventario/index.html",context=context)


def inventoryList(request):
    if validarToken():
        inventories=Inventory.objects.all()
        filtro=CodeFiltro(request.GET,queryset=inventories)
        inventories=filtro.qs
        filtroD=DescripcionFiltro(request.GET,queryset=inventories)
        inventories=filtroD.qs
        context={"title":"Lista Inventario","inventories":inventories,"filtro":filtro,"filtroD":filtroD}
        return render(request,"Inventario/listaProductos.html",context=context)
    else:
        messages.warning(request,"EL TOKEN DE LAUDUS A EXPIRADO , CONTACTA A UN PROGRAMADOR")
        return redirect('index')

def xProductView(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    context={"inventory":inventory}
    return render(request,"Inventario/vistaProducto.html",context=context)


def addProduct(request):
    if request.method=="POST":
        addForm=añadir(request.POST)
        if addForm.is_valid():
            informacion = addForm.cleaned_data
            idLaudus=crearProducto(informacion['code'],informacion['resume'],informacion['priceUnit'])
            if idLaudus:
                producto = Inventory(
                        priceUnit = informacion['priceUnit'],
                        code = informacion['code'],
                        resume = informacion['resume'],
                        idWarehouse = informacion['idWarehouse'],
                        idLaudus=idLaudus
                        )
                producto.save()
                messages.success(request,"Producto Añadido Correctamente")
                return redirect('/productos/')
            else:
                messages.success(request,"Producto Ya Existe")
                return redirect('/productos/')
    else:
        addForm=añadir()
        
    return render(request,"Inventario/addProducto.html",{"form":addForm})


def deleteProduct(request,pk):
    producto = Inventory.objects.get(pk = pk)
    if not eliminarProducto(producto.idLaudus):
        inventory=get_object_or_404(Inventory,pk=pk)
        inventory.delete()
        messages.success(request,"Producto Eliminado Correctamente")
        return redirect("/productos/")
    else:
        messages.success(request,"Producto Asociado a un Ingreso No se Puede eliminar")
        return redirect("/productos/")

def updateProduct(request,pk):
    inventory=get_object_or_404(Inventory,pk=pk)
    if request.method=="POST":
        updateForm=actualizar(data=request.POST)
        if updateForm.is_valid():
            if actualizarProducto(inventory.idLaudus,updateForm.data['resume'],updateForm.data['priceUnit']):
                inventory.priceUnit=updateForm.data['priceUnit']
                inventory.resume=updateForm.data['resume']
                inventory.updateDate=actualChile
                inventory.save()
                messages.success(request,"Producto Actualizado Correctamente")
                
                return redirect(f'/producto/{pk}')
    else:
        updateForm=actualizar(instance=inventory)
    
    return render(request,"Inventario/updateProducto.html",{"form":updateForm})



def bodegaList(request):
    if validarToken():
        bodegas=warehouse.objects.all()
        context={"title":"Lista Bodegas","bodegas":bodegas}
        return render(request,"Inventario/bodegaList.html",context=context)
    else:
        messages.warning(request,"EL TOKEN DE LAUDUS A EXPIRADO , CONTACTA A UN PROGRAMADOR")
        return redirect('index')

def inventarioList(request):
    # validarToken()
    if validarToken():
        inventario=Inventory.objects.all()
        filtro=BodegaFiltro(request.GET,queryset=inventario)
        inventario=filtro.qs
        filtroCode=CodeFiltro(request.GET,queryset=inventario)
        inventario=filtroCode.qs
        filtroN=DescripcionFiltro(request.GET,queryset=inventario)
        inventario=filtroN.qs
        # context={"title":"Lista Inventario","inventario":inventario,"filtro":filtro,"filtroPro":filtroPro,"filtroN":filtroN}
        context={"title":"Lista Inventario","inventario":inventario,"filtroN":filtroN,"filtroCode":filtroCode,"filtro":filtro}
        
        return render(request,"Inventario/inventarioList.html",context=context)
    else:
        messages.warning(request,"EL TOKEN DE LAUDUS A EXPIRADO , CONTACTA A UN PROGRAMADOR")
        return redirect('index')

def inventarioHistoria(request,pk):
    context=dict()
    product=get_object_or_404(Inventory,pk=pk)
    stocks = Stock.objects.filter(product = product).all()
    context['product'] = product
    context['stocks'] = stocks

    return render(request, 'Inventario/inventory-history.html', context )

def adInventario(request,pk=""):
    product=get_object_or_404(Inventory,pk=pk)
    if request.method=="POST":
        addForm=addInventario(request.POST)
        if addForm.is_valid():
            informacion = addForm.cleaned_data
            producto = Inventory.objects.get(pk = informacion['producto'])
            warehouseID=warehouse.objects.get(pk=producto.idWarehouse.pk)
            if informacion['type']=='1':
                ingresoBodega(warehouseID.idLaudus,producto.idLaudus,informacion['cantidad'])
            else:
                salidaBodega(warehouseID.idLaudus,producto.idLaudus,informacion['cantidad'])
            inventario = Stock(
                    product=informacion['producto'],
                    quantity=informacion['cantidad'],
                    type=informacion['type'],
                    pro=informacion['pro'],
                    )
            inventario.save()
            messages.success(request,"Inventario Añadida Correctamente")
            return redirect('/inventario/')
    else:
        addForm=addInventario(initial={'producto': product})
        
    return render(request,"Inventario/addInventario.html",{"form":addForm})

def addBodega(request):
    if request.method=="POST":
        addForm=añadirBodega(request.POST)
        if addForm.is_valid():
            informacion = addForm.cleaned_data
            idLaudus=crearBodega(informacion['name'])
            bodega = warehouse(
                    nameWarehouse=informacion['name'],
                    idLaudus=idLaudus
                    )
            bodega.save()
            messages.success(request,"Bodega Añadida Correctamente")
            return redirect('/bodegas/')
    else:
        addForm=añadirBodega()
    
    return render(request,"Inventario/addBodega.html",{"form":addForm})


def modBodega(request,pk):
    bod=get_object_or_404(warehouse,pk=pk)
    if request.method=="POST":
        updateForm=updateBodega(data=request.POST)
        
        if updateForm.is_valid():
            if actualizarBodega(bod.idLaudus,updateForm.data['name']):
                bod.nameWarehouse=updateForm.data['name']
                bod.save()
                messages.success(request,"Bodega Actualizada Correctamente")
                return redirect(f'/bodegas/')
    else:
        updateForm=updateBodega(instance=bod)
    
    return render(request,"Inventario/updateBodega.html",{"form":updateForm})

def deleteBodega(request,pk):
    warehous=get_object_or_404(warehouse,pk=pk)
    warehous.delete()
    messages.success(request,"Bodega Eliminada Correctamente")
    return redirect("/bodegas/")

def dashboard(request):
    stocks = Stock.objects.all()

    df= read_frame(stocks)
    name_stock = df.groupby(by="product").sum().sort_values(by="quantity")
    nameStock = px.bar(name_stock, 
                                    x = name_stock.index, 
                                    y = name_stock.quantity, 
                                    title="Nombre Stock"
                                )
    nameStock = json.dumps(nameStock, cls=plotly.utils.PlotlyJSONEncoder)
    
    most_product_in_stock_df = df.groupby(by="product").sum().sort_values(by="quantity")
    most_product_in_stock = px.pie(most_product_in_stock_df, 
                                    names = most_product_in_stock_df.index, 
                                    values = most_product_in_stock_df.quantity, 
                                    title="Productos en Stock"
                                )
    most_product_in_stock = json.dumps(most_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)
    context={"nameStock":nameStock,"most_product_in_stock":most_product_in_stock}
    return render(request,"Inventario/dashboard.html", context=context)



def obtenerRelatores(pro):
    BOARD_ID='3667934365'
    COLUMN_ID='name'
    data=mon.items.fetch_items_by_column_value(BOARD_ID, COLUMN_ID, pro)['data']['items_by_column_values'][0]['column_values']
    relatores=None
    fecha=None
    for i in data:
        if i['id']=='dup__of_celular_encargado':
            relatores=i['text']
        if i['id']=='dup__of_dup__of_reflejo':
            fecha=i['text']

    if relatores and fecha:
        return relatores.split(','),fecha
    else:
        return None

def registroPresencial(request):
    show=False
    pro=None
    relatores=None
    fecha=None
    if request.method=="GET" and request.GET.get('pro')!=None:
        pro = request.GET.get('pro')
        show=True
        relatores,fecha=obtenerRelatores(pro)
        if relatores and fecha:
            pass
        else:
            messages.warning(request,'No se encontraron relatores')
            redirect('registro')
    if request.method=="POST":
        pro = request.GET.get('pro')
        fecha_salida = request.POST.get('date')
        relator = request.POST.get('relator')
        maleta = request.POST.get('maleta')

        print('Salida perteneciente a :'+pro)
        print('Fecha Salida: ' +fecha_salida)
        print('Fecha Curoso '+fecha)
        print(relator)
        print(maleta)

        if 'True' in request.POST.getlist('data'):
            # Se ha seleccionado el checkbox 'Data'
            print('Se lleva un data')
            
        if 'True' in request.POST.getlist('monitor'):
            # Se ha seleccionado el checkbox 'Monitor de signos'
            # ...
            print('Se lleva un Monitor')
            
        if 'True' in request.POST.getlist('notebook'):
            # Se ha seleccionado el checkbox 'Notebook'
            # ...
            print('Se lleva un Note')
            
        if 'True' in request.POST.getlist('carpetas'):
            # Se ha seleccionado el checkbox 'Carpetas'
            cantidad = request.POST.get('carpetas_cantidad')
            # ...
            print('Se lleva ',cantidad,' de carpetas')
            
        if 'True' in request.POST.getlist('lapices'):
            # Se ha seleccionado el checkbox 'Lápices'
            cantidad = request.POST.get('lapices_cantidad')
            # ...
            print('Se lleva ',cantidad,' de lapices')
            
            
            
        if 'True' in request.POST.getlist('dea'):
            # Se ha seleccionado el checkbox 'DEA'
            cantidad = request.POST.get('dea_cantidad')
            # ...
            print('Se lleva ',cantidad,' de dea')
            
        
        
        
        
    maletas = Inventory.objects.filter(resume__icontains='maleta').values_list('resume', flat=True)
    productos = Inventory.objects.all().values_list('resume', flat=True)
    
    context={"relatores":relatores,"maletas":maletas,"productos":productos,"show_second_form":show,"pro":pro,"productos":productosCheck}
    return render(request,"Inventario/registroPresencial.html",context=context)



def informe_diplomas(request):
    return render(request,"Inventario/index.html")