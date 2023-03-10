from django.shortcuts import render,redirect
from .forms import ArchivoForm
from django.contrib import messages
from .leerCSV import *
from .models import *
# Create your views here.



def index(request):
    
    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
            except:
                pass
            files =  request.FILES.getlist('archivo')
            codigo=request.POST['codigoPro']
            if len(files) >2:
                messages.warning(request,"Solo se pueden Subir 2 Archivos o 1 , CSV con NOTAS y PDF con ENCUESTAS")
                return redirect('informe_diplomas')
            csvFile=None
            encuestasFile=None
            for file in files:
                try:
                    Archivo.objects.create(archivo = file)
                except:
                    pass
                if file.name.endswith('.csv'):
                    csvFile=file.name
                if file.name.lower().endswith('.pdf'):
                    encuestasFile=file.name
            
            if csvFile and encuestasFile:
                resp=leer(csvFile,encuestasFile,codigo)
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
                messages.warning(request,"Falta cargar algun archivo")
                return redirect('informe_diplomas')

                
    else:
        form = ArchivoForm()
        
    return render(request, 'Diplomas/index.html', {'form': form})