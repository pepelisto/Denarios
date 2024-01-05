from django.conf import settings
import django
from bots.notUsed.A_A.functions.CryptoAnalyzer import CryptoAnalyzer
import time
import datetime
from bots.notUsed.A_A_desarrollo.desarollo.Agripina_class import Agripina

from Denarios.settings import DATABASES, INSTALLED_APPS
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from app.models import *


def traeder():
    symbols = Optimum_parameter.objects.filter(timeframe=15).order_by('-pnl')
    for s in symbols:
        symbols = [s.symbol.symbol]
        interval = '15m'
        limit = 100
        df = CryptoAnalyzer(symbols=symbols, interval=interval, limit=limit).analyze_crypto()
        df = df[::-1].reset_index(drop=True)
        stoch_buy = 20
        stoch_sell = 80
        rsi_buy = 50 + s.open_rsi
        rsi_sell = 50 - s.open_rsi
        sl_tp_ratio = s.tp_sl_ratio
        sl_limit = s.sl_limit
        sl_low_limit = s.sl_low_limit
        Agripina(s, df, sl_tp_ratio, sl_limit, sl_low_limit, timeframe).agripina(s, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, sl_tp_ratio, sl_limit, sl_low_limit)

def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        minutes_to_next_interval = (15 - current_time.minute % 15) % 15
        next_start_time = current_time + datetime.timedelta(minutes=minutes_to_next_interval, seconds=30, microseconds=0)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time}")
        time.sleep(remaining_time)
        traeder()
        print("Executing your task.")


run_scheduled_pattern()

