from bots.simulations.samples.Crypto_Get_samples.Get_row_data.CryptoAnalyzerSimulatorBuy4 import CryptoAnalyzer
from datetime import datetime, timedelta
import django
import pandas as pd

#
# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

interval = '15m'
m = 15
candles = 1100
limit = 400 + candles
periodos = 21

symbols_queryset = Symbol.objects.filter(find_in_api=True)#.filter(id__gt=38)
symbols = [symbol.symbol for symbol in symbols_queryset]

# symbols = ['BTCBUSD']

for s in symbols:
    # Initialize an empty list to store the individual data frames
    data_frames_list = []
    sy = [s]
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=candles * m)
    for p in range(periodos):
        data_frame = CryptoAnalyzer(symbols=sy, interval=interval, limit=limit, end_date=end_date, candles=candles).analyze_crypto()
        data_frames_list.append(data_frame)
        end_date = start_date
        start_date = end_date - timedelta(minutes=candles * m)


    # Concatenate the list of data frames into one
    combined_data_frame = pd.concat(data_frames_list, ignore_index=True)
    combined_data_frame.to_csv(f"USDT6/15m/{s}_simulation.csv", index=False)
    # print("simbol pronto:  " + str(sy))