from django.shortcuts import render,redirect
from .forms import ArchivoForm
from django.contrib import messages
from .leerCSV import *
# Create your views here.



def index(request):
    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
            except:
                pass
            archivo = request.FILES['archivo']
            codigo=request.POST['codigoPro']
            resp=leer(archivo.name,codigo)
            if resp==200:
                messages.success(request,"Informes cargados correctamente en Monday")
                return redirect('informe_diplomas')
            if resp==401:
                messages.warning(request,"No hay datos del Curso")
                return redirect('informe_diplomas')
            if resp==402:
                messages.warning(request,"Ya existen diplomas en Monday , Elimine el archivo si desea gernerarlos nuevamente")
                return redirect('informe_diplomas')
            if resp==403:
                messages.warning(request,"No existe el curso en Monday")
                return redirect('informe_diplomas')

                
    else:
        form = ArchivoForm()
    return render(request, 'Diplomas/index.html', {'form': form})