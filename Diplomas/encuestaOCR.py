import cv2
import numpy as np
import plotly.graph_objects as go
from imutils.perspective import four_point_transform
from pdf2image import convert_from_path
from plotly.graph_objs import Layout

 

class BubbleSheetScanner:
    questionCount = 11
    bubbleCount = 7
    sqrAvrArea = 0
    bubbleWidthAvr = 0
    bubbleHeightAvr = 0
    ovalCount = questionCount * bubbleCount
    
    def __init__(self):
        pass

    def getCannyFrame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
        frame = cv2.Canny(gray, 127, 255)
        return frame

    def getAdaptiveThresh(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        adaptiveFrame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 7)
        # adaptiveFrame = canny = cv2.Canny(frame, 127, 255)
        return adaptiveFrame

    def getFourPoints(self, canny):
        squareContours = []
        contours, hie = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            fourPoints = []
            i = 0
            for cnt in contours:

                (x, y), (MA, ma), angle = cv2.minAreaRect(cnt)

                epsilon = 0.04 * cv2.arcLength(cnt, False)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                if len(approx) == 4 and aspect_ratio >= 0.9 and aspect_ratio <= 1.1:
                    M = cv2.moments(cnt)
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    fourPoints.append((cx, cy))
                    squareContours.append(cnt)
                    i += 1
            return fourPoints, squareContours

    # We are using warping process for creative purposes
    def getWarpedFrame(self, cannyFrame, frame):

        fourPoints = np.array(self.getFourPoints(cannyFrame)[0], dtype="float32")
        fourContours = self.getFourPoints(cannyFrame)[1]

        if len(fourPoints) >= 4:
            newFourPoints = []
            newFourPoints.append(fourPoints[0])
            newFourPoints.append(fourPoints[1])
            newFourPoints.append(fourPoints[len(fourPoints) - 2])
            newFourPoints.append(fourPoints[len(fourPoints) - 1])

            newSquareContours = []
            newSquareContours.append(fourContours[0])
            newSquareContours.append(fourContours[1])
            newSquareContours.append(fourContours[len(fourContours) - 2])
            newSquareContours.append(fourContours[len(fourContours) - 1])

            for cnt in newSquareContours:
                area = cv2.contourArea(cnt)
                self.sqrAvrArea += area

            self.sqrAvrArea = int(self.sqrAvrArea / 4)

            newFourPoints = np.array(newFourPoints, dtype="float32")
            return four_point_transform(frame, newFourPoints)
        else:
            return None

    def getOvalContours(self, adaptiveFrame):
        contours, hierarchy = cv2.findContours(adaptiveFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ovalContours = []

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0, True)
            ret = 0
            x, y, w, h = cv2.boundingRect(contour)

            # eliminating not ovals by approx lenght
            if (len(approx) > 15 and w / h <= 1.2 and w / h >= 0.8):

                mask = np.zeros(adaptiveFrame.shape, dtype="uint8")
                cv2.drawContours(mask, [contour], -1, 255, -1)

                ret = cv2.matchShapes(mask, contour, 1, 0.0)

                if (ret < 1):
                    ovalContours.append(contour)
                    self.bubbleWidthAvr += w
                    self.bubbleHeightAvr += h
        self.bubbleWidthAvr = self.bubbleWidthAvr / len(ovalContours)
        self.bubbleHeightAvr = self.bubbleHeightAvr / len(ovalContours)

        return ovalContours

    def x_cord_contour(self, ovalContour):
        x, y, w, h = cv2.boundingRect(ovalContour)

        return y + x * self.bubbleHeightAvr

    def y_cord_contour(self, ovalContour):
        x, y, w, h = cv2.boundingRect(ovalContour)

        return x + y * self.bubbleWidthAvr




def ocr(ruta):
    # Store Pdf with convert_from_path function
    # images = convert_from_path(ruta,poppler_path=r'C:\Users\56993\Downloads\poppler-0.68.0\bin')
    images = convert_from_path(ruta)
    
    imagenes=[]
    cantidadEncuestas=len(images)
    for i in range(len(images)):
        # Save pages as images in the pdf
        name='./tmp/encuesta-'+ str(i) +'.jpg'
        images[i].save(name, 'JPEG')
        imagenes.append(name)
        
    resp={0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0}
    cant={0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0}
    score = 0
    bandera=True
    bubbleSheetScanner = BubbleSheetScanner()

    for image in imagenes:
        a = cv2.imread(image)
        # x = 800
        # y = 500
        # ancho = 800
        # alto = 1500
        x = 760
        y = 460
        ancho = 1000
        alto = 1600
        # Recortamos la imagen utilizando cv2.crop()
        image = a[y:y+alto, x:x+ancho]
        # cv2.imshow('original',image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        h = int(round(600 * image.shape[0] / image.shape[1]))
        frame = cv2.resize(image, (600, h), interpolation=cv2.INTER_LANCZOS4)
        cannyFrame = bubbleSheetScanner.getCannyFrame(frame)
        warpedFrame = bubbleSheetScanner.getWarpedFrame(cannyFrame, frame)
        adaptiveFrame = bubbleSheetScanner.getAdaptiveThresh(warpedFrame)
        # cv2.imshow('original',adaptiveFrame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        ovalContours = bubbleSheetScanner.getOvalContours(adaptiveFrame)
        if (len(ovalContours) == bubbleSheetScanner.ovalCount):

            ovalContours = sorted(ovalContours, key=bubbleSheetScanner.y_cord_contour, reverse=False)
            
            for (q, i) in enumerate(np.arange(0, len(ovalContours), bubbleSheetScanner.bubbleCount)):
                
                bubbles = sorted(ovalContours[i:i + bubbleSheetScanner.bubbleCount], key=bubbleSheetScanner.x_cord_contour,
                                reverse=False)
                for (j, c) in enumerate(bubbles):
                    area = cv2.contourArea(c)
                    mask = np.zeros(adaptiveFrame.shape, dtype="uint8")
                    cv2.drawContours(mask, [c], -1, 255, -1)
                    mask = cv2.bitwise_and(adaptiveFrame, adaptiveFrame, mask=mask)
                    total = cv2.countNonZero(mask)
                    # answer = bubbleSheetScanner.ANSWER_KEY[q]
                    # x, y, w, h = cv2.boundingRect(c)
                    isBubbleSigned = ((float)(total) / (float)(area)) >= 0.5
                    if (isBubbleSigned):
                        # score=score+j+1
                        cant[q]=cant[q]+1 
                        resp[q]=resp[q]+j+1 
                        cv2.drawContours(warpedFrame, bubbles, j, (0, 255, 0), 2)
                    
            # # Add score
            # warpedFrame = cv2.putText(warpedFrame, 'Score:' + str(score),
            #                         (100, 12),
            #                         cv2.FONT_HERSHEY_SIMPLEX,
            #                         0.5,
            #                         (0, 0, 0),
            #                         1
            #                         )

            # cv2.imshow('result', warpedFrame)
            # cv2.waitKey(0)
        else:
            print('Revisar a mano, mas de una respuestas marcada por fila')



    for i in cant:
        if cant[i]>cantidadEncuestas:
            print('Revisar a mano, mas de una respuestas marcada por Pregunta')
            exit() 


    divididos = [round(value / cantidadEncuestas, 2) for value in resp.values()]
    print(cantidadEncuestas)
    # import pandas as pd
    # df = pd.DataFrame([[key, resp[key]] for key in resp.keys()], columns=['Pregunta', 'Promedio'])
    # fig = go.Figure([go.Bar(x=df['Pregunta'], y=df['Promedio'])])
    # fig.write_html("grafico_de_barras.html")
    # print(df)
    # exit()
    # datos
    x = [1,2,3,4,5,6,7,8,9,10,11]
    y = divididos
    print(divididos)

    label=y
    # creación de gráfico de barras
    yLabel = [f'{val}%' for val in label]
    x_labels = ["Pregunta 1", "Pregunta 2", "Pregunta 3", "Pregunta 4", "Pregunta 5",
                "Pregunta 6", "Pregunta 7", "Pregunta 8", "Pregunta 9", "Pregunta 10","Pregunta 11"]

    figs=[]
    layout = Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
            )
    fig = go.Figure(go.Bar(
                    x=x_labels,
                    y=y,
                    width=0.4,
                    # text=yLabel, # agregar texto encima de cada barra
                    # textposition='outside', # posición del texto
                    marker_color='#6ec63b',
                    textfont=dict(color='black')
                ),layout=layout)
    fig.update_layout(title='Promedio por Pregunta',title_x=.5)
    name='./tmp/graficoEncuesta.png'
    fig.write_image(name,scale=6)
    figs.append(name)
    
    
    
    preguntas=[
       "Los contenidos son pertinentes a los objetivos generales y específicos que aborda el curso",
       "El curso presenta una estructuración lógica de los contenidos que facilita su comprensión",
       "La metodología utilizada para impartir los conocimientos facilita alcanzar los objetivos de aprendizaje",
       "El relator muestra un alto nivel de conocimientos en el tema expuesto",
       "El relator muestra una buena disposición hacia los alumnos, resolviendo dudas y reforzando ideas principales",
       "El relator cumple con los horarios de inicio, receso y término de la actividad ",
       "El recinto en el cual se dicta la capacitación tiene adecuadas condiciones de higiene y seguridad",
       "El recinto en el cual se dicta la capacitación cuenta con adecuada iluminación, acústica y equipos audiovisuales",
       "El servicio de catering entregado cumple con estándares de calidad, acordes a lo comprometido",
       "El material de apoyo utilizado durante el curso (ppt, video,etc) están diseñados y presentados con calidad suficiente",
       "Se utilizan imágenes, gráficos, ejemplos o animaciones para facilitar su comprensión"
    ]
    # Crear la figura y agregar la tabla
    fig = go.Figure(go.Table(
        columnorder = [1,2],
        columnwidth = [80,500],
        header=dict(values=["Pregunta", "Promedio"],align='center',fill_color='#6ec63b',font=dict(color='white')),
        cells=dict(values=[preguntas, divididos],font_size=8,height=30),
    ),layout=layout)
    name='./tmp/tablaEncuesta.png'
    fig.update_layout(title='Tabla Promedio por Pregunta',title_x=.5)
    fig.write_image(name,scale=6)
    figs.append(name)
    promedioCurso=sum(divididos) / 11
    promedioRelator=(divididos[3]+divididos[4]+divididos[5])/3
    return figs,promedioCurso,promedioRelator