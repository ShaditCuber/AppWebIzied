import requests
import json
import time
import datetime
HEADERS = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXlsb2FkIjoiZzVBL2VQYVpOdDdpOGtvK2J0OXJkZDNZUDFhMHZ6SUxyS1kzWFhoOFdrNVdSRzBiV2RNaU5jNyt1c3l5MGtYK2tKaU5CVWR0cmNOMC84TXZqRGUzZUVSdUZyRFZ6SlQzM1RkN1RWWS9QSE1kK21BOGg1b21KdENoeS9aY2VUTVJaM0owZ3NUdTIrTzlmc2hncnc2YmFmNmxTcjFQWWNhbU9LOUlhdE1jWWNiRWU2bklJdWFONm9wQTZ1YWVmT0ZrL2g3QXc3cjIzWDF6RnJ1S0crdThuWHFNYWVwRGE5bTU5cmhPTGowNkNlTmxTZUhWb2hMdmE5R2JJbGN2SHJNQnFMTFdpbkdvbXhEZ0JtM0s2ZkYzVThkNmJseUNhTmxDeEt0enVkenpYTWFQcGFuK01LV1RiblcxUERoMmdkcUgxM1lVNDBzaU45d2hUUGFhdVZJNkd4bG81Z3hRajVhRHF1MUwxYXY4R0pnVHNtd0EyNDNoYkZZPSJ9.h81ci8nHkUMV-NsqRydaXKMyIk8did3TNDCIjgLkehw',
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
    
    
