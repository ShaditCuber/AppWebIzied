from django.shortcuts import render

# Create your views here.
def index(request):
    context={"title":"Inicio"}
    return render(request,"Inventario/index.html",context=context)