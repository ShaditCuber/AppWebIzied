import pandas as pd

def leer(ruta):
    df=pd.read_csv('./tmp/'+ruta)
    print(df)