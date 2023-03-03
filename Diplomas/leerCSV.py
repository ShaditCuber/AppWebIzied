import pandas as pd
# from .diplomas_informes import *
from monday import MondayClient
from reportlab.pdfgen import canvas
import os
import PyPDF2
import datetime
KEY='eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI'
mon=MondayClient(KEY)

def leer(ruta,codigo):
    fila=None
    try:
       fila= mon.items.fetch_items_by_column_value('3549229417','name',codigo)['data']['items_by_column_values'][0]['id']
    except:
        pass
    if not fila:
        exit()
        
    datos=mon.items.fetch_items_by_id(fila)['data']['items'][0]['column_values']
    curso=None
    institucion=None
    horas=None
    fecha =None
    for i in datos:
        if i['id']=='texto14':
            curso=i['text']
        if i['id']=='texto57':
            institucion=i['text']
        if i['id']=='n_meros2':
            horas=i['text']
        if i['id']=='cronograma9':
            fecha=i['text']
            
    if not curso and not institucion and not horas and not fecha:
        exit()
    
    os.makedirs(f'./tmp/{codigo}',exist_ok=True)
    df=pd.read_csv('./tmp/'+ruta)
    pdf_salida = PyPDF2.PdfFileWriter()
    for elemento,row in df.iterrows():
        nombres=row['nombres']
        rut=str(row['rut']).replace('.0','')
        nota=str(row['notas'])
        if str(rut)=='nan':
            result_pdf = f"./tmp/{codigo}/{elemento}.pdf"
        else:
            result_pdf = f"./tmp/{codigo}/{rut}.pdf"
        c = canvas.Canvas(result_pdf, pagesize=(2000,1414))
        c.setFont('Helvetica',50)
        c.drawImage('./static/assets/image/base.png', 0, 0, width=2000, height=1414)
        x_nombre = (2000 - c.stringWidth(nombres)) / 2
        c.drawString(x_nombre, 995 , nombres)
        c.setFont('Helvetica',35)
        try:
            if not str(rut)=='nan':
                x_rut = (2000 - c.stringWidth(rut)) / 2
                c.drawString(x_rut, 925, rut)
        except:
            pass
        c.setFont('Helvetica',40)
        x_curso = (2000 - c.stringWidth(curso)) / 2
        c.drawString(x_curso, 777, curso)
        c.setFont('Helvetica',25)
        c.drawString(865, 700, horas)
        c.setFont('Helvetica',40)
        x_institucion = (2000 - c.stringWidth(institucion)) / 2
        c.drawString(x_institucion, 638, institucion)
        c.setFont('Helvetica',28)
        c.drawString(955, 550, nota)
        c.setFont('Helvetica',24)
        inicio=fecha.split(' - ')[0]
        fin=fecha.split(' - ')[0]
        fecha_obj = datetime.datetime.strptime(inicio, '%Y-%m-%d')
        fecha_formateada_inicio = fecha_obj.strftime('%d/%m/%Y')
        fecha_obj = datetime.datetime.strptime(fin, '%Y-%m-%d')
        fecha_formateada_fin = fecha_obj.strftime('%d/%m/%Y')
        print(fecha_formateada_inicio,fecha_formateada_fin)
        c.drawString(1280, 593, fecha_formateada_inicio+' y '+fecha_formateada_fin)
        
        c.save()
        # Abre cada archivo en modo de lectura binaria
        with open(result_pdf, 'rb') as pdf_actual:
            # Crea un objeto de lectura para el archivo actual
            pdf_leido = PyPDF2.PdfFileReader(pdf_actual)
            # Itera a través de todas las páginas del archivo actual y añádelas al archivo de salida
            for pagina in range(pdf_leido.getNumPages()):
                pdf_salida.addPage(pdf_leido.getPage(pagina))

    with open(f'./tmp/{codigo}/diplomas.pdf', 'wb') as pdf_resultado:
        pdf_salida.write(pdf_resultado)
    
    pdf_resultado.close()
leer('ejemplo.csv','ppp')