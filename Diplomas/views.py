from django.shortcuts import render,redirect
from .forms import ArchivoForm
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
            if leer(archivo.name,codigo):
                return redirect('informe_diplomas')
    else:
        form = ArchivoForm()
    return render(request, 'Diplomas/index.html', {'form': form})