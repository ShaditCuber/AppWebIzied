import requests
import json
import time
import datetime
HEADERS = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoidEVoL0swZDh2Rnp6SU9QQm5xZld5OFJRRTdUb0hlN3pCTnQ3aHI4SHFHT3I2azJFS2FIeS9UOEZOdkxaVnhOOWFCb2J1dkZrY00xejgySTAvcU5hVUdtU0x0UmZYWUEvbjA1NjlReTZheGhyMlhiWFpJSjdvdGZicFQrV2krdzg1V1JTQXFwQXNVNWkyV1NPQlRadEg2NUlOWXpQSGMvcmJ3c3NPbWV1SW05TjlCUUt3ZG1qSVJ4ZEdsanlQcGpYMWF2MHk4eS9ZWkRTWFZJUWo5QjduR3RrSWVVRUZTMGFRUVk5eEMva3RJRE1YL0FpUWhMOHhwM09jOENHNXZYN25rUTdGTTlhM2Z5NDdUSlg5dnp5LzJRcnNla3dmZEdvTklmaDRwbmRTRVRxbGRQV1BtdGlFc1R4K1hBZU9YbmNqUy9XaXFhRmxGcHkyV0o0WGZEQlQxM28zdlhKTWtVZVo0cWRCTEhSS1B1WVJXV21aYXZXUnJFPSJ9.KjEkKB16cVe6TIaOFM76TUsbi-zscLbIudaOfyLvGao',
  'Content-Type': 'application/json'
}
URL='https://api.laudus.cl/'
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
    }}""".format(sku, description, sku, unitPrice)
    data=requests.post(URL+funcion,headers=HEADERS,data=payload).json()
    print(data)
    time.sleep(5)
    try:
        idProducto=data['productId']
        return idProducto
    except:
        return None
    

    

def eliminarProducto(idLaudus):
    funcion='production/products/'+str(idLaudus)
    data=requests.delete(URL+funcion,headers=HEADERS).text
    return 'error' in data
    

def actualizarProducto():
    pass

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
    
    
