import pandas as pd

df=pd.read_csv('./tmp/'+'ejemplo.csv')
df = df.drop('rut', axis=1)
print(df)
print(df.to_html())