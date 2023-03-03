import pandas as pd
# from .diplomas_informes import *
from monday import MondayClient
from reportlab.pdfgen import canvas
import os
import PyPDF2
import datetime
from PyPDF2 import PdfMerger
from django.contrib import messages

KEY='eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI'
mon=MondayClient(KEY)

def leer(ruta,codigo):
    fila=None
    try:
       fila= mon.items.fetch_items_by_column_value('3549229417','name',codigo)['data']['items_by_column_values'][0]['id']
    except:
        pass
    
    if not fila:
        return 403
        
    datos=mon.items.fetch_items_by_id(fila)['data']['items'][0]['column_values']
    curso=None
    institucion=None
    horas=None
    fecha =None
    archivo=None
    modalidad=None
    for i in datos:
        if i['id']=='texto14':
            curso=i['text']
        if i['id']=='texto57':
            institucion=i['text']
        if i['id']=='n_meros2':
            horas=i['text']
        if i['id']=='cronograma9':
            fecha=i['text']
        if i['id']=='archivo2':
            archivo=i['text']
        if i['id']=='estado9':
            modalidad=i['text']
            
    if modalidad.strip()=='No informa':
        return 401
    if not curso and not institucion and not horas and not fecha:
        return 401
    
        
    if archivo:
        return 402
    if modalidad=='Presencial':
        base='./static/assets/image/17.png'
        y_horas=700
        tipoFecha=1
    if modalidad=='Sincrónico':
        y_horas=679
        base='./static/assets/image/18.png'
        tipoFecha=2
        
    if modalidad=='Sincrónico/Presencial':
        y_horas=679
        base='./static/assets/image/19.png'
        tipoFecha=2
        

        
    os.makedirs(f'./tmp/{codigo}',exist_ok=True)
    df=pd.read_csv('./tmp/'+ruta)
    merger = PdfMerger()
    #fecha y horas modificar
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
        #cambiar entre los dos tipos de Modalidad
        c.drawImage(base, 0, 0, width=2000, height=1414)
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
        c.drawString(865, y_horas, horas)
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
        if tipoFecha==1:
            fechaFinal=fecha_formateada_inicio+' y '+fecha_formateada_fin
        else:
            fechaFinal=fecha_formateada_inicio+'       '+fecha_formateada_fin
            
        c.drawString(1280, 593, fechaFinal)
        c.save()
        merger.append(result_pdf)
        
    diplomas=f'./tmp/{codigo}/Diplomas.pdf'
    merger.write(diplomas)
    merger.close()     
    from shutil import rmtree
    mon.items.add_file_to_column(fila,'archivo2',diplomas)
    #Subir diplomas a s3
    rmtree('./tmp/')
    return 200
    

    
    
    
    