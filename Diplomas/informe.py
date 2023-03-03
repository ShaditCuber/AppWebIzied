from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PyPDF2 import PdfMerger
import json
import os
import math
from os.path import join, sep
import requests
import re
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from PIL import ImageDraw, Image
import numpy as np
import boto3
import botocore
import platform




base_dir = './static'

URL = "https://www.izied.com"
# URL = "http://52.23.33.192/moodle/"
ENDPOINT = "/webservice/rest/server.php"
TOKEN = "339aa39958e934fe16e3f21464b7b96a"
MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI'


FUNCTION_GET_GRADE_ITEMS = 'gradereport_user_get_grade_items'
FUNCTION_GET_COURSE_BY_FIELD = 'core_course_get_courses_by_field'
FUNCTION_GET_ENROLLED_USERS = 'core_enrol_get_enrolled_users'
FUNCTION_GET_COMPLETION = 'core_completion_get_activities_completion_status'
FUNCTION_GET_ACTIVITIES = 'core_course_get_contents'
FUNCTION_GET_QUIZZES_BY_COURSES = 'mod_quiz_get_quizzes_by_courses'
FUNCTION_GET_USER_ATTEMPTS = 'mod_quiz_get_user_attempts'
FUNCTION_GET_ATTEMPT_REVIEW = 'mod_quiz_get_attempt_review'
FUNCTION_GET_FEEDBACKS_BY_COURSE = 'mod_feedback_get_feedbacks_by_courses'
FUNCTION_GET_FEEDBACK_ANALYSIS= 'mod_feedback_get_analysis'
FUNCTION_GET_FEEDBACK_ITEMS= 'mod_feedback_get_items'

USERS_TO_IGNORE = [2, 3, 4, 117, 513, 847, 3535, 4023, 4260, 831, 16274] #IDs de admins, supervisores, etc
TRACKING_MODNAMES = ["scorm", "feedback", "quiz"]

RE_DIGIT = re.compile('\d')

DEFAULT_RELATORES_BOARD = "3549156018"

#COURSE BOARD
NAME_COLUMN_NAME        = "NOMBRE CURSO"
MOODLE_COLUMN_NAME      = "URL Curso"
CRONOGRAMA_COLUMN_NAME  = "DURACIÓN CURSO"
RELATORES_COLUMN_NAME   = "RELATOR REAL"
EMPRESA_COLUMN_NAME     = "Institución"
HORAS_CURSO_COLUMN_NAME = "HORAS TOTAL"
MODALIDAD_COLUMN_NAME   = "Modalidad"
BOARD_RELATION_COLUMN_NAME = "Enlace Tab. Sec."
INFORM_FILE_COLUMN_NAME = "Informe"
PROMEDIO_GENERAL_COLUMN_NAME = "Promedio Curso"
PROMEDIO_RELATOR_COLUMN_NAME = "Promedio Relator"

#RELATOR BOARD
RELATOR_NAME_COLUMN_NAME = "name"
RELATOR_RUT_COLUMN_NAME  = "Rut"
RELATOR_PROFESION_COLUMN_NAME = "Profesión"
RELATOR_FOTO_COLUMN_NAME = "Foto"

encuesta_desc = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.' \
    ' Integer vel blandit mi. Pellentesque molestie risus vitae dolor semper' \
    ' ultricies. Nullam malesuada ipsum leo, eu sagittis dolor cursus a. Morbi' \
    ' euismod velit pellentesque semper vulputate. Fusce varius interdum vulputate.' \
    ' Donec vulputate mauris urna, vitae elementum dolor interdum ac. Nunc sem dolor.'
prueba_desc = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus' \
    ' ipsum nisl, euismod quis aliquet eleifend, placerat a nibh. Sed vestibulum' \
    ' venenatis est eu ultricies. Etiam porttitor diam at ex pellentesque placerat' \
    ' eget sit amet turpis. Phasellus pretium volutpa.'

res_notas_desc = prueba_desc
progress_desc = encuesta_desc[0:200]
datos_desc = encuesta_desc[0:200]

COLOR_GRIS = [115, 115, 115]
COLOR_AZUL = [51, 76, 91]
COLOR_IZIED = [109, 197, 58]
COLOR_RED = [255, 97, 116]

FONTS = {
    'leagueSpartan' : ['leagueSpartan', '', join(base_dir, 'assets', 'fonts', 'league-spartan', 'LeagueSpartan-Bold.ttf')],
    'openSansLight' : ['openSansLight', '', join(base_dir, 'assets', 'fonts', 'Open_Sans', 'OpenSans-Light.ttf')],
    'openSansExtraBold' : ['openSansExtraBold', '', join(base_dir, 'assets', 'fonts', 'Open_Sans', 'OpenSans-ExtraBold.ttf')],
    'openSemiBold' : ['openSemiBold', '', join(base_dir, 'assets', 'fonts', 'Open_Sans', 'OpenSans-SemiBold.ttf')],
    'alikeRegular' : ['alikeRegular', '', join(base_dir, 'assets', 'fonts', 'Alike', 'Alike-Regular.ttf')]  
}

def will_it_float(val: str):
    try:
        float(val)
        return True
    except Exception as e:
        return False

def get_multi_cell_height(font: list, font_size: float or int, txt: str, align: str, w: float or int, h: float or int):
    temp_pdf = FPDF()
    temp_pdf.add_font(*font) #'openSansLight', '', join(base_dir, 'fonts', 'Open_Sans', 'OpenSans-Light.ttf')
    temp_pdf.set_font(font[0],'', font_size)
    temp_pdf.add_page(format = 'A4')
    #for name in stacks_names:
    temp_pdf.set_xy(0,0)
    temp_pdf.multi_cell(w=w, h=h, txt=txt, align=align)
    return (temp_pdf.get_y()) 

def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.

    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict==None:
        out_dict = {}
    if not type(in_args) in (list,dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args)==list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args)==dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, KEY, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.

    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})

    response = requests.post(URL+ENDPOINT, parameters)
    if type(response) == dict and response.get('exception'):
        raise SystemError("Error calling Moodle API\n", response)
    return response

def process_nota(nota: str) -> None or float:
    if RE_DIGIT.search(nota):
        return float(nota.strip().replace(",","."))
    else:
        return None

def custom_round(floating) -> str:
    """Redondea el valor como si fuera una nota"""
    entera = str(floating).split('.')[0]
    decimal = str(floating).split('.')[1]
    if (len(decimal)<=1):
        return floating
    if(int(decimal[1]) >= 5):
        decimal = str(int(decimal[0])+1)
    else:
        decimal = decimal[0]
    stringi = float(entera + "." + decimal)
    return stringi

def get_notas(courseid: int)-> dict:
    notas = call(fname = FUNCTION_GET_GRADE_ITEMS, KEY = TOKEN, courseid = courseid, userid = 0).json()
    notas = [(lambda x: dict(
                x, **{"finalgrade": next((grade for grade in x["gradeitems"] if grade["itemtype"] == "course"), None)}
            ))(usergrades) for usergrades in notas["usergrades"] if usergrades["userid"] not in USERS_TO_IGNORE]

    notas = [
        {
            "userid" : persona["userid"],
            "nombre" : persona["userfullname"],
            "nota" : ("0.0" if process_nota(persona["finalgrade"]["gradeformatted"]) is None else str(custom_round(process_nota(persona["finalgrade"]["gradeformatted"]))))
        } for persona in notas
    ]
    return sorted(notas, key=lambda d: float(d['nota']))

def get_quiz_questions(attempt_review: list)-> list[dict]:
    if attempt_review["attempt"]["state"] != "finished":
        exit("Error, enviado un intento sin terminar")
    questions = []
    for question in attempt_review["questions"]:
        soup = BeautifulSoup(question["html"],"html.parser")
        questions_texts = soup.find_all("div", {"class": "qtext"})
        questions.append({
            'slot' : question["slot"],
            'number' : question.get("number",0),
            'page' :  question["page"],
            'question' : questions_texts[0].text.strip(),
            'answers' : []
        })

    questions_by_blocks = []
    for page in list(set([question["page"] for question in questions])):
        block = {
            "page" : page, 
            "questions" : [],
            "header" : None
        }
        for question in questions:
            if question["page"] == page:
                if not question["number"]:
                    block["header"] = question["question"]
                else:
                    block["questions"].append(question)
        questions_by_blocks.append(block)
    return questions_by_blocks

def add_header_agregated(pdf: FPDF, agregated_values: dict, x: int=25, y: int=60)-> int:
    WIDHT = 160
    HEADERS = [
        { "txt" : "Matriculados", "icon" : "profile.png", "color" : [97, 136, 255]},
        { "txt" : "Aprobados", "icon" : "check.png", "color" : [0, 219, 187]},
        { "txt" : "Reprobados", "icon" : "cross.png", "color" : [255, 97, 116]},
        { "txt" : "Desertores", "icon" : "missing.png", "color" : [176, 176, 176]}
    ]

    X_RESUME_OFFSET = x
    Y_RESUME_OFFSET = y

    SEP = 5
    RESUME_ICONS_DIM = 5
    RESUME_TEXT_WIDTH = 30

    single_header_space = (WIDHT - (len(HEADERS)-1) * SEP * 2) / len(HEADERS)
    text_widht = single_header_space - RESUME_ICONS_DIM - math.floor(SEP/2)

    pdf.set_font('leagueSpartan','',10)
    pdf.set_text_color(*COLOR_GRIS)
    pdf.set_xy(X_RESUME_OFFSET, Y_RESUME_OFFSET)

    for i, head in enumerate(HEADERS):
        pdf.set_xy(x = X_RESUME_OFFSET + single_header_space * i + (SEP*2)*i, y = Y_RESUME_OFFSET)
        pdf.image(join(base_dir, 'assets', 'icons', head["icon"]), 
            x = pdf.get_x(), 
            y = pdf.get_y(), h= RESUME_ICONS_DIM)

        pdf.set_font('leagueSpartan','',10)
        pdf.set_text_color(*COLOR_GRIS)
        pdf.set_xy(
            x = pdf.get_x() + RESUME_ICONS_DIM + math.floor(SEP/2),  
            y = pdf.get_y())
            
        pdf.cell(w= text_widht, h= 6, txt= head["txt"], align= 'L', new_x=XPos.LEFT, new_y=YPos.NEXT, border=True)

        pdf.set_font('leagueSpartan','',20)
        pdf.set_text_color(*COLOR_AZUL)
        pdf.set_xy(
            x = pdf.get_x() - RESUME_ICONS_DIM - math.floor(SEP/2),# X_RESUME_OFFSET + single_header_space * i + (SEP*2)*i, 
            y = pdf.get_y())
        pdf.cell(w= RESUME_TEXT_WIDTH, h= 8, txt= str(agregated_values[head["txt"]]), align= 'L',
            new_x=XPos.LEFT, new_y=YPos.NEXT, border=True)

        pdf.set_draw_color(*head["color"])
        pdf.set_fill_color(*head["color"])
        pdf.rect(x = pdf.get_x() + 1, y= pdf.get_y(), style='DF',
            w=pdf.get_string_width(str(agregated_values["Matriculados"])), h=1, round_corners= True)

        pdf.rect(x = X_RESUME_OFFSET + single_header_space * i + (SEP*2)*i,
            y = Y_RESUME_OFFSET, 
            w = single_header_space,
            h = RESUME_ICONS_DIM + 8 + 1 + 1)
    
    return  Y_RESUME_OFFSET + RESUME_ICONS_DIM + 8 + 1 + 1

def make_bar_graph(pdf: FPDF, data: dict, x: float, y: float, w: float, h: float, bars_widht : float = 3.5):
    BAR_GRAPH_X = x  # 25
    BAR_GRAPH_Y = y  # 75
    BAR_GRAPH_W = w  # 160
    BAR_GRAPH_H = h  # 75

    BAR_GRAPH_LABELS_PAD = 6
    BAR_GRAPH_LABELS_FONT = 'openSansLight'
    BARS_LABEL_FONT = 'openSansLight'
    BARS_LABEL_FONT_SIZE = 10
    BAR_GRAPH_LABELS_FONT_SIZE = 10

    BARS_WIDTH = bars_widht
    BARS_TOP = BAR_GRAPH_Y + BAR_GRAPH_LABELS_PAD
    BARS_BOTTOM = BAR_GRAPH_Y + BAR_GRAPH_H - BAR_GRAPH_LABELS_PAD
    BARS_COLOR = COLOR_IZIED
    BARS_RED_COLOR = COLOR_RED

    BARS_INITIAL_X = BAR_GRAPH_X + BAR_GRAPH_LABELS_PAD + BARS_WIDTH
    BARS_FINAL_X = BAR_GRAPH_X + BAR_GRAPH_W - BARS_WIDTH * 2

    BAR_GRAPH_BARS = 6.0 #BASADO EN NOTAS 1 A 7 (6)

    max_bar_count = max(data.values())
    #max_bar_count = 30
    max_line_value = 5 * (math.ceil(max_bar_count/5.0))
    bar_space = (BARS_FINAL_X - BARS_INITIAL_X) / BAR_GRAPH_BARS
    max_bar = BARS_BOTTOM - BARS_TOP # for value max_line_value
    bar_unit_value = max_bar / float(max_line_value)
    bar_graph_line_count = 5 if bool(max_line_value%10) else 4

    graph_line_sep = (BAR_GRAPH_H - BAR_GRAPH_LABELS_PAD * 2) / bar_graph_line_count


    #set horizontal labels
    pdf.set_text_color(*COLOR_GRIS)
    pdf.set_font(BAR_GRAPH_LABELS_FONT,'', BAR_GRAPH_LABELS_FONT_SIZE)
    for i in range(bar_graph_line_count + 1):
        val = i * (max_line_value / bar_graph_line_count)
        val_str =  f'{val:.1f}' if not val.is_integer() else str(int(val))
        pdf.set_xy(BAR_GRAPH_X, BAR_GRAPH_Y + BAR_GRAPH_H - graph_line_sep * i - BAR_GRAPH_LABELS_PAD - (BAR_GRAPH_LABELS_PAD - 1)*0.5)
        pdf.cell(w=BAR_GRAPH_LABELS_PAD - 1 , h= BAR_GRAPH_LABELS_PAD - 1, txt= val_str, align='C')

    #set horizontal lines
    pdf.set_text_color(*COLOR_GRIS)
    pdf.set_font(BAR_GRAPH_LABELS_FONT,'', BAR_GRAPH_LABELS_FONT_SIZE)
    for i in range(bar_graph_line_count + 1):
        pdf.line(x1 = BAR_GRAPH_X + BAR_GRAPH_LABELS_PAD, 
            y1 = BAR_GRAPH_Y + BAR_GRAPH_H - graph_line_sep * i - BAR_GRAPH_LABELS_PAD,
            x2 = BAR_GRAPH_X + BAR_GRAPH_W,
            y2 = BAR_GRAPH_Y + BAR_GRAPH_H - graph_line_sep * i - BAR_GRAPH_LABELS_PAD
            )

    #dibujar barras
    pdf.set_font(BARS_LABEL_FONT,'',BARS_LABEL_FONT_SIZE)
    for key, value in data.items():
        if float(key) >= 4.0:
            pdf.set_fill_color(*BARS_COLOR)
        else:
            pdf.set_fill_color(*BARS_RED_COLOR)
        bar_height = value * bar_unit_value
        bar_x =  BARS_INITIAL_X + (float(key)-1.00) * bar_space
        pdf.rect(x = bar_x, y= BARS_BOTTOM - bar_height,
            style='F', w=BARS_WIDTH, h=bar_height, round_corners=("TOP_LEFT", "TOP_RIGHT"))

        #bar count legend  
        pdf.set_text_color(*COLOR_AZUL)
        pdf.set_xy(bar_x, BARS_BOTTOM - bar_height - BARS_WIDTH)
        pdf.cell(w=BARS_WIDTH, h= BARS_WIDTH, txt=str(value), align='C')
        
        #bar nota legend
        pdf.set_text_color(*COLOR_GRIS)
        pdf.set_xy(bar_x, BARS_BOTTOM + 1)
        pdf.cell(w=BARS_WIDTH, h= BARS_WIDTH, txt=str(key), align='C')

    #bars set legends
    pdf.set_text_color(*[0,0,0])
    for val in ['1.0', '4.0', '7.0']:
        pdf.set_xy(BARS_INITIAL_X + (float(val)-1.0) * bar_space, BARS_BOTTOM + 1)
        pdf.cell(w=BARS_WIDTH, h= BARS_WIDTH, txt=val, align='C')

def make_stacked_graph(pdf: FPDF, data: dict, x: float, y: float, w: float, h: float, stacks_widht : float = 3.5):
    STACK_GRAPH_X = x  # 25
    STACK_GRAPH_Y = y  # 75
    STACK_GRAPH_W = w  # 160
    STACK_GRAPH_H = h  # 75

    STACK_GRAPH_LABELS_PAD = 6
    STACK_GRAPH_LABELS_H_PAD = 10
    STACK_GRAPH_LABELS_FONT = 'openSansLight'
    STACK_GRAPH_LABELS_FONT_SIZE = 10
    STACKS_LABEL_FONT = 'openSansLight'
    STACKS_LABEL_FONT_SIZE = 10

    #nuevo
    STACKS_WIDTH = STACK_GRAPH_LABELS_H_PAD # labels en vez de width
    STACKS_TOP = STACK_GRAPH_Y + STACK_GRAPH_LABELS_PAD
    STACKS_BOTTOM = STACK_GRAPH_Y + STACK_GRAPH_H - STACK_GRAPH_LABELS_PAD

    STACKS_COLOR = COLOR_IZIED

    STACKS_INITIAL_X = STACK_GRAPH_X + STACK_GRAPH_LABELS_H_PAD + STACKS_WIDTH
    STACKS_FINAL_X = STACK_GRAPH_X + STACK_GRAPH_W - STACK_GRAPH_LABELS_H_PAD * 2

    stacks_values = [val for sublist in [list(mod["elements"].values()) for mod in list(data.values())] for val in sublist]
    stacks_names = [val for sublist in [list(mod["elements"].keys()) for mod in list(data.values())] for val in sublist]
    
    stacks_labels_heights = []

    max_stack_count = max(stacks_values)
    max_line_value = max_stack_count
    stack_space = (STACKS_FINAL_X - STACKS_INITIAL_X) / (len(stacks_values) - 1)
 
    for name in stacks_names:
        stacks_labels_heights.append(get_multi_cell_height(font=FONTS['openSansLight'],
            font_size=STACK_GRAPH_LABELS_FONT_SIZE * 0.75, txt=str(name), align='C', w=stack_space, h=STACK_GRAPH_LABELS_PAD))

    max_stack = STACKS_BOTTOM - STACKS_TOP # for value max_line_value
    stack_unit_value = max_stack / float(max_line_value)
    stack_graph_line_count = 4 
    graph_line_sep = max_stack / stack_graph_line_count
    
    poligon_cords = ((STACKS_INITIAL_X, STACKS_BOTTOM),)

    pdf.set_text_color(*COLOR_AZUL)
    for i, (val, name, ls_heights) in enumerate(zip(stacks_values, stacks_names, stacks_labels_heights)):
        poligon_cords += ((STACKS_INITIAL_X + i * stack_space, STACKS_BOTTOM - stack_unit_value * float(val)),)
        
    poligon_cords += ((STACKS_FINAL_X, STACKS_BOTTOM),)
    pdf.set_fill_color(*STACKS_COLOR)
    pdf.polygon(poligon_cords, style="F")

    for i, (val, name, ls_heights) in enumerate(zip(stacks_values, stacks_names, stacks_labels_heights)):
        pdf.set_font(STACK_GRAPH_LABELS_FONT,'', STACK_GRAPH_LABELS_FONT_SIZE)
        pdf.set_xy(STACKS_INITIAL_X + i * stack_space - STACK_GRAPH_LABELS_PAD / 2, STACKS_BOTTOM - stack_unit_value * float(val) - STACK_GRAPH_LABELS_PAD)
        pdf.cell(w=STACK_GRAPH_LABELS_PAD, h= STACK_GRAPH_LABELS_PAD, txt=str(val), align='C', fill=False)
        
        val_offset = pdf.get_string_width(str(val))
        val_str =  (f'%{((val*100.0)/max_stack_count):.0f}').split(".0")[0]

        pdf.set_font(STACK_GRAPH_LABELS_FONT,'', STACK_GRAPH_LABELS_FONT_SIZE * 0.75)
        pdf.set_xy(pdf.get_x() + val_offset/2 - STACK_GRAPH_LABELS_PAD/2, pdf.get_y())
        pdf.cell(w=STACK_GRAPH_LABELS_PAD, h= STACK_GRAPH_LABELS_PAD, txt=val_str, align='L', fill=False)

        #print item labels
        pdf.set_font(STACK_GRAPH_LABELS_FONT,'', STACK_GRAPH_LABELS_FONT_SIZE * 0.75)
        pdf.set_xy(STACKS_INITIAL_X + i * stack_space - stack_space / 2, STACKS_BOTTOM)
        pdf.multi_cell(w=stack_space, h= ((STACK_GRAPH_LABELS_FONT_SIZE * 0.75)**2) /ls_heights, txt=str(name), align='C', fill= False, border=True)
        # deberia ser STACK_GRAPH_LABELS_FONT_SIZE * 0.75  = 5
        # es ls_heights = 15  => (STACK_GRAPH_LABELS_FONT_SIZE * 0.75) ^ 2 / ls_heights

    #set horizontal labels
    pdf.set_text_color(*COLOR_GRIS)
    pdf.set_font(STACK_GRAPH_LABELS_FONT,'', STACK_GRAPH_LABELS_FONT_SIZE)
    for i in range(stack_graph_line_count + 1):
        val = i * (100 / stack_graph_line_count)
        val_str =  f'{val:.1f}' if not val.is_integer() else str(int(val))
        pdf.set_xy(STACK_GRAPH_X, STACKS_BOTTOM - i * graph_line_sep - (STACK_GRAPH_LABELS_PAD - 1)*0.5)
        pdf.cell(w=STACK_GRAPH_LABELS_H_PAD - 1 , h= STACK_GRAPH_LABELS_PAD - 1, txt= val_str + " %", align='C')

    #set horizontal lines
    pdf.set_text_color(*COLOR_GRIS)
    pdf.set_font(STACK_GRAPH_LABELS_FONT,'', STACK_GRAPH_LABELS_FONT_SIZE)
    for i in range(stack_graph_line_count + 1):
        pdf.line(x1 = STACK_GRAPH_X + STACK_GRAPH_LABELS_H_PAD, 
            y1 = STACKS_BOTTOM - i * graph_line_sep,
            x2 = STACK_GRAPH_X + STACK_GRAPH_W,
            y2 = STACKS_BOTTOM - i * graph_line_sep
            )

    return

def get_attempts(quizids: list[int], userids : list[int]) -> list[dict]:
    attempts = []
    for quizid in quizids:
        for userid in userids:
            user_attempts = call(fname = FUNCTION_GET_USER_ATTEMPTS, KEY = TOKEN, quizid  = quizid, userid = userid, status = "finished", includepreviews = 1).json()
            if len(user_attempts["attempts"]) > 1:
                attempts.append( max(user_attempts["attempts"], key=lambda x:x['sumgrades']) )
            else:
                if user_attempts["attempts"]:
                    attempts.append(user_attempts["attempts"][0])
    return attempts

def get_quiz_answers(attempts: list[dict]) -> list[dict]:
    questions = get_quiz_questions(call(fname = FUNCTION_GET_ATTEMPT_REVIEW, KEY = TOKEN, attemptid = attempts[0]["id"], page  = -1).json())
    for atmps in attempts:
        if atmps:
            attempt_review = call(fname = FUNCTION_GET_ATTEMPT_REVIEW, KEY = TOKEN, attemptid = atmps["id"], page  = -1).json()
            for qst in attempt_review["questions"]:
                qst["html"] = None
                for page in questions:
                    for question in page["questions"]:
                        if question["slot"] == qst["slot"]:
                            question["answers"].append(qst["status"])
    return questions

def agregate_notas(notas: list[float]) -> dict:
    agregated_values = {
        "Matriculados" : len(notas),
        "Aprobados" : len([nota for nota in notas if will_it_float(nota["nota"]) and float(nota["nota"]) >= 4.0]),
        "Reprobados" : len([nota for nota in notas if will_it_float(nota["nota"]) and 1.0 < float(nota["nota"]) < 4.0])
    }
    agregated_values["Desertores"] = agregated_values["Matriculados"] - agregated_values["Aprobados"] - agregated_values["Reprobados"]
    return agregated_values

def get_modules(courseid: int) -> list[dict]:
    mods = call(fname = FUNCTION_GET_ACTIVITIES, KEY = TOKEN, courseid = courseid, options = [
        { "name" : "excludecontents", "value" : True}
    ]).json()

    modules = []
    for x in [mod for mod in mods if any([element for element in mod["modules"] if element["modname"] in TRACKING_MODNAMES])]:
        modules.append({
            "modid" : x["id"],
            "modname" : x["name"],
            "elements" : [
                {
                    "elementid" : y["id"],
                    "elementname" : y["name"],
                    "elementtype" : y["modname"]
                } for y in x["modules"] if y["modname"] in TRACKING_MODNAMES
            ]
        })
    return modules

def get_module_completion_by_users(modules: list[dict], courseid: int, userids: list[int]) -> list[dict]:
    completaciones = []
    for user in userids:
        completions = call(fname = FUNCTION_GET_COMPLETION, KEY = TOKEN, courseid = courseid, userid = user["id"]).json()["statuses"]
        completaciones.append({
            "id" : user["id"],
            "fullname" : user["fullname"],
            "username" : user["username"],
            "completiondata" : [{
                "modname" : mod["modname"],
                "modid" : mod["modid"],
                "elements" : [
                    {
                        "elementname" : element["elementname"],
                        "elementtype" : element["elementtype"],
                        "elementcompletion" : next((x["state"] for x in completions if x["cmid"] == element["elementid"]) , 0) in [1,2],
                        "elementid" : element["elementid"]
                    } for element in mod["elements"]
                ] 
            } for mod in modules]
        })
    return completaciones

def get_completion_status(completaciones: list, userid = int, activityid = id) -> bool:
    for comp in completaciones:
        if comp["id"] == userid:
            for mod in comp["completiondata"]:
                for element in mod["elements"]:
                    if element["elementid"] == activityid:
                        return element["elementcompletion"]

def get_feedback_questions(feedbackid: int) -> list[dict]:
    feedback_items = call(fname = FUNCTION_GET_FEEDBACK_ITEMS, KEY = TOKEN, feedbackid = feedbackid).json()
    feedback_items["items"].pop(0)

    questions = []
    page = 0
    for question in feedback_items["items"]:
        try:
            soup = BeautifulSoup(question["presentation"],"html.parser")
            question_text = soup.find_all("p")[0].text.strip()
        except Exception as e:
            question_text = question["name"]        
        if not question["required"]:
            page += 1
        questions.append({
            'slot' : question["position"],
            'number' : question.get("itemnumber",0),
            'page' :  page,
            'question' : question_text,
            'answers' : []
        })

    questions_by_blocks = []
    for page in list(set([question["page"] for question in questions])):
        block = {
            "page" : page, 
            "questions" : [],
            "header" : None
        }
        for question in questions:
            if question["page"] == page:
                if not question["number"]:
                    block["header"] = question["question"]
                else:
                    block["questions"].append(question)
        questions_by_blocks.append(block)
    return questions_by_blocks

def get_feedback_answers(feedbackid: int) -> list[dict]:
    questions = get_feedback_questions(feedbackid = feedbackid)
    feedback_analysis = call(fname = FUNCTION_GET_FEEDBACK_ANALYSIS, KEY = TOKEN, feedbackid = feedbackid).json()

    for item in feedback_analysis["itemsdata"]:
        answers = [json.loads(x) for x in item["data"]]
        for answ in answers:
            answ["answertext"] = answ["answertext"].strip()
        for page in questions:
            for question in page["questions"]:
                if question["number"] == item["item"]["itemnumber"]:
                    question["answers"].extend(answers)
    return questions

def add_circle_graph(pdf: FPDF, x: int, y: int, w: int, h: int, val: int or float, txt: str) -> None:
    pdf.image(name = join(base_dir, 'assets', 'icons', 'disk.svg'), 
        x= x, y= y, w=w, h=h)
    for i in range(100):
        if i < val:
            with FPDF.rotation(pdf, angle=-(360 / 100) * i, x=x + w/2, y=y + h/2):
                pdf.image(name = join(base_dir, 'assets', 'icons', 'green percent.svg'), 
                    x= x, y= y, w=w, h=h)
        else:
            with FPDF.rotation(pdf, angle=-(360 / 100) * i, x=x + w/2, y=y + h/2):
                pdf.image(name = join(base_dir, 'assets', 'icons', 'grey percent.svg'), 
                    x= x, y= y, w=w, h=h)
        
    pdf.set_text_color(*COLOR_IZIED)
    pdf.set_xy(x= x, y= y + h/2.0 - (h*0.5)/2.0)
    pdf.set_font('leagueSpartan','', h*0.5 )
    pdf.cell(w= w, h=h*0.5, txt= txt, align= 'C')

def draw_resume(pdf: FPDF, answers: list[dict], title: str, desc: str) -> None:
    CIRCLE_X = 25
    CIRCLE_Y = 80 # 20
    CIRCLE_W = 30
    CIRCLE_H = 30
    TEXT_SPAN = 40
    SEP = 5
    INNER_SEP = 10

    CENTER_H = False
    CENTER_LAST = True
    BOTTOM_OF_PAGE = 280

    pdf.image(join(base_dir, 'assets', 'base', 'background.png'), x = 0, y = 0, w = 210, h = 297)
    pdf.set_text_color(*COLOR_AZUL)
    pdf.set_font('leagueSpartan','',28)
    pdf.set_xy(40,42)
    pdf.multi_cell(w = 160, h = 9, txt = title, align = 'L')
    
    pdf.set_font('openSansLight','',12)
    pdf.set_xy(25,60)
    pdf.multi_cell(w = 160, h = 9, txt = desc, align = 'J')

    if answers[0]["header"] is None:
        corrected_answers = [{
            'header': "PRUEBA NO SEPARADA POR CONTENIDOS",
            'page': 0,
            'questions': []
        }]
        for i, page in enumerate(answers):
            for question in page["questions"]:
                corrected_answers[0]["questions"].append(question)
        answers = corrected_answers

    expected_height = math.ceil(len(answers)/2) * CIRCLE_H + SEP * math.floor((len(answers) -1)/2)
    if expected_height < CIRCLE_H: expected_height = CIRCLE_H

    if CENTER_H:
        CIRCLE_Y = pdf.get_y() + (BOTTOM_OF_PAGE - pdf.get_y()) / 2 - expected_height / 2
    else:
        CIRCLE_Y = pdf.get_y() + 15

    topics = get_course_feedback_topics_averages(feedback_answers=answers)
    for i, topic in enumerate(topics):
        expected_height_text = get_multi_cell_height(
                font=FONTS['leagueSpartan'], font_size= 10, txt=topic["header"], align='C', w=TEXT_SPAN, h=5)

        if (i % 2):
            _x = CIRCLE_X + CIRCLE_W + TEXT_SPAN + SEP + INNER_SEP
        else:
            if i == (len(answers)-1) and CENTER_LAST:
                _x = CIRCLE_X + (CIRCLE_W + TEXT_SPAN + SEP + (INNER_SEP/2)) / 2
            else:
                _x = CIRCLE_X

        add_circle_graph(pdf = pdf, 
            # x = CIRCLE_X,
            x = _x,
            y = CIRCLE_Y + (SEP + CIRCLE_H) * (math.floor(i/2)), 
            w = CIRCLE_W, h = CIRCLE_H, val = topic["rel_val"], txt = topic["val_str"])
        pdf.set_text_color(*COLOR_AZUL)
        pdf.set_font('leagueSpartan', '', 10)
        # pdf.set_xy(x= CIRCLE_X + CIRCLE_W + SEP, y= CIRCLE_Y + (SEP + CIRCLE_H) * (math.floor(i/2)) + CIRCLE_H/2 - expected_height_text/2)
        pdf.set_xy(x= _x + CIRCLE_W + SEP, y= CIRCLE_Y + (SEP + CIRCLE_H) * (math.floor(i/2)) + CIRCLE_H/2 - expected_height_text/2)
        pdf.multi_cell(w= TEXT_SPAN, h=5, txt=topic["header"], align= 'C', border=True)
        
    pdf.rect(CIRCLE_X, CIRCLE_Y, (CIRCLE_W + SEP + TEXT_SPAN)*2 + INNER_SEP, expected_height)

def lcomp(string_1: str, string_2: str) -> bool:
    """Compara dos strings ignorando mayusculas, tildes y limpiandolas primero"""
    replaces = {'á':'a','é':'e','í':'i','ó':'o','ú':'u', 'ñ':'n'}
    string_1 = str(string_1).strip().lower().replace("  ","")
    string_2 = str(string_2).strip().lower().replace("  ","")
    for key, value in replaces.items():
        string_1 = string_1.replace(key, value)
        string_2 = string_2.replace(key, value)
    return string_1 == string_2

def syncchallenge(event: dict) -> dict or None:
    try:
        event_body = json.loads(event['body'])
        challenge = {'challenge' : event_body['challenge']}
        return challenge
    except Exception as e:
        return

def get_item_by_id(element_id: str)->dict:
    """
        busca en el elemento con el id element_id, retorna el elemento con sus columnas
    """
    query =f'''{{
        items (ids: {str(element_id)}) {{ id name
            column_values{{ id title text value}}
            assets {{ id url name public_url }}  }} }}'''
    data = {'query' : query}
    r = requests.post(url=MONDAY_API_URL, json=data, headers= {"Authorization" : MONDAY_API_KEY})
    return r.json()["data"]["items"]

def get_items_by_multiple_column_values(board_id: str, column_id: str, column_values: list[str])->dict:
    """
        busca en los elementos del tablero con id board_id, en la columna con id column_id, valores de la lista column_values,
        retorna el elemento con sus columnas
    """
    query =f'''{{
        items_by_multiple_column_values (board_id: {str(board_id)}, column_id: "{str(column_id)}", column_values: ["{'", "'.join(column_values)}"]) {{
            id
            name
                column_values{{ id title text }}
                assets {{ id url name public_url }}  }} }}'''
    data = {'query' : query}
    r = requests.post(url=MONDAY_API_URL, json=data, headers= {"Authorization" : MONDAY_API_KEY})
    return r.json()["data"]["items_by_multiple_column_values"]

def current_date_format(date: datetime) -> str:
    """Compone string para el informe con el formato "dd de mm del yyyy" en español"""
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)
    return messsage

def get_stringed_timeslot(curso_inicio: str, curso_final: str) -> str:
    sameyear = str(curso_inicio).split("-")[0] in str(curso_final).split("-")[0]
    samemonth = str(curso_inicio).split("-")[1] in str(curso_final).split("-")[1]

    curso_inicio_str= current_date_format(parser.parse(curso_inicio))
    curso_final_str = current_date_format(parser.parse(curso_final))

    stringed_time_slot = 'Realizado desde el '
    if sameyear:
        if samemonth:
            stringed_time_slot += curso_inicio_str.split()[0] + " al "
            stringed_time_slot += curso_final_str
        else:
            stringed_time_slot += curso_inicio_str.split(" del ")[0] + " al "
            stringed_time_slot += curso_final_str
    else:
        stringed_time_slot += curso_inicio_str + " al " + curso_final_str + "."
    return stringed_time_slot

def get_thumbnail_for_relator(url: str, out_size: tuple[int, int] = [200,200]) -> str:
    fname = url.split("/")[-1].split("?")[0]

    resp = requests.get(url)
    if resp.status_code == 200:
        with open(join(sep,"tmp", fname), 'wb') as fd:
            fd.write(resp.content)
    else:
        return None
    
    img = Image.open(join(sep,"tmp", fname))

    img = img.crop((
        (img.size[0] - min(img.size))/2.0,
        (img.size[1] - min(img.size))/2.0,
        ((img.size[0] - min(img.size))/2.0) + (min(img.size)),
        ((img.size[1] - min(img.size))/2.0) + (min(img.size)),
            ))

    h,w = img.size

    lum_img = Image.new('L',[h,w] ,0) 
    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0,0),(h,w)],0,360,fill=255)

    img_arr = np.array(img)
    lum_img_arr = np.array(lum_img)
    
    img_arr = img_arr[:,:,:3] # REMOVER ALPHA/TRANSPARENCIA

    final_img_arr = np.dstack((img_arr, lum_img_arr))

    final_img = Image.fromarray(final_img_arr)
    final_img = final_img.resize(out_size, Image.Resampling.LANCZOS)

    save_path = join(sep,"tmp", fname.split(".")[0] + ".png")
    final_img.save(save_path)
    return save_path

def get_course_by_itemid(itemid: int)->dict:
    curso = get_item_by_id(element_id= itemid)[0]

    courseid = 716
    if not courseid:
        exit("No se encontro la columna 'Enlace' para identificar el curso en plataforma")

    values = json.loads(next((x["value"] for x in curso["column_values"] if lcomp(x["title"], RELATORES_COLUMN_NAME)), None))

    columns_curso = {
        NAME_COLUMN_NAME : next((col["text"] for col in curso["column_values"] if lcomp(col["title"], NAME_COLUMN_NAME)), None),
        "id" : 716,
        "relatoresids" : [val["linkedPulseId"] for val in values["linkedPulseIds"]] if values else values,
        INFORM_FILE_COLUMN_NAME : next((col["id"] for col in curso["column_values"] if lcomp(col["title"], INFORM_FILE_COLUMN_NAME)), None),
        CRONOGRAMA_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], CRONOGRAMA_COLUMN_NAME)), None),
        MOODLE_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], MOODLE_COLUMN_NAME)), None),
        RELATORES_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], RELATORES_COLUMN_NAME)), None),
        EMPRESA_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], EMPRESA_COLUMN_NAME)), None),
        HORAS_CURSO_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], HORAS_CURSO_COLUMN_NAME)), None),
        MODALIDAD_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], MODALIDAD_COLUMN_NAME)), None),
        BOARD_RELATION_COLUMN_NAME : next((x["text"] for x in curso["column_values"] if lcomp(x["title"], MODALIDAD_COLUMN_NAME)), None),
        PROMEDIO_GENERAL_COLUMN_NAME : next((x["id"] for x in curso["column_values"] if lcomp(x["title"], PROMEDIO_GENERAL_COLUMN_NAME)), None),
        PROMEDIO_RELATOR_COLUMN_NAME : next((x["id"] for x in curso["column_values"] if lcomp(x["title"], PROMEDIO_RELATOR_COLUMN_NAME)), None)
    }

    if None in columns_curso.values():
        exit("Columnas importantes no encontradas o vacias en el curso : " + str([i for i in columns_curso if columns_curso[i] is None]))
    return columns_curso

def get_course_relatores(relatores_ids: list[int])->list[dict]:
    datos_relatores = []
    for rel_id in relatores_ids:
        relator = get_item_by_id(element_id= rel_id)[0]
        if not relator:
            exit("Relator no encontrado, revisar nombre o tabla de relatores")
        datos_relatores.append(relator)

    columns_relatores = [
        {
            RELATOR_NAME_COLUMN_NAME : next((x["text"] for x in rel["column_values"] if lcomp(x["title"], RELATOR_NAME_COLUMN_NAME)), rel.get(RELATOR_NAME_COLUMN_NAME)),
            RELATOR_RUT_COLUMN_NAME : next((x["text"] for x in rel["column_values"] if lcomp(x["title"], RELATOR_RUT_COLUMN_NAME)), None),
            RELATOR_PROFESION_COLUMN_NAME : next((x["text"] for x in rel["column_values"] if lcomp(x["title"], RELATOR_PROFESION_COLUMN_NAME)), None),
            RELATOR_FOTO_COLUMN_NAME : next((x["public_url"] for x in rel["assets"] if lcomp(
                    x["url"], 
                    next((y["text"] for y in rel["column_values"] if lcomp(y["title"], RELATOR_FOTO_COLUMN_NAME)), "")
                )), "")
        } for rel in datos_relatores
    ]

    if any([None in cols_rel.values() for cols_rel in columns_relatores]):
        exit("Columnas importantes no encontradas o vacias en el relator: " + str(next((cols_rel for cols_rel in columns_relatores if None in cols_rel.values()), None)))
    return columns_relatores

def add_intro_page(pdf: FPDF, course: dict, relatores: list[dict]) -> None:
    curso_inicio = course[CRONOGRAMA_COLUMN_NAME].split(" - ")[0]
    curso_final = course[CRONOGRAMA_COLUMN_NAME].split(" - ")[1]

    pdf.add_page(format='A4')
    pdf.image(join(base_dir, 'assets', 'base', 'backgroundnohand.png'), x = 0, y = 0, w = 210, h = 297)
    pdf.set_text_color(*COLOR_AZUL) 
    now = datetime.now()

    pdf.set_font('openSansLight','',16)
    pdf.set_xy(25,50)
    pdf.multi_cell(w = 160, h = 9,
        txt = "San Pedro de la Paz, {}, Rodrigo Villablanca Cuevas, director de " \
        "IZIED (anteriormente Sociedad Huellas Capacitaciones SpA), envía las " \
        "siguientes conclusiones basadas en la capacitación:".format(current_date_format(now)),
        align = 'J')

    height = get_multi_cell_height(font = FONTS['leagueSpartan'], 
        font_size = 16, txt = course[NAME_COLUMN_NAME], align = 'C', w = 160, h = 9)

    pdf.set_font('leagueSpartan','',16)
    pdf.set_xy(25,85 + (130 - 85)/2 - height/2)
    pdf.multi_cell(w = 160, h = 9, txt = course[NAME_COLUMN_NAME], align = 'C')

    pdf.set_font('openSansLight','',16)
    pdf.set_xy(25,130)
    pdf.multi_cell(w = 160, h = 9, txt = get_stringed_timeslot(curso_inicio, curso_final), align = 'J')


    if len(relatores) == 1:
        pdf.set_font('leagueSpartan','',14)
        pdf.set_xy(25,180)
        pdf.multi_cell(w = 160, h = 9, txt = 'RELATOR', align = 'L')
        padd_x = 25
        if relatores[0][RELATOR_FOTO_COLUMN_NAME]:
            foto = get_thumbnail_for_relator(url= relatores[0][RELATOR_FOTO_COLUMN_NAME])
            if foto:
                pdf.image(foto, x = 25, y = 190 + 2.5, w = 30, h = 30) 
                padd_x = 60
                

        pdf.set_font('openSansLight','',16)
        pdf.set_xy(padd_x,190)
        pdf.multi_cell(w = 160, h = 9,
            txt = """{0}
        Rut: {1}
        Correo Electrónico: contacto@huellascapacitaciones.cl
        Profesión: {2}""".format(
                relatores[0][RELATOR_NAME_COLUMN_NAME], 
                relatores[0][RELATOR_RUT_COLUMN_NAME], 
                relatores[0][RELATOR_PROFESION_COLUMN_NAME]),
            align = 'L')
    else:
        pdf.add_page(format = 'A4')
        pdf.image(join(base_dir, 'assets', 'base', 'background.png'), x = 0, y = 0, w = 210, h = 297)
        pdf.set_text_color(*COLOR_AZUL)
        pdf.set_font('leagueSpartan','',28)
        pdf.set_xy(40,42)
        pdf.multi_cell(w = 190, h = 5, txt = 'Relatores', align = 'L')

        base_y = 60
        for relator in relatores:
            padd_x = 25
            if relator[RELATOR_FOTO_COLUMN_NAME]:
                foto = get_thumbnail_for_relator(url= relator[RELATOR_FOTO_COLUMN_NAME])
                if foto:
                    pdf.image(foto, x = 25, y = base_y + 2.5, w = 30, h = 30)  
                    padd_x = 60

            pdf.set_font('leagueSpartan','',14)
            pdf.set_xy(padd_x, base_y)
            pdf.multi_cell(w = 160, h = 9, txt = relator[RELATOR_NAME_COLUMN_NAME], align = 'L')
                
            pdf.set_font('openSansLight','',16)
            pdf.set_xy(padd_x, base_y+10)
            pdf.multi_cell(w = 160, h = 9,
                txt = """Rut: {0} \nCorreo Electrónico: contacto@huellascapacitaciones.cl \nProfesión: {1}""".format(
                    relator[RELATOR_RUT_COLUMN_NAME], 
                    relator[RELATOR_PROFESION_COLUMN_NAME]), 
                align = 'L')
            base_y += 50

def add_grade_report(pdf: FPDF, data: dict) -> None:
    agregated_values = agregate_notas(notas = data)
    bars = {}
    for nota in [nota for nota in data if will_it_float(nota["nota"]) and 1.0 < float(nota["nota"])]:
        if nota["nota"] in bars:
            bars[nota["nota"]] += 1
        else:
            bars[nota["nota"]] = 1
    bars.pop("Desertado", None)

    pdf.image(join(base_dir, 'assets', 'base', 'background.png'), x = 0, y = 0, w = 210, h = 297)
    pdf.set_text_color(*COLOR_AZUL)
    pdf.set_font('leagueSpartan','',28)
    pdf.set_xy(40,42)
    pdf.multi_cell(w = 160, h = 9, txt = 'Resumen de Notas', align = 'L')

    new_y = add_header_agregated(pdf = pdf, agregated_values = agregated_values, x = 25, y = 60)
    pdf.set_font('openSansLight','',12)
    pdf.set_xy(25, new_y + 3)
    pdf.multi_cell(w = 160, h = 9, txt = res_notas_desc, align = 'J', new_y= YPos.NEXT)

    pdf.set_font('openSansLight','',18)
    pdf.set_xy(x=25, y=pdf.get_y() + 5)
    pdf.cell(w = 160, h = 9, txt = 'Notas', align = 'C', new_y= YPos.NEXT)

    make_bar_graph(pdf=pdf, data=bars, x=25, y=pdf.get_y(), w=160, h=90, bars_widht=5)

def add_completion_report(pdf: FPDF, data: list[dict], users: list):
    stacks = { 0 : {
        'elements' : {
            'Matriculado' : len(users)
        },
        'modname' : "Matricula"
    }}

    for completed in data:
        for mod in completed["completiondata"]:
            if mod["modid"] not in stacks:
                stacks[mod["modid"]] = {
                    "modname" : mod["modname"].title(),
                    "elements" : {}
                }
            for element in mod["elements"]:
                if element["elementname"].title() not in stacks[mod["modid"]]["elements"]:
                    stacks[mod["modid"]]["elements"][element["elementname"].title()] = 0
                else:
                    if element["elementcompletion"]:
                        stacks[mod["modid"]]["elements"][element["elementname"].title()] += 1

    pdf.image(join(base_dir, 'assets', 'base', 'background.png'), x = 0, y = 0, w = 210, h = 297)
    pdf.set_text_color(*COLOR_AZUL)
    pdf.set_font('leagueSpartan','',28)
    pdf.set_xy(40,42)
    pdf.cell(w = 160, h = 9, txt = 'Resumen de Progreso', align = 'L')

    pdf.set_font('openSansLight','',12)
    pdf.set_xy(25,60)
    pdf.multi_cell(w = 160, h = 9, txt = progress_desc, align = 'J', new_y= YPos.NEXT)

    make_stacked_graph(pdf= pdf, data=stacks, x=25, y=pdf.get_y() + 5, w=160, h=90)

def crear_carta_recomendacion(columns_curso: dict, filename: str, columns_relatores: list[dict]) -> str:
    pdf_carta=FPDF()
    pdf_carta.add_page(format = 'A4')
    pdf_carta.image(join(base_dir, 'assets', 'base', 'icono_izied.png'), x = 0, y = 0, w = 210, h = 297)
    pdf_carta.add_font(*FONTS['alikeRegular'])
    pdf_carta.set_font('alikeRegular','',28)
    pdf_carta.set_text_color(*COLOR_AZUL) 
    pdf_carta.set_draw_color(*COLOR_GRIS)


    pdf_carta.set_xy(25,40)
    pdf_carta.set_font('alikeRegular','',12)

    pdf_carta.multi_cell(w = 160, h = 9,
        txt = 'La persona que suscribe esta carta certifica que, IZIED ' \
            '(anteriormente Sociedad Huellas Capacitaciones SpA), rut: ' \
            '76.199.438-7, ha realizado el curso abajo mencionado, cumpliendo ' \
            'de manera satisfactoria, seria y responsable la ejecución del mismo.',
        align = 'J', new_x = XPos.LEFT, new_y=YPos.NEXT)
    fecha_ahora = datetime.now()
    horas_curso_numero = str(columns_curso[HORAS_CURSO_COLUMN_NAME])
    if not(columns_curso[HORAS_CURSO_COLUMN_NAME].isnumeric()):
        horas_curso_numero = re.findall(r'\d+', columns_curso[HORAS_CURSO_COLUMN_NAME])
        horas_curso_numero=str(horas_curso_numero).replace('[','').replace(']','').replace("'",'') + ""
    
    pdf_carta.set_xy(x=pdf_carta.get_x(),y=pdf_carta.get_y()+10)
    pdf_carta.multi_cell(w = pdf_carta.get_string_width("Cantidad de Horas") + 2, h = 9,
        txt = ("Curso\n" \
            "Establecimiento\n"\
            "Modalidad\n"\
            "Cantidad de Horas\n"\
            "Fecha Realización"),
        align = 'L', new_x = XPos.RIGHT, new_y=YPos.TOP)
    pdf_carta.multi_cell(w = 160 + 25 - pdf_carta.get_x(), h = 9,
        txt = (": {0}\n" \
            ": {1}\n"\
            ": {2}\n"\
            ": {4} Horas\n"\
            ": {3}").format( 
                columns_curso[NAME_COLUMN_NAME], 
                columns_curso[EMPRESA_COLUMN_NAME], 
                columns_curso[MODALIDAD_COLUMN_NAME], 
                get_stringed_timeslot(
                    columns_curso[CRONOGRAMA_COLUMN_NAME].split(" - ")[0], 
                    columns_curso[CRONOGRAMA_COLUMN_NAME].split(" - ")[-1]),
                columns_curso[HORAS_CURSO_COLUMN_NAME]),
        align = 'L', new_x = XPos.RIGHT, new_y = YPos.NEXT)
    
    pdf_carta.set_xy(x=25,y=pdf_carta.get_y()+10)

    if len(columns_relatores) == 1:
        pdf_carta.multi_cell(w = 160, h = 9,
            txt = ('El/La relator(a) que estuvo a cargo de este curso es {0}, ' \
                'quien realizó la docencia del curso de forma adecuada, ' \
                'demostrando conocimiento y experiencia en el tema.').format(columns_relatores[0][RELATOR_NAME_COLUMN_NAME]),
            align = 'J', new_x = XPos.LEFT, new_y=YPos.NEXT)
    else:
        pdf_carta.multi_cell(w = 160, h = 9,
            txt = ('Los relatores que estuvieron a cargo de este curso son {0}, ' \
                'quienes realizaron la docencia del curso de forma adecuada, ' \
                'demostrando conocimiento y experiencia en el tema.').format( ', '.join([rel[RELATOR_NAME_COLUMN_NAME] for rel in columns_relatores])),
            align = 'J', new_x = XPos.LEFT, new_y=YPos.NEXT)
            

    pdf_carta.set_xy(x=25,y=pdf_carta.get_y()+5)
    pdf_carta.multi_cell(w = 160, h = 9,
        txt = 'Sociedad Huellas Capacitaciones spa cumplió de manera satisfactoria, ' \
            'seria y responsable con la realización del curso antes señalado.',
        align = 'J', new_x = XPos.LEFT, new_y=YPos.NEXT)
    
    
    pdf_carta.set_xy(x=25,y=pdf_carta.get_y()+5)
    pdf_carta.multi_cell(w = pdf_carta.get_string_width("Nombre") + 2, h = 9,
        txt = ('FIRMA\n' \
            'Nombre\n' \
            'Cargo'),
        align = 'L', new_x = XPos.RIGHT, new_y=YPos.TOP)
    pdf_carta.multi_cell(w = 160 + 25 - pdf_carta.get_x(), h = 9,
        txt = (": \n: \n:"),
        align = 'L', new_x = XPos.LEFT, new_y=YPos.BMARGIN)


    pdf_carta.set_xy(x=15,y=pdf_carta.get_y()-15)
    pdf_carta.set_font('alikeRegular','',10)
    pdf_carta.multi_cell(w = 160, h = 9,
        txt = 'Fecha: {0}'.format(current_date_format(fecha_ahora)),
        align = 'L', new_x = XPos.LEFT)
    pdf_carta.output(filename)

def get_course_feedback_topics_averages(feedback_answers: list[dict]) -> list[dict]:
    topics = []
    for page in feedback_answers:
        header = page["header"]
        agregated = 0
        count = 0
        for question in page["questions"]:
            # print("question:", str(page["header"]))
            if type(question["answers"][0]) == dict:
                for answer in question["answers"]:
                    agregated += answer["answercount"] * int(answer["answertext"])
                    # print("answer:",str(int(answer["answertext"])), ",count:", str(answer["answercount"]))
                    count += answer["answercount"]
            else:
                for answer in question["answers"]:
                    if 'Correcta' == answer:
                        agregated += 1
                    count += 1 
        val = agregated/count
        if val > 1.0: #NOTA NUMERICA
            val_str = f'{custom_round(val):.1f}'
            true_val = custom_round(val)
            val = (val / 7.00) * 100
        else: #PORCENTAJE
            val = 100 * val
            val_str = f'{val:.0f}%'
            true_val = val
        topics.append({
            "header" : header,
            "rel_val" : val,
            "true_val" : true_val,
            "val_str" : val_str
        })
    return topics

def write_table(pdf: FPDF, notas: dict, completaciones: list[dict], modules: list[dict]):
    WIDTH = 160
    GRADE_LENGHT = 20
    MODULE_LENGHT = 25
    
    max_name_lenght = max([pdf.get_string_width(nota["nombre"]) for nota in notas])

    pdf.image(join(base_dir, 'assets', 'base', 'background.png'), x = 0, y = 0, w = 210, h = 297)
    pdf.set_text_color(*COLOR_AZUL)
    pdf.set_font('leagueSpartan','',28)
    pdf.set_xy(40,42)
    pdf.multi_cell(w = 190, h = 5, txt = 'Datos', align = 'L')

    pdf.set_font('openSansLight','',12)
    pdf.set_xy(25,60)
    pdf.multi_cell(w = 160, h = 9, txt = datos_desc, align = 'J', new_y= YPos.NEXT) 

    pdf.set_fill_color(15,15,15)

    pdf.set_xy(x=20, y=pdf.get_y() + 10)

    pdf.set_font('openSansLight','',10)
    pdf.cell(w= max_name_lenght, h= 6, txt= "NOMBRE", align= 'C', border=True)
    pdf.cell(w= GRADE_LENGHT, h= 6, txt= "NOTA", align= 'C', border=True)

    for mod in modules:
        for element in mod["elements"]:
            with FPDF.rotation(pdf, angle=360, x=pdf.get_x() + MODULE_LENGHT/2, y=pdf.get_y() + 3):
                pdf.multi_cell(w= MODULE_LENGHT, h= 6, txt= element["elementname"], align= 'C', new_y= YPos.TOP, border=True)
            pdf.set_xy(pdf.get_x(), pdf.get_y())

    pdf.set_xy(pdf.get_x(), pdf.get_y()+10)

    for nota in notas:
        pdf.set_xy(20, pdf.get_y() + 6)
        pdf.cell(w= max_name_lenght, h= 6, txt= nota["nombre"], align= 'C', border=True)
        pdf.set_xy(pdf.get_x(), pdf.get_y())  
        pdf.set_font('leagueSpartan','',10)
        if nota["nota"] not in ["1.0", "0.0"]:
            pdf.cell(w= GRADE_LENGHT, h= 6, txt=(str(nota["nota"])), align= 'C', border=True)
        else:
            pdf.set_font('leagueSpartan','',6)
            pdf.cell(w= GRADE_LENGHT, h= 6, txt="DESIERTO", align= 'C', border=True)

        pdf.set_font('openSansLight','',10)
        for mod in modules:
            for element in mod["elements"]:
                pdf.cell(w= MODULE_LENGHT, h= 6, txt= 
                    str(get_completion_status(completaciones=completaciones, userid=nota["userid"], activityid=element["elementid"])), 
                align= 'C', border=True)

def add_file_to_column(item_id: str, filename: str = '/example.pdf', file_column_id: str = 'archivo72', filetype: str = 'application/pdf'):
    q = f"""
            mutation add_file($file: File!) {{
                add_file_to_column (
                            item_id: {int(item_id)},
                            column_id: {file_column_id},
                            file: $file) {{ id }}
            }}
        """
    try:
        files = {
            'query': (None, q, filetype),
            'variables[file]': (filename.split(os.path.sep)[-1], open(filename, 'rb'), 'multipart/form-data', {'Expires': '0'})
        }
    except Exception as e:
        print(e)
    r = requests.post(url=MONDAY_API_URL, files=files, headers={"Authorization" : MONDAY_API_KEY}).json()
    pprint(r)
    return r

def change_column_value(item_id: str, board_id: str, column_id: str, value: str):
    q = f"""
            mutation {{
                change_column_value(item_id: {str(item_id)}, board_id: {str(board_id)}, column_id: {str(column_id)}, 
                    value: "{str(value)}" ) {{ id }}
            }}
        """
    data = {'query' : q}
    r = requests.post(url=MONDAY_API_URL, json=data, headers= {"Authorization" : MONDAY_API_KEY})
    pprint(r.json())
    return r.json()

def lambda_handler(fila, context):
    

    columns_curso = get_course_by_itemid(itemid = fila)
        
    courseid = columns_curso["id"]
    
    columns_relatores = get_course_relatores(relatores_ids = columns_curso["relatoresids"])

    pdf = FPDF()

    for v in FONTS.values():
        pdf.add_font(*v)

    add_intro_page(pdf = pdf, course = columns_curso, relatores = columns_relatores)

    quizzes = call(fname = FUNCTION_GET_QUIZZES_BY_COURSES, KEY = TOKEN, courseids = [courseid]).json()
    quizzes_ids = [quiz["id"] for quiz in quizzes["quizzes"]]

    enroled_users = (call(fname = FUNCTION_GET_ENROLLED_USERS, KEY = TOKEN,  courseid = courseid).json())
    enroled_users = [user for user in enroled_users if user["id"] not in USERS_TO_IGNORE]
    enroled_users_ids = [user["id"] for user in enroled_users]

    attempts = get_attempts(quizids = quizzes_ids, userids = enroled_users_ids)
    attempts_answers = get_quiz_answers(attempts= attempts)

    pdf.add_page(format = 'A4')
    draw_resume(pdf= pdf, answers=attempts_answers, title = 'Cumplimiento de Objetivos', desc = prueba_desc)

    notas = get_notas(courseid = courseid)

    pdf.add_page(format = 'A4')
    add_grade_report(pdf = pdf, data = notas)

    feedbacks = call(fname = FUNCTION_GET_FEEDBACKS_BY_COURSE, KEY = TOKEN, courseids = [courseid]).json()
    feedbackid = next((feedback["id"] for feedback in feedbacks["feedbacks"] if "satisfacc" in feedback["name"].lower()), None)

    feedback_items = get_feedback_questions(feedbackid = feedbackid)
    feedback_answers = get_feedback_answers(feedbackid = feedbackid)

    modules = get_modules(courseid = courseid)
    completaciones = get_module_completion_by_users(modules = modules, courseid = courseid, userids = enroled_users)

    pdf.add_page(format= 'A4')
    add_completion_report(pdf, completaciones, enroled_users)

    pdf.add_page(format= 'A4')
    write_table(pdf=pdf, notas=notas, completaciones=completaciones, modules=modules)

    pdf.add_page(format='A4')
    draw_resume(pdf = pdf, answers = feedback_answers, title = 'Evaluación de la Capacitación', desc = encuesta_desc)
    
    pdf.output('./tmp/testlambda.pdf')

    merger = PdfMerger()
    merger.append(join(base_dir, "assets", "base", "portada.pdf"))
    merger.append('./tmp/testlambda.pdf')
    merger.write('./tmp/testlambda2.pdf')
    merger.close()
    inform_file_name = './tmp/testlambda2.pdf'

    # add_file_to_column(item_id= incoming_event['pulseId'], filename= inform_file_name, file_column_id= columns_curso[INFORM_FILE_COLUMN_NAME])

    
    topics = get_course_feedback_topics_averages(feedback_answers)
    rel_topic = next((topic["true_val"] for topic in topics if lcomp("Relator", topic["header"])), 0.0)
    promedio = sum([x["true_val"] for x in topics]) / len(topics)
    rounded_promedio = f'{(custom_round(promedio)):.1f}'
    # change_column_value(item_id= incoming_event['pulseId'], board_id=incoming_event['boardId'], column_id= columns_curso[PROMEDIO_GENERAL_COLUMN_NAME], value=rounded_promedio)
    # change_column_value(item_id= incoming_event['pulseId'], board_id=incoming_event['boardId'], column_id= columns_curso[PROMEDIO_RELATOR_COLUMN_NAME], value=rel_topic)

    if promedio >= 5.00:
        carta_file_name = './tmp/CartaRecomendacion.pdf'
        crear_carta_recomendacion(columns_curso= columns_curso, filename= carta_file_name, columns_relatores= columns_relatores)
        # add_file_to_column(item_id= incoming_event['pulseId'], filename= carta_file_name, file_column_id= columns_curso[INFORM_FILE_COLUMN_NAME])


        

if __name__ == "__main__":
    lambda_handler('3836689992', None)
    