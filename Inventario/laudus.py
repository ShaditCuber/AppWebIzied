import requests
import json
import time
import datetime

HEADERS = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoiamtLQWZIekRXTmkzMjVveVFXeHBzeVFISVhMTjFXd2I3SmMyWG9LSFF6ZGh5aHpORFhHZkdFdzlKdVhoenpZQ3F4d3lMZnNUT3VjNDdaTUFySUlGV2lBMEV1ZlFtemtUajRyN2RTY1BpSWNCUG4xeHNuekNNTUpncTEweWZvamdtRXNldEdaZmV3WVVwMnZWcGxJOGtheENneGlXU3NHSktTMmR0aitmck9zZWlwZnVmYUxxNG5BUS80QkkzMlkxT0F6eWJ4ZFZIaEc2N1hlemdFYVFLRytFTFlXNHF6UHFUM2N3Z0ZxSVRQWkpXSXR1cGxCMEdjWVZUL3psOEs5Z3l6Zlg0ekVwbUg1NXBoRFZhYVRwOFVJU1RWRWFsbGIyZHRuMUNiWUZIM0pYNWNZOEloNEJKeFFEcndQUEdicDlnUlJTalUxNDNTYVQ5YStwV0Zhamo5Q0hOUGVDN0ttcjZBNm5IaVozbGFpT0tscThWUmlHajFzPSJ9.1bLy90S7ZpT6gSVk6aGO64wd0opZVq0tcfDRMg5UeDE',
  'Content-Type': 'application/json'
}
URL='https://api.laudus.cl/'


def validarToken():
    funcion='security/checkToken'
    data=requests.get(URL+funcion,headers=HEADERS).text
    return 'TOKEN_EXPIRED' not in data
         


def limpiarString(string_1):
    """Compara dos strings ignorando mayusculas, tildes y limpiandolas primero"""
    replaces = {'á':'a','é':'e','í':'i','ó':'o','ú':'u', 'ñ':'n'}
    string_1 = str(string_1).strip().lower().replace("  ","")
    for key, value in replaces.items():
        string_1 = string_1.replace(key, value)
    return string_1 

def crearProducto(sku:str,description:str,unitPrice:int):
    
    funcion='production/products'
    payload = """{{
    "sku": "{}",
    "description": "{}",
    "allowFreeDescription": "true",
    "barCode": "{}",
    "type": "s",
    
    "unitPrice": {},
    "unitOfMeasure": "unidad",
    "notes": "string",
    "createdBy": {{
        "userId": "st",
        "name": "string"
    }},
    "modifiedBy": {{
        "userId": "st",
        "name": "string"
        }}
    }}""".format(limpiarString(sku), limpiarString(description), limpiarString(sku), unitPrice)
    
    try:
        data=requests.post(URL+funcion,headers=HEADERS,data=payload).json()
        idProducto=data['productId']
        return idProducto
    except:
        return None
    

    

def eliminarProducto(idLaudus):
    funcion='production/products/'+str(idLaudus)
    data=requests.delete(URL+funcion,headers=HEADERS).text
    return 'error' in data
    

def actualizarProducto(idLaudus:str,description:str,unitPrice:str):
    funcion='production/products/{}'.format(idLaudus)
    payload = """{{
    "productId": {},
    "description": "{}",
    "allowFreeDescription": "true",
    "type": "s",
    
    "unitPrice": {},
    "unitOfMeasure": "unidad",
    "notes": "string",
    "createdBy": {{
        "userId": "st",
        "name": "string"
    }},
    "modifiedBy": {{
        "userId": "st",
        "name": "string"
        }}
    }}""".format(idLaudus,limpiarString(description), unitPrice)
    data=requests.put(URL+funcion,headers=HEADERS,data=payload).json()
    return data['productId']!=None

def crearBodega(nombre:str):
    funcion='production/warehouses'
    payload="""{{
    "name": "{}",
    "address": "Calle 2 Norte 376,Condominio Costa San Pedro",
    "city": "San Pedro de la Paz",
    "county": "Concepcion",
    "notes": "",
    "createdBy": {{
        "userId": "st",
        "name": "string"
    }},
    "modifiedBy": {{
        "userId": "st",
        "name": "string"
    }},
    }}""".format(nombre)
    data=requests.post(URL+funcion,headers=HEADERS,data=payload).json()
    return data['warehouseId']
    


def actualizarBodega(idBodega,nombre):
    funcion='production/warehouses/{}'.format(idBodega)
    payload="""{{
    "warehouseId": "{}",
    "name": "{}",
    "address": "Calle 2 Norte 376,Condominio Costa San Pedro",
    "city": "San Pedro de la Paz",
    "county": "Concepcion",
    }}""".format(idBodega,nombre)
    data=requests.put(URL+funcion,headers=HEADERS,data=payload).json()
    return data['warehouseId']!=None

def ingresoBodega(idWarehouse:str,idProduct:int,quantity:int):
    
    now = datetime.datetime.utcnow()
    iso_date = now.isoformat() + 'Z'
    funcion='production/inputs'
    payload="""{{
        "date": '{}',
        "warehouse": {{
            "warehouseId": '{}',
        }},
        "createdAt":'{}',
        "modifiedAt": '{}',
        "items": [
                {{
                "product": {{
                    "productId": {},
                }},
                "quantity": {},
                }}
                ]
    }}""".format(str(iso_date),str(idWarehouse),str(iso_date),str(iso_date),idProduct,quantity)
    data=requests.post(URL+funcion,headers=HEADERS,data=payload).json()
    print(data)

def salidaBodega(idWarehouse:str,idProduct:int,quantity:int):
    
    now = datetime.datetime.utcnow()
    iso_date = now.isoformat() + 'Z'
    funcion='production/outputs'
    payload="""{{
        "date": '{}',
        "warehouse": {{
            "warehouseId": '{}',
        }},
        "createdAt":'{}',
        "modifiedAt": '{}',
        "items": [
                {{
                "product": {{
                    "productId": {},
                }},
                "quantity": {},
                }}
                ]
    }}""".format(str(iso_date),str(idWarehouse),str(iso_date),str(iso_date),idProduct,quantity)
    data=requests.post(URL+funcion,headers=HEADERS,data=payload).json()
    print(data)
    
    

