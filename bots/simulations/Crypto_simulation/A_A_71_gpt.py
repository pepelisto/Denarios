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
    factor_ajuste = po.ratr
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

def agripina(s, symbol, df,  stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    macdhistogram = df.loc[idx, 'MACD histogram']
    macdhistogram_previo = df.loc[idx + 1, 'MACD histogram']
    srsik = df.loc[idx, 'St k']
    srsid = df.loc[idx, 'St d']
    rsi = df.loc[idx, 'RSI']
    ema_100 = df.loc[idx, 'ema_100']
    ema_50 = df.loc[idx, 'ema_50']
    close = df.loc[idx, 'Close']

    #---------------------check the stochastich rsi indicators ----------------------------------------
    if srsik >= stoch_sell and srsid >= stoch_sell:
        if op.type != 'SELL':
            DB_habndle.update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
    elif srsik <= stoch_buy and srsid <= stoch_buy:
        if op.type != 'BUY':
            DB_habndle.update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)
    # ----------------------check the bearish indicators   ----------------------------------------
    if op.type == 'SELL':
        if srsik <= 0.20 or srsid <= 0.20:
            DB_habndle.update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
        else:
            if not op.macd and macdhistogram < 0 < macdhistogram_previo:
                DB_habndle.update_opportunities(op, macd=True)
            elif op.macd and macdhistogram > 0 > macdhistogram_previo:
                DB_habndle.update_opportunities(op, macd=False)
            if not op.rsi and rsi <= rsi_sell: # >= 30:
               DB_habndle.update_opportunities(op, rsi=True)
            elif op.rsi and rsi >= rsi_sell: #or rsi_regular <= 30):
                DB_habndle.update_opportunities(op, rsi=False)


    # --------------------check the bullish indicators   ----------------------------------------
    if op.type == 'BUY':
        if srsik >= 0.80 or srsid >= 0.80:
            DB_habndle.update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
        else:
            if not op.macd and macdhistogram > 0 > macdhistogram_previo:
                DB_habndle.update_opportunities(op, macd=True)
            elif op.macd and macdhistogram < 0 < macdhistogram_previo:
                DB_habndle.update_opportunities(op, macd=False)
            if not op.rsi and rsi >= rsi_buy: # <= 70:
                DB_habndle.update_opportunities(op, rsi=True)
            elif op.rsi and rsi <= rsi_buy: # or rsi_regular >= 70):
                DB_habndle.update_opportunities(op, rsi=False)

    if op.macd and op.rsi and op.stock_rsi:
        entry_price_ = df.loc[idx, 'Close']
        open_date_ = df.loc[idx, 'timestamp']
        symbol_ = s
        s_high = df.loc[idx, 'max_high_20']
        s_low = df.loc[idx, 'min_low_20']
        if op.type == 'BUY':
            # quantity_ = round(25 + (15 * (rsi - 50)), 0)
            sl_price = s_low
            sl_factor = (sl_price / entry_price_) - 1
            quantity_ = 100
            stoch_ = stoch_buy
            rsi_ = rsi_buy
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit:
                sl_price = entry_price_ * (1 - sl_limit)

        else:
            # quantity_ = round(25 + (15 * (50 - rsi)), 0)
            sl_price = s_high
            sl_factor = (sl_price / entry_price_) - 1
            quantity_ = 100
            stoch_ = stoch_sell
            rsi_ = rsi_sell
            type_ = 'SELL'
            if sl_factor > sl_limit:
                sl_price = entry_price_ * (1 + sl_limit)

        DB_habndle.create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio)
        DB_habndle.update_opportunities(op, type='OPEN')

def simulator():
    path = "../samples/USDT7/4h/"
    path5 = "../samples/USDT7/5m/"
    symbols = Symbol.objects.filter(find_in_api=True)
    i = 1
    for s in symbols:
        print("simulando " + str(s.symbol) + " - " + str(i))
        i += 1
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation_3.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = min(len(df), 6500)
        csv_file_path5 = f"{path5}{symbol}_simulation.csv"
        df5 = pd.read_csv(csv_file_path5)
        for v1 in [0]:#quedo fijado en 80 y 20, pq la variacion no mostro impacto signifiactivo
            stoch_buy = round(0.2 - v1, 2)
            stoch_sell = round(0.8 + v1, 2)
            for v2 in [0]:
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for v3 in [2]:
                    sl_tp_ratio = v3
                    for v5 in [0]:
                        sl_low_limit = v5
                        for v4 in [0.1]:
                            sl_limit = v4
                            sim_number = 134
                            sim_info = "ratio 1.2"
                            for idx in range(num_rows - 150, -1, -1):
                                anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit, sim_number, sim_info)
                                agripina(s, symbol, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                            op = Oportunities_sim.objects.get(symbol_id=s.pk)
                            DB_habndle.update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                            try:
                                Open_position_sim.objects.get(symbol_id=s.pk).delete()
                            except:
                                pass
simulator()

