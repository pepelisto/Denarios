from bots.simulations.samples.Crypto_Get_samples.CryptoAnalyzerSimulatorBuy4 import CryptoAnalyzer
from datetime import datetime, timedelta
from django.conf import settings
import django
import pandas as pd
from Denarios.settings import DATABASES, INSTALLED_APPS

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

interval = '15m'
m = 30
candles = 1100
limit = 400 + candles
periodos = 14

symbols_queryset = Symbol.objects.filter(find_in_api=True)[24:]
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
    combined_data_frame.to_csv(f"samples/USDT/2023_30m/{s}_simulation.csv", index=False)
    print(combined_data_frame)