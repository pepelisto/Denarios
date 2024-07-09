
import pandas as pd
import datetime

def descargar_datos(symbol, start_date=None):
    # Convert the start date to a Unix timestamp if provided
    if start_date:
        start_timestamp = int(datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    else:
        start_timestamp = 0

    # URL de Yahoo Finance para el símbolo especificado
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_timestamp}&period2=9999999999&interval=1d&events=history'

    # Descargar los datos utilizando pandas
    datos = pd.read_csv(url)

    return datos
# Llamar a la función para descargar los datos del par de divisas USDCLP

symbols = {'USDCLP': 'USDCLP=X', 'USDCOBRE': 'HG=F', 'USDPETROLEO': 'CL=F'}
start_date = '2014-01-01'

for key, value in symbols.items():
    datos = descargar_datos(symbol=value, start_date=start_date)
    print(datos)
    # datos.to_csv(key + '.csv', index=False)
