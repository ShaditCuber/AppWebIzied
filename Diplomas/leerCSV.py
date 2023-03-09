import pandas as pd
from monday import MondayClient
from reportlab.pdfgen import canvas
import os
import datetime
from PyPDF2 import PdfMerger
import boto3
from fpdf import FPDF
import math
import time
import plotly.graph_objs as go
from plotly.graph_objs import Layout
import numpy as np
from encuestaOCR import ocr
BUCKET_KEY = 'informes-diplomas'
s3_client = boto3.client('s3')
KEY='eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI'
mon=MondayClient(KEY)

def dataframe_to_lists(df):
    data = []
    # Agregar encabezados
    data.append(list(df.columns))
    # Agregar filas
    for index, row in df.iterrows():
        data.append(list(row.values))
    return data

def leer(csvFile,encuestasFile,codigo):
    
    
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
    relatorNombre=None
    relatorRut=None
    relatorProfesion=None
    for i in datos:
        if i['id']=='texto14':
            curso=i['text'].title()
        if i['id']=='texto57':
            institucion=i['text'].title()
        if i['id']=='n_meros2':
            horas=i['text']
        if i['id']=='cronograma9':
            fecha=i['text']
        if i['id']=='archivo2':
            archivo=i['text']
        if i['id']=='estado9':
            modalidad=i['text'].title()
        if i['id']=='conectar_tableros1':
            relatorNombre=(i['text'].split(','))[0]
        
    relatorDatos=mon.items.fetch_items_by_column_value('3549156018','name',relatorNombre)['data']['items_by_column_values'][0]['column_values']
    for dato in relatorDatos:
        if dato['id']=='texto':
            relatorRut=dato['text']
        if dato['id']=='texto0':
            relatorProfesion=dato['text']
            
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
    dfOriginal=pd.read_csv('./tmp/'+csvFile)
    dfOriginal = dfOriginal.apply(lambda x: x.str.title() if x.dtype == "object" else x)
        
    merger = PdfMerger()
    #fecha y horas modificar
    
    
    for elemento,row in dfOriginal.iterrows():
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
        fin=fecha.split(' - ')[1]
        fecha_obj = datetime.datetime.strptime(inicio, '%Y-%m-%d')
        fecha_formateada_inicio = fecha_obj.strftime('%d/%m/%Y')
        fecha_obj = datetime.datetime.strptime(fin, '%Y-%m-%d')
        fecha_formateada_fin = fecha_obj.strftime('%d/%m/%Y')
        year=fecha_obj.strftime('%Y')
        if tipoFecha==1:
            fechaFinal=fecha_formateada_inicio+' y '+fecha_formateada_fin
            x_fecha=1280
        else:
            fechaFinal=fecha_formateada_inicio+'       '+fecha_formateada_fin
            x_fecha=1250
        
        c.drawString(x_fecha, 593, fechaFinal)
        c.save()
        s3_path = year + "/" + codigo + "/" + rut+".pdf"
            
        # try:
        #     s3_client.upload_file(result_pdf, BUCKET_KEY, s3_path)
        #     print(s3_path)
        # except Exception as e:
        #     print(e)
        #     pass
        merger.append(result_pdf)
        
    
        
    diplomas=f'./tmp/{codigo}/Diplomas.pdf'
    merger.write(diplomas)
    merger.close()     
    # mon.items.add_file_to_column(fila,'archivo2',diplomas)
    
    dfSinRut = dfOriginal.drop('rut', axis=1)
    # import dataframe_image as dfi
    # dfi.export(df, "df.png", dpi = 600)

    dfSinRut.columns = ['Nombres', 'Nota']
    cantidad=len(dfOriginal. index)
    partes=cantidad/12
    if int(partes)==0:
        partes=1 
    df_parts = np.array_split(dfSinRut, int(partes))
    # Crear figuras para cada una de las partes del dataframe
    figs = []
    #Creamos las tablas de Nombre - Nota
    for i, part in enumerate(df_parts):
        
        fill_colors = ['lavender' if i%2==0 else 'white' for i in range(len(part))]  # Color de fondo para filas pares e impares
        layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
        )
        fig = go.Figure(data=[
                            go.Table(
                                header=dict(values=list(part.columns),align='center',fill_color='#6ec63b',font=dict(color='white')),
                                cells=dict(values=part.values.transpose(),
                                        fill_color=[fill_colors],
                                        align='center'
                                        )
                                    )
                            ],layout=layout)

        fig.write_image(f'./tmp/tabla_notas-{i}.png',scale=6)
        figs.append(f'./tmp/tabla_notas-{i}.png')
     
     
    
    
    
    counts=dfSinRut['Nota'].value_counts()
    # Calculamos los porcentajes de cada nota
    percentages = counts / counts.sum() * 100
    # Creamos la tabla
    table = pd.concat([counts, percentages], axis=1)
    table.columns = ['Cantidad Alumnos', 'Porcentaje']
    table.index.name = 'Nota'
    table.reset_index(inplace=True)
    total_alumnos = counts.sum()
    table['Porcentaje'] = table['Porcentaje'].round(2).apply(lambda x: f"{x}%")
    cantidadPorcentaje=len(table. index)
    partesP=cantidadPorcentaje/12
    if int(partesP)==0:
        partesP=1
    dfPartsPorcentaje = np.array_split(table, int(partesP))
    for i, part in enumerate(dfPartsPorcentaje):
        fill_colors = ['lavender' if i%2==0 else 'white' for i in range(len(table))]  # Color de fondo para filas pares e impares
        
        if i == len(dfPartsPorcentaje) - 1:
            part.loc[len(part)] = ['Total', total_alumnos, '100%']
            fill_colors[-1] = 'paleturquoise'  # Cambiar color de fondo de la última fila
        fig = go.Figure(data=[
                                go.Table(
                                    header=dict(values=list(part.columns),align='center',fill_color='#6ec63b',font=dict(color='white')),
                                    cells=dict(values=part.values.transpose(),
                                            fill_color=[fill_colors],
                                            align='center'
                                            )
                                        )
                                ],layout=layout)
        
        fig.write_image(f'./tmp/tabla_notas_porcentaje-{i}.png',scale=6)
        figs.append(f'./tmp/tabla_notas_porcentaje-{i}.png')
    
    # for i, part in enumerate(df_parts):
    #     notas_grouped = part.groupby('Nota').agg({'Nota': 'count'})
    #     print(notas_grouped)
    #     exit()
    #     notas_grouped.columns = ['Cantidad Alumnos']
    #     notas_grouped['Porcentaje'] = notas_grouped['Cantidad Alumnos'] / notas_grouped['Cantidad Alumnos'].sum() * 100
    #     notas_grouped['Porcentaje'] = notas_grouped['Porcentaje'].apply(lambda x: f"{int(x)}%")

    #     notas_grouped.index.name = 'Nota'
    #     notas_grouped.reset_index(inplace=True)
    #     total_alumnos = part['Nota'].count()
    #     fill_colors = ['lavender' if i%2==0 else 'white' for i in range(len(notas_grouped))]  # Color de fondo para filas pares e impares
        
    #     if i == len(df_parts) - 1:
    #         # Add "Total" row to notas_agrupadas
    #         notas_grouped.loc[len(notas_grouped)] = ['Total', total_alumnos, '100%']
    #         fill_colors[-1] = 'paleturquoise'  # Cambiar color de fondo de la última fila
        
    #     fig = go.Figure(data=[
    #                         go.Table(
    #                             header=dict(values=list(notas_grouped.columns),align='center',fill_color='#6ec63b',font=dict(color='white')),
    #                             cells=dict(values=notas_grouped.values.transpose(),
    #                                     fill_color=[fill_colors],
    #                                     align='center'
    #                                     )
    #                                 )
    #                         ],layout=layout)
    #     fig.write_image(f'./tmp/tabla_notas_porcentaje-{i}.png',scale=6)
    #     figs.append(f'./tmp/tabla_notas_porcentaje-{i}.png')
    # Definir los límites de los intervalos
    
    # bins=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7]
    # dfTablaNotas==
    # # Crear una nueva columna en el dataframe con los intervalos correspondientes a cada nota
    # dfSinRut['rango_notas'] = pd.cut(float(dfSinRut['Nota']), bins=bins)
    # print(dfSinRut)
    # # Agrupar el dataframe por los intervalos y contar la cantidad de alumnos en cada intervalo
    # tabla_notas = part.groupby('rango_notas')['Nota'].agg(['count']).reset_index()
    # print(tabla_notas)
    # exit()
    # # Renombrar las columnas
    # tabla_notas.columns = ['Rango de Notas', 'Cantidad Alumnos']

    # # Mostrar la tabla resultante
    # print(tabla_notas)
    
    # exit()
    dfBarras=table
    
    if cantidad>60:
        # bins = [x/2 for x in range(2, 15)]
        # labels = [f'{x-.5} - {x}' for x in bins]
        dfBarras = dfBarras.drop('Porcentaje', axis=1)
        dfBarras=dfBarras.iloc[:-1]
        # notas_grouped['rango_notas'] = pd.cut(notas_grouped['Nota'], bins=range(0, 110, 10))
        # df_grouped = notas_grouped.groupby('rango_notas')['Cantidad Alumnos'].sum().reset_index()
        # fig=go.Figure(go.Bar(x=df_grouped['rango_notas'], y=df_grouped['Cantidad Alumnos']),layout=layout)
        # print(fig)
        # fig.write_image('./tmp/tabla_notas_barras.png',scale=6)
        dfBarras['rango_notas'] = pd.cut(dfBarras['Nota'], bins=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7])
        dfBarras = dfBarras.groupby('rango_notas')['Cantidad Alumnos'].sum().reset_index()
        dfBarras['rango_notas_str'] = dfBarras['rango_notas'].astype(str)
        dfBarras['rango_notas_display'] = dfBarras['rango_notas'].apply(lambda x: f'{x.left}-{x.right}')
        fig = go.Figure([go.Bar(x=dfBarras['rango_notas_display'], y=dfBarras['Cantidad Alumnos'])],layout=layout)
        fig.write_image('./tmp/tabla_notas_barras.png',scale=6)
        figs.append('./tmp/tabla_notas_barras.png')
        
        # dfBarras['Nota']=dfBarras['Nota'].apply(lambda x: int(x))
        # dfBarras['Nota Rango'] = pd.cut(dfBarras['Nota'], bins=bins, labels=labels)
        # dfBarras['Nota Rango Num'] = dfBarras['Nota Rango'].apply(lambda x: (float(x.split('-')[0].strip()) + float(x.split('-')[1].strip())) / 2)

        # dfBarras = dfBarras.groupby('Nota Rango Num').sum().reset_index()

        # fig = go.Figure(go.Bar(
        #     x=dfBarras['Nota Rango Num'],
        #     y=dfBarras['Cantidad Alumnos'],
        #     width=0.4,
        #     text=dfBarras['Cantidad Alumnos'],
        #     textposition='auto',
        #     marker_color='#6ec63b',
        #     textfont=dict(color='black')
        # ),layout=layout)
        # fig.update_layout(title='Cantidad de alumnos por nota',title_x=.5)
        # fig.write_image('./tmp/tabla_notas_barras.png',scale=6)
    else:
        dfBarras = dfBarras.groupby('Nota').agg({'Nota': 'count'})
        dfBarras.columns = ['Cantidad Alumnos']
        dfBarras.index.name = 'Nota'
        dfBarras.reset_index(inplace=True)
        dfBarras['Nota'] = dfBarras['Nota'].apply(lambda x: '{:.1f}'.format(x))
        fig = go.Figure(go.Bar(
                x=dfBarras['Nota'],
                y=dfBarras['Cantidad Alumnos'],
                width=0.1,
                text=dfBarras['Cantidad Alumnos'], # agregar texto encima de cada barra
                textposition='outside', # posición del texto
                marker_color='#6ec63b',
                textfont=dict(color='black')
            ),layout=layout)
        fig.update_layout(title='Cantidad de alumnos por nota',title_x=.5)
        fig.write_image('./tmp/tabla_notas_barras.png',scale=6)
        figs.append('./tmp/tabla_notas_barras.png')

    base_dir='./static/assets'
    print("Generando Informe")
    pdf1 = FPDF()
    pdf1.add_page()
    #eliminar pkl antes de subir a git uwu para no tenr problemas con las fuentes
    pdf1.image(base_dir + '\\base\\backgroundnohand.png', x = 0, y = 0, w = 210, h = 297)
    leaguePath=os.path.join(base_dir,'fonts','league-spartan','LeagueSpartan-Bold.ttf')
    openPath=os.path.join(base_dir,'fonts','Open_Sans','OpenSans-Light.ttf')
    
    pdf1.add_font('leagueSpartan', '', leaguePath,uni=True)
    pdf1.add_font('openSansLight', '', openPath,uni=True)
    pdf1.set_text_color(51,76,91) 

    now = datetime.datetime.now()
    meses = {
    'January': 'enero',
    'February': 'febrero',
    'March': 'marzo',
    'April': 'abril',
    'May': 'mayo',
    'June': 'junio',
    'July': 'julio',
    'August': 'agosto',
    'September': 'septiembre',
    'October': 'octubre',
    'November': 'noviembre',
    'December': 'diciembre'
    }

    fecha_actual = now.strftime("%d %B %Y")
    fecha_actual = fecha_actual.replace(fecha_actual.split()[1], "de "+meses[fecha_actual.split()[1]].title()+ " del")
    pdf1.set_font('openSansLight','',16)
    pdf1.set_xy(25,50)
    pdf1.multi_cell(160, 9,
        "San Pedro de la Paz, {}, Rodrigo Villablanca Cuevas, director de Sociedad Huellas Capacitaciones Spa, envía las siguientes conclusiones basadas en la capacitación:".format(fecha_actual),
        border = 0,
        align = 'J',
        fill = False)

    centering_offset = 4-int(math.ceil(len(curso)/50))

    pdf1.set_font('leagueSpartan','',16)
    pdf1.set_xy(25,85+(centering_offset*5))
    pdf1.multi_cell(160, 9,
        '"{0}"'.format(curso.title()),
        border = 0,
        align = 'C',
        fill = False)


    pdf1.set_font('openSansLight','',16)
    pdf1.set_xy(25,130)
    pdf1.multi_cell(160, 9,'Realizado desde el '+
        fecha_formateada_inicio+' al '+fecha_formateada_fin,
        border = 0,
        align = 'J',
        fill = False)

    pdf1.set_font('leagueSpartan','',14)
    pdf1.set_xy(25,180)
    pdf1.multi_cell(160, 9,
        'RELATOR',
        border = 0,
        align = 'L',
        fill = False)

    pdf1.set_font('openSansLight','',16)
    pdf1.set_xy(25,190)
    #Correo??
    pdf1.multi_cell(160, 9,
        """{0}
    Rut: {1}
    Correo Electrónico: contacto@huellascapacitaciones.cl
    Profesión: {2}""".format(relatorNombre, relatorRut, relatorProfesion),
        border = 0,
        align = 'L',
        fill = False)


    encuesta=ocr('./tmp/'+encuestasFile)
    for i in encuesta:
        figs.append(i)
    
    
    for tabla in figs:
        pdf1.add_page(orientation='P')
        pdf1.image(base_dir + '\\base\\background.png', x = 0, y = 0, w = 210, h = 297)
        pdf1.set_font('leagueSpartan','',28)
        pdf1.set_xy(12,42)
        if tabla.endswith('Encuesta.png'):
            pdf1.multi_cell(190, 5,
            'Resultados de la Encuesta',
            border = 0,
            align = 'C',
            fill = False)
        else:
            pdf1.multi_cell(190, 5,
                'Resultados de la Evaluación',
                border = 0,
                align = 'C',
                fill = False)
        print(tabla)
        pdf1.image(tabla, x = 0, y = 0, w = 210, h = 297)

    pdf1.output("./tmp/generado.pdf")

    ##pdf1.close()
    time.sleep(5)

    merger = PdfMerger()
    merger.append(base_dir+'/base/portada.pdf')
    merger.append("./tmp/generado.pdf")
    merger.append(base_dir+'/base/contraportada.pdf')
    merger.write("./tmp/Informe.pdf")
    merger.close()
    # from shutil import rmtree
    # rmtree('./tmp/')
    # dir = './tmp/'
    # for f in os.listdir(dir):
    #     os.remove(os.path.join(dir, f))
    return 200



leer('ejemplo.csv','encuestav4-2-resp.pdf','500000')
    

    
    
    
    