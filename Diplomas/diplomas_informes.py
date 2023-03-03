
import json
import boto3
import requests
import re
import os
from os import listdir
from os.path import join, isfile
import zipfile
import tempfile
from datetime import datetime
from PyPDF2 import PdfMerger

USERS_TO_IGNORE = [2, 3, 4, 117, 513, 847, 3535, 4023, 4260, 831, 16274] #IDs de admins, supervisores, etc
MOODLE_URL = "https://www.izied.com/"
MONDAY_API_URL = "https://api.monday.com/v2"

DIPLOMA_FILE_COLUMN_NAME = "Diplomas"

TOKEN = '339aa39958e934fe16e3f21464b7b96a'
TOKEN_CERT = 'adaba7cfeb8a2fdb4c20373601296357'
monday_api_key = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI"


FUNCTION_GET_GRADE_ITEMS = 'gradereport_user_get_grade_items'
FUNCTION_GET_ISSUEDCERTS = 'local_certs_get_issued'
FUNCTION_GET_COURSEMODULEID = 'local_certs_get_course_customcerts'
FUNCTION_FORCE_ISSUES = 'local_certs_force_issue'
FUNCTION_GET_COURSE_BY_FIELD = 'core_course_get_courses_by_field'
FUNCTION_GET_ENROLLED_USERS = 'core_enrol_get_enrolled_users'
FUNCTION_FORCE_ISSUES_ARCHIVE = "local_certs_get_issued_archive"

URL = "https://www.izied.com"
ENDPOINT="/webservice/rest/server.php"

RE_DIGIT = re.compile('\d')

NOTA_MINIMA = 1.00
NOTA_APROBACION = 4.00


BUCKET_KEY = 'informes-diplomas'
s3_client = boto3.client('s3')


def process_nota(nota: str) -> None or float:
    if RE_DIGIT.search(nota):
        return float(nota.strip().replace(",","."))
    else:
        return None

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

def syncchallenge(event: dict):
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
            column_values{{ id title text }}
            assets {{ id url name public_url }}  }} }}'''
    data = {'query' : query}
    r = requests.post(url=MONDAY_API_URL, json=data, headers= {"Authorization" : monday_api_key})
    return r.json()["data"]["items"][0]

def lcomp(string_1: str, string_2: str) -> bool:
    """Compara dos strings ignorando mayusculas, tildes y limpiandolas primero"""
    replaces = {'á':'a','é':'e','í':'i','ó':'o','ú':'u', 'ñ':'n'}
    string_1 = str(string_1).strip().lower().replace("  ","")
    string_2 = str(string_2).strip().lower().replace("  ","")
    for key, value in replaces.items():
        string_1 = string_1.replace(key, value)
        string_2 = string_2.replace(key, value)
    return string_1 == string_2

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
    r = requests.post(url=MONDAY_API_URL, files=files, headers={"Authorization" : monday_api_key}).json()
    return r




def lambda_handler(courseid,fila):

    course = call(fname = FUNCTION_GET_COURSE_BY_FIELD, KEY = TOKEN, field = 'id', value = courseid).json()["courses"][0]
    enroled_users = (call(fname = FUNCTION_GET_ENROLLED_USERS, KEY = TOKEN,  courseid = courseid).json())

    notas = call(fname = FUNCTION_GET_GRADE_ITEMS, KEY = TOKEN, courseid = courseid, userid = 0).json()
    coursemoduleid = call(fname = FUNCTION_GET_COURSEMODULEID, KEY= TOKEN_CERT, courseid = courseid).json()[0]
    issued = call(fname = FUNCTION_GET_ISSUEDCERTS, KEY= TOKEN_CERT, coursemoduleid=coursemoduleid).json()

    notas = [(lambda x: dict(
                x, **{"finalgrade": next((grade for grade in x["gradeitems"] if grade["itemtype"] == "course"), None)}
            ))(usergrades) for usergrades in notas["usergrades"] if usergrades["userid"] not in USERS_TO_IGNORE]

    resultados_prueba = [
        {
            "userid" : persona["userid"],
            "nombre" : persona["userfullname"],
            "nota" : process_nota(persona["finalgrade"]["gradeformatted"])
        } for persona in notas
    ]

    aprobados = [(resultado["userid"], resultado["nota"]) for resultado in resultados_prueba if resultado["nota"] and resultado["nota"] >= NOTA_APROBACION]
    reprobados = [(resultado["userid"], resultado["nota"]) for resultado in resultados_prueba if resultado["nota"] and resultado["nota"] < NOTA_APROBACION]
    desertores = [(resultado["userid"], resultado["nota"]) for resultado in resultados_prueba if not resultado["nota"]]


    dips_faltantes = list(set([x[0] for x in aprobados]) - set([x["userid"] for x in issued]))

    if dips_faltantes:
        call(fname = FUNCTION_FORCE_ISSUES, KEY= TOKEN_CERT, coursemoduleid=coursemoduleid).json()
        issued_new = call(fname = FUNCTION_GET_ISSUEDCERTS, KEY= TOKEN_CERT, coursemoduleid=coursemoduleid).json()
        if len(issued_new) == len(issued):
            exit("Error asignando diplomas faltantes, revizar restricciones")
        else:
            issued = issued_new


    course_name = course["fullname"]
    course_shortname = course["shortname"]

    response = call(FUNCTION_FORCE_ISSUES_ARCHIVE, KEY=TOKEN_CERT, coursemoduleid = coursemoduleid)
    
    base_dir = "/tmp"
    file_name = os.path.join(base_dir, "downloaded.zip")
    
    with open(file_name, 'wb') as fd:
        fd.write(response.content)

    for issue in issued:
        issue["username"] = next((x["username"] for x in enroled_users if x["id"] == issue["userid"]), None)


    date_time = datetime.fromtimestamp(int(course["startdate"]))
    year = date_time.strftime("%Y")
    merger = PdfMerger()

    zf = zipfile.ZipFile(file_name)
    with tempfile.TemporaryDirectory(prefix= join(base_dir,"")) as tempdir:
        zf.extractall(tempdir)
        for file in  [f for f in listdir(tempdir) if isfile(join(tempdir, f))]:
            # print(file, " => ", next(( (x["username"] + ".pdf") for x in issued if file.split(".pdf")[0] == x["code"]), file))
      
            lc_path = join(tempdir,file)
            s3_path = year + "/" + course_shortname + "/" + next(( (x["username"] + ".pdf") for x in issued if file.split(".pdf")[0] == x["code"]), file)
            
            try:
                s3_client.upload_file(lc_path, BUCKET_KEY, s3_path)
                print(s3_path)
            except Exception as e:
                print(e)
                pass
            
            merger.append(lc_path)

        lc_path = join(tempdir, "Diplomas " + course_shortname + ".pdf")
        s3_path = year + "/" + course_shortname + "/" + "Diplomas " + course_shortname + ".pdf"
        merger.write(lc_path)
        merger.close()

        
        try:
            s3_client.upload_file(lc_path, BUCKET_KEY, s3_path)
            print(s3_path)
        except Exception as e:
            print(e)
            pass
        
        try:
            reponse = add_file_to_column(item_id= fila, filename= lc_path, file_column_id= 'archivo2')
            return True
        except Exception as e:
            print(reponse)
            print(e)


    # url = s3_client.generate_presigned_url(
    #                 ClientMethod='get_object',
    #                 Params={
    #                     'Bucket': BUCKET_KEY,
    #                     'Key': s3_path,
    #                     'ResponseContentDisposition' : 'attachment' 
    #                 },
    #                 ExpiresIn=(60*60*24*365)
    #                 )

    #courseid = 554

    return {
        'statusCode': 200,
        'body': json.dumps('Lamba Finished')
    }