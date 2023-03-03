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
from PIL import ImageGrab, Image
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
    df=pd.read_csv('./tmp/'+ruta)
    df = df.apply(lambda x: x.str.title() if x.dtype == "object" else x)
        
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
    
    df = df.drop('rut', axis=1)
    # import dataframe_image as dfi
    # dfi.export(df, "df.png", dpi = 600)
    import plotly.graph_objs as go
    from plotly.graph_objs import Layout
    import numpy as np
    df.columns = ['Nombres', 'Nota']
    cantidad=len(df. index)
    if cantidad>13:
        partes=cantidad/12
        df_parts = np.array_split(df, int(partes))
        # Crear figuras para cada una de las partes del dataframe
        figs = []
        for i, part in enumerate(df_parts):
            notas_grouped = part.groupby('Nota').agg({'Nota': 'count'})
            notas_grouped.columns = ['Cantidad Alumnos']
            notas_grouped['Porcentaje'] = notas_grouped['Cantidad Alumnos'] / notas_grouped['Cantidad Alumnos'].sum() * 100
            notas_grouped['Porcentaje'] = notas_grouped['Porcentaje'].apply(lambda x: f"{int(x)}%")

            notas_grouped.index.name = 'Nota'
            notas_grouped.reset_index(inplace=True)
            total_alumnos = part['Nota'].count()
            notas_grouped.loc[len(notas_grouped)] = ['Total', total_alumnos, "100%"]
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
    
    fill_colors = ['lavender' if i%2==0 else 'white' for i in range(len(notas_grouped))]  # Color de fondo para filas pares e impares
    fill_colors[-1] = 'paleturquoise'  # Cambiar color de fondo de la última fila
    fig = go.Figure(data=[
                        go.Table(
                            header=dict(values=list(notas_grouped.columns),align='center',fill_color='#6ec63b',font=dict(color='white')),
                            cells=dict(values=notas_grouped.values.transpose(),
                                    fill_color=[fill_colors],
                                    align='center'
                                    )
                                )
                        ],layout=layout)
    fig.write_image('./tmp/tabla_notas_porcentaje.png',scale=6)
    
    fig = go.Figure(go.Bar(
            x=notas_grouped['Nota'],
            y=notas_grouped['Cantidad Alumnos'],
            width=0.4,
            text=notas_grouped['Cantidad Alumnos'], # agregar texto encima de cada barra
            textposition='outside', # posición del texto
            marker_color='#6ec63b',
            textfont=dict(color='black')
        ),layout=layout)
    fig.update_layout(title='Cantidad de alumnos por nota',title_x=.5)
    fig.write_image('./tmp/tabla_notas_barras.png',scale=6)

    base_dir='./static/assets'
    print("Generando Informe")
    pdf1 = FPDF()
    pdf1.add_page(format = 'A4')

    pdf1.image(base_dir + '\\base\\backgroundnohand.png', x = 0, y = 0, w = 210, h = 297)
    pdf1.add_font('leagueSpartan', '', base_dir + "\\fonts\\league-spartan\\LeagueSpartan-Bold.ttf")
    pdf1.add_font('openSansLight', '', base_dir + "\\fonts\\Open_Sans\\OpenSans-Light.ttf")
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
    fecha_actual = fecha_actual.replace(fecha_actual.split()[1], "de "+meses[fecha_actual.split()[1]].title()+ " del ")
    print(fecha_actual)
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



    # cuadros_notas = [f for f in listdir(download_folder) if isfile(join(download_folder, f)) and "nota" in f]

    pixel_to_mm = 0.2645833333
    normal_widht_change = 1.375
    big_widht_change = 1.15
    # df = df.drop('rut', axis=1)
    # tablaNotas=df.to_html()    
    for tabla in figs:
        pdf1.add_page('P','A4')
        pdf1.image(base_dir + '\\base\\background.png', x = 0, y = 0, w = 210, h = 297)

        pdf1.set_font('leagueSpartan','',28)
        pdf1.set_xy(10,42)
        pdf1.multi_cell(190, 5,
            'Resultados de la Evaluación',
            border = 0,
            align = 'C',
            fill = False)
        
        pdf1.image(tabla, x = 0, y = 0, w = 210, h = 297)
    
    
    
    # pdf1.set_font('Arial', 'B', 12)
    
    # pdf1.cell(40)
    # col_width = pdf1.w / 6
    # row_height = pdf1.font_size * 1.5
    # for col in df.columns:
    #     pdf1.cell(col_width, row_height, str(col).title(), border=1,align='C')
    
    # pdf1.ln(row_height)

    # # Agregar filas de datos
    # for row in df.values:
    #     for item in row:
    #         pdf1.cell(col_width, row_height, str(item), border=1,align='C')
    #     pdf1.ln(row_height)
        
    # pdf1.set_xy(40, 20)

    # # Agregar encabezado
    # pdf1.set_font('Arial', 'B', 16)
    # pdf1.cell(0, 10, 'Tabla de datos', ln=1, align='C')
    # data = dataframe_to_lists(df)
    # for row in data:
    #     for item in row:
    #         pdf1.multi_cell(190, 10, str(item))
    #     pdf1.ln()
    #     cn_img = Image.open(join(download_folder, cuadro_notas))
    #     cn_size = cn_img.size
    #     if max_len_name < 30:
    #         pdf1.image(join(download_folder, cuadro_notas),
    #             x = (210-cn_size[0]*pixel_to_mm*normal_widht_change)/2, 
    #             y = (297-cn_size[1]*pixel_to_mm*1.375)/2 + 10, 
    #             w = cn_size[0]*pixel_to_mm*normal_widht_change, 
    #             h = cn_size[1]*pixel_to_mm*1.375, 
    #             type = 'PNG', link = '')
    #     else:
    #         pdf1.image(join(download_folder, cuadro_notas),
    #             x = (210-cn_size[0]*pixel_to_mm*big_widht_change)/2, 
    #             y = (297-cn_size[1]*pixel_to_mm*1.375)/2 + 10, 
    #             w = cn_size[0]*pixel_to_mm*big_widht_change, 
    #             h = cn_size[1]*pixel_to_mm*1.375, 
    #             type = 'PNG', link = '')

    # cn_img = Image.open(join(download_folder, "agrupadas.png"))
    # cn_size_gp = cn_img.size
    # cn_img.close()
    # cn_img = Image.open(join(download_folder, "graph.png"))
    # cn_size_ch = cn_img.size
    # cn_img.close()
    # if not db_encuesta.empty:
    #     cn_img = Image.open(join(download_folder, "encuesta.png"))
    #     cn_size_en = cn_img.size
    #     cn_img.close()


    # pdf1.add_page(format = 'A4')
    # pdf1.image(base_dir + '\\base\\background.png', x = 0, y = 0, w = 210, h = 297)
    # pdf1.set_font('leagueSpartan','',28)
    # pdf1.set_xy(40,42)
    # pdf1.multi_cell(190, 5,
    #     'Resultados de la Evaluación',
    #     border = 0,
    #     align = 'CB',
    #     fill = False)
    # #1.375 ratio

    # if len(numbers) < 6 : # Caben bien en la pagina juntos     
    #     pdf1.image(join(download_folder, "agrupadas.png"),
    #             x = (210 - cn_size_gp[0]*pixel_to_mm*1.375)/2, 
    #             y = (297 
    #                 - cn_size_gp[1]*pixel_to_mm*1.375
    #                 - cn_size_ch[1]*pixel_to_mm*0.75 
    #                 - 20)/2 + 10, 
    #             w = cn_size_gp[0]*pixel_to_mm*1.375, 
    #             h = cn_size_gp[1]*pixel_to_mm*1.375, 
    #             type = 'PNG', link = '')

    #     pdf1.image(join(download_folder, "graph.png"), 
    #             x = (210 - cn_size_ch[0]*pixel_to_mm*0.75)/2, 
    #             y = (297 
    #                 - cn_size_gp[1]*pixel_to_mm*1.375
    #                 - cn_size_ch[1]*pixel_to_mm*0.75 
    #                 - 20)/2 + 10 
    #                 + cn_size_gp[1]*pixel_to_mm*1.375
    #                 + 20, 
    #             w = cn_size_ch[0]*pixel_to_mm*0.75, 
    #             h = cn_size_ch[1]*pixel_to_mm*0.75, 
    #             type = 'PNG', link = '')

    # else:   # Necesitan 2 Paginas
    #     pdf1.image(join(download_folder, "agrupadas.png"), 
    #         x = (210 - (cn_size_gp[0]*pixel_to_mm))/2, 
    #         y = (297 - (cn_size_gp[1]*pixel_to_mm))/2, 
    #         w = cn_size_gp[0]*pixel_to_mm, 
    #         h = cn_size_gp[1]*pixel_to_mm, 
    #         type = 'PNG', link = '')

    #     pdf1.add_page(format = 'A4')
    #     pdf1.image(base_dir + '\\base\\background.png', x = 0, y = 0, w = 210, h = 297)
    #     pdf1.set_font('leagueSpartan','',28)
    #     pdf1.set_xy(40,42)
    #     pdf1.multi_cell(190, 5,
    #         'Resultados de la Evaluación',
    #         border = 0,
    #         align = 'CB',
    #         fill = False)

    #     """pdf1.image(join(download_folder, "graph.png"), 
    #         x = (210 - (cn_size_ch[0]*pixel_to_mm*0.75))/2, 
    #         y = (297 - (cn_size_ch[1]*pixel_to_mm*0.75))/2, 
    #         w = cn_size_ch[0]*pixel_to_mm*0.75, 
    #         h = cn_size_ch[1]*pixel_to_mm*0.75, 
    #         type = 'PNG', link = '') """   
    #     pdf1.image(join(download_folder, "graph.png"), 
    #         x = 20, 
    #         y = (297 - (cn_size_ch[1]*(170/cn_size_ch[0]))) /2, 
    #         w = 170, 
    #         h = (cn_size_ch[1]*(170/cn_size_ch[0])), 
    #         type = 'PNG', link = '')


    # if not db_encuesta.empty:
    #     pdf1.add_page(format = 'A4')
    #     pdf1.image(base_dir + '\\base\\background.png', x = 0, y = 0, w = 210, h = 297)
    #     pdf1.set_font('leagueSpartan','',28)
    #     pdf1.set_xy(40,42)
    #     pdf1.multi_cell(190, 5,
    #         'Resultados de la Encuesta',
    #         border = 0,
    #         align = 'CB',
    #         fill = False)

    #     pdf1.image(join(download_folder, "encuesta.png"), 
    #             x = (210 - (cn_size_en[0]*pixel_to_mm))/2, 
    #             y = (297 - (cn_size_en[1]*pixel_to_mm))/2, 
    #             w = cn_size_en[0]*pixel_to_mm, 
    #             h = cn_size_en[1]*pixel_to_mm, 
    #             type = 'PNG', link = '')

    pdf1.output("./tmp/generado.pdf")

    ##pdf1.close()
    time.sleep(5)

    merger = PdfMerger()
    merger.append(base_dir+'/base/portada.pdf')
    merger.append("./tmp/generado.pdf")
    merger.append(base_dir+'/base/contraportada.pdf')
    merger.write("./tmp/informe.pdf")
    merger.close()
    # from shutil import rmtree
    # rmtree('./tmp/')
    # dir = './tmp/'
    # for f in os.listdir(dir):
    #     os.remove(os.path.join(dir, f))
    return 200



leer('ejemplo.csv','500000')
    

    
    
    
    