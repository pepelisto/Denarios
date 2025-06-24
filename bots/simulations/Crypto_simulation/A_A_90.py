from Funciones import DB_habndle
import pandas as pd
import datetime
import numpy as np
from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from datetime import timedelta

# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from app.models import *

def anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit, sim_number, sim_info):
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    close_date_ = df.loc[idx, 'timestamp']
    try:
        matching_row = df5[df5['timestamp'] == close_date_].index[0]
    except:
        return
    factor_ajuste = None
    for i in range(matching_row, matching_row - 48, -1):
        row_data = df5.iloc[i]
        type_ = po.type
        high = row_data['High']
        low = row_data['Low']
        close = row_data['Close']
        close_date_ = row_data['timestamp']
        tp_p = po.tp_price
        sl_p = po.sl_price
        alteraciones = po.atr
        tp_period = False
        sl_period = False
        ajuste = False
        if type_ == 'BUY':
            if high >= tp_p:
                tp_period = True
            if low <= sl_p:
                sl_period = True
            if tp_period and not sl_period:
                DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                          sim_number, sim_info, close_method='TP')
                return
            elif not tp_period and sl_period:
                DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                          sim_number, sim_info, close_method='SL')
                return
            elif tp_period and sl_period:
                tp_indicator = high - tp_p
                sl_indicator = sl_p - low
                if tp_indicator > sl_indicator:
                    DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                              sim_number, sim_info, close_method='TP')
                    return
                else:
                    DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                              sim_number, sim_info, close_method='SL')
                    return

            # aumento = (close - po.entry_price) / po.entry_price
            # if aumento > (alteraciones + 1) * factor_ajuste:
            #     ajuste = True
            #     stop_loss = sl_p + po.entry_price * factor_ajuste
            #     take_profit = tp_p + po.entry_price * factor_ajuste

        else:
            if low <= tp_p:
                tp_period = True
            if high >= sl_p:
                sl_period = True
            if tp_period and not sl_period:
                DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                          sim_number, sim_info, close_method='TP')
                return
            elif not tp_period and sl_period:
                DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                          sim_number, sim_info, close_method='SL')
                return
            elif tp_period and sl_period:
                tp_indicator = tp_p - low
                sl_indicator = high - sl_p
                if tp_indicator > sl_indicator:
                    DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                              sim_number, sim_info, close_method='TP')
                    return
                else:
                    DB_habndle.close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste,
                                              sim_number, sim_info, close_method='SL')
                    return

        #     aumento = -((close - po.entry_price) / po.entry_price)
        #     if aumento > (alteraciones + 1) * factor_ajuste:
        #         ajuste = True
        #         stop_loss = sl_p - po.entry_price * factor_ajuste
        #         take_profit = tp_p - po.entry_price * factor_ajuste
        #
        # if ajuste:
        #     alt = alteraciones + 1
        #     update_position(po, alt, stop_loss)

def agripina(s, symbol, df, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return

    long = df.loc[idx, 'pullback_confirmed_long']
    short = df.loc[idx, 'pullback_confirmed_short']

    if long or short:
        entry_price_ = df.loc[idx, 'Close']
        open_date_ = df.loc[idx, 'timestamp']
        symbol_ = s
        atr = df.loc[idx, 'atr']
        if long:
            # quantity_ = round(25 + (15 * (rsi - 50)), 0)
            sl_price = entry_price_ - atr
            sl_factor = (sl_price / entry_price_) - 1
            quantity_ = 100
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit:
                sl_price = entry_price_ * (1 - sl_limit)

        else:
            # quantity_ = round(25 + (15 * (50 - rsi)), 0)
            sl_price = entry_price_ + atr
            sl_factor = (sl_price / entry_price_) - 1
            quantity_ = 100
            type_ = 'SELL'
            if sl_factor > sl_limit:
                sl_price = entry_price_ * (1 + sl_limit)

        DB_habndle.create_position(symbol_, type_, entry_price_, quantity_, open_date_, None, None, sl_price, sl_tp_ratio)
        DB_habndle.update_opportunities(op, type='OPEN')

def simulator():
    path = "../samples/Crypto_Get_samples/Get_row_data/USDT9/1h/"
    path5 = "../samples/Crypto_Get_samples/Get_row_data/USDT9/5m/"
    symbols = Symbol.objects.filter(find_in_api=True)
    i = 1
    for s in symbols:
        print("simulando " + str(s.symbol) + " - " + str(i))
        i += 1
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = min(len(df), 10000)
        csv_file_path5 = f"{path5}{symbol}_simulation_with_indicators.csv"
        df5 = pd.read_csv(csv_file_path5)
        for v3 in [2]:
            sl_tp_ratio = v3
            for v5 in [0]:
                sl_low_limit = v5
                for v4 in [0.1]:
                    sl_limit = v4
                    sim_number = 90
                    sim_info = "ratio 1.2"
                    for idx in range(num_rows - 150, -1, -1):
                        anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit, sim_number, sim_info)
                        agripina(s, symbol, df, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                    op = Oportunities_sim.objects.get(symbol_id=s.pk)
                    DB_habndle.update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                    try:
                        Open_position_sim.objects.get(symbol_id=s.pk).delete()
                    except:
                        pass
simulator()

