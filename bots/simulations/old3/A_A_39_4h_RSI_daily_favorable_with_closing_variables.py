
import pandas as pd
import datetime
import numpy as np
from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from app.models import *

def update_opportunities(op, type=None, stock_rsi=None, macd=None, rsi=None):
    if type is not None:
        op.type = type
    if stock_rsi is not None:
        op.stock_rsi = stock_rsi
    if macd is not None:
        op.macd = macd
    if rsi is not None:
        op.rsi = rsi
    op.save()

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio):
    sl_factor = (sl_price/entry_price_) - 1
    tp__ = entry_price_ + entry_price_ * sl_factor * (-1.05) * sl_tp_ratio
    sl__ = entry_price_ + entry_price_ * sl_factor * (1.05)
    Open_position_sim.objects.create(
        symbol=symbol_,
        type=type_,
        entry_price=entry_price_,
        quantity=quantity_,
        open_date=open_date_,
        stoch=stoch_,
        rsi=rsi_,
        sl_price=sl__,
        tp_price=tp__,
        atr=0,
    )

def close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method, close_price=None):
    if close_method == "TP" and close_price is None:
        exit_price = po.tp_price
    elif close_method == "SL" and close_price is None:
        exit_price = po.sl_price
    else:
        exit_price = close_price
    if po.type == "BUY":
        delta = exit_price/po.entry_price - 1
    else:
        delta = -((exit_price / po.entry_price) - 1)
    quantity_ = round(po.quantity * (1 + delta), 2)
    fee_entry = round(po.quantity * 0.00045, 5)
    fee_exit = round(quantity_ * 0.00045, 5)
    total_fee = round(fee_exit + fee_entry, 4)
    profit_ = round(po.quantity * delta - total_fee, 3)
    roe_ = round((profit_/po.quantity)*100, 1)
    Closed_position_sim.objects.create(
        symbol=s,
        type=po.type,
        entry_price=round(po.entry_price, 6),
        exit_price=round(exit_price, 6),
        roe=roe_,
        fee=total_fee,
        profit=profit_,
        quantity=quantity_,
        open_date=po.open_date,
        close_date=close_date_,
        stoch_open=po.stoch,
        rsi_open=po.rsi,
        close_method=close_method,
        tp_price=po.tp_price,
        sl_price=po.sl_price,
        tp_sl_ratio=sl_tp_ratio,
        sl_limit=sl_limit,
        sl_low_limit=sl_low_limit,
        ratr=factor_ajuste,
        simulation=400654057,
        sim_info='rsi +-5, histograma decreciente , AA_39 revisa el tf diario que sea el rsi 56 tambien favorable'
                 'en valores de menora a 45 para sell y mayor a 55 para buy , tambien cierra posiciones con macd t srsi en contra',
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def update_position(po, alt_TP_SL=None, sl_price=None, tp_price=None):
    if tp_price is not None:
        po.tp_price = tp_price
    if alt_TP_SL is not None:
        po.atr = alt_TP_SL
    if sl_price is not None:
        po.sl_price = sl_price
    po.save()

def anastasia(s, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste):
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    close_date_ = df.loc[idx, 'timestamp']
    matching_row = df5[df5['timestamp'] == close_date_].index[0]

    macdhistogram = df.loc[idx, 'macd_histogram_2']
    macdhistogram_previo = df.loc[idx + 1, 'macd_histogram_2']
    srsik = df.loc[idx, 'St k']
    srsid = df.loc[idx, 'St d']
    type_ = po.type
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if type_ == 'SELL':
        if srsik <= 0.1 and srsid <= 0.1:
            update_opportunities(op, stock_rsi=False)
        if macdhistogram < macdhistogram_previo:
            update_opportunities(op, macd=False)
        if op.macd and op.stock_rsi:
            close = df.loc[idx, 'Open']
            resultado = po.entry_price - close
            if resultado < 0:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='TP', close_price=close)
                return
            else:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='SL', close_price=close)
                return
    else:
        if srsik >= 0.9 and srsid >= 0.9:
            update_opportunities(op, stock_rsi=False)
        if macdhistogram > macdhistogram_previo:
            update_opportunities(op, macd=False)
        if op.macd and op.stock_rsi:
            close = df.loc[idx, 'Open']
            resultado = po.entry_price - close
            if resultado > 0:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='TP', close_price=close)
                return
            else:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='SL', close_price=close)
                return
    for i in range(matching_row, matching_row - 48, -1):
        row_data = df5.iloc[i]
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
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='TP')
                return
            elif not tp_period and sl_period:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='SL')
                return
            elif tp_period and sl_period:
                tp_indicator = high - tp_p
                sl_indicator = sl_p - low
                if tp_indicator > sl_indicator:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='TP')
                    return
                else:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='SL')
                    return

            aumento = (close - po.entry_price)/po.entry_price
            if aumento > (alteraciones + 1) * factor_ajuste:
                ajuste = True
                stop_loss = sl_p + po.entry_price * factor_ajuste
                take_profit = tp_p + po.entry_price * factor_ajuste

        else:
            if low <= tp_p:
                tp_period = True
            if high >= sl_p:
                sl_period = True
            if tp_period and not sl_period:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='TP')
                return
            elif not tp_period and sl_period:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='SL')
                return
            elif tp_period and sl_period:
                tp_indicator = tp_p - low
                sl_indicator = high - sl_p
                if tp_indicator > sl_indicator:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='TP')
                    return
                else:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method='SL')
                    return

            aumento = -((close - po.entry_price) / po.entry_price)
            if aumento > (alteraciones + 1) * factor_ajuste:
                ajuste = True
                stop_loss = sl_p - po.entry_price * factor_ajuste
                take_profit = tp_p - po.entry_price * factor_ajuste

        if ajuste:
            alt = alteraciones + 1
            update_position(po, alt, stop_loss, take_profit)


def calculate_stop_loss_factor(op, df, idx):
    sl_price = None
    sl_price_2 = None
    if op.type == 'BUY':
        for i in range(0, 10):
            min_value = df.loc[idx + i, 'Low']
            if sl_price is None or min_value < sl_price:
                sl_price = min_value
        found = False
        starting = 10
        while not found:
            for i in range(starting, starting + 5):
                min_value_2 = df.loc[idx + i, 'Low']
                if sl_price_2 is None or min_value_2 < sl_price_2:
                    sl_price_2 = min_value_2
            if sl_price_2 < sl_price:
                sl_price = sl_price_2
                sl_price_2 = None
            else:
                found = True
            starting += 5
    else:
        for i in range(0, 10):
            min_value = df.loc[idx + i, 'High']
            if sl_price is None or min_value > sl_price:
                sl_price = min_value
            found = False
            starting = 10
            while not found:
                for i in range(starting, starting + 5):
                    min_value_2 = df.loc[idx + i, 'High']
                    if sl_price_2 is None or min_value_2 > sl_price_2:
                        sl_price_2 = min_value_2
                if sl_price_2 > sl_price:
                    sl_price = sl_price_2
                    sl_price_2 = None
                else:
                    found = True
                starting += 5
    return sl_price

def agripina(s, df, df24, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    macdhistogram = df.loc[idx, 'macd_histogram_2']
    macdhistogram_previo = df.loc[idx + 1, 'macd_histogram_2']
    # macdhistogram_previo_previo = df.loc[idx + 2, 'macd_histogram_2']
    srsik = df.loc[idx, 'St k']
    srsid = df.loc[idx, 'St d']
    rsi = df.loc[idx, 'RSI']
    #---------------------check the stochastich rsi indicators ----------------------------------------
    if srsik >= stoch_sell and srsid >= stoch_sell:
        if op.type != 'SELL':
            update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
    elif srsik <= stoch_buy and srsid <= stoch_buy:
        if op.type != 'BUY':
            update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)
    # ----------------------check the bearish indicators   ----------------------------------------
    if op.type == 'SELL':
        if not op.macd and macdhistogram < macdhistogram_previo:
            update_opportunities(op, macd=True)
        if op.macd and macdhistogram > macdhistogram_previo:
            update_opportunities(op, macd=False)
        if not op.rsi and rsi <= rsi_sell:
           update_opportunities(op, rsi=True)
        if op.rsi and rsi >= rsi_sell:
            update_opportunities(op, rsi=False)
    # --------------------check the bullish indicators   ----------------------------------------
    if op.type == 'BUY':
        if not op.macd and macdhistogram > macdhistogram_previo:
            update_opportunities(op, macd=True)
        if op.macd and macdhistogram < macdhistogram_previo:
            update_opportunities(op, macd=False)
        if not op.rsi and rsi >= rsi_buy:
            update_opportunities(op, rsi=True)
        if op.rsi and rsi <= rsi_buy:
            update_opportunities(op, rsi=False)

    if op.macd and op.rsi and op.stock_rsi:
        entry_price_ = df.loc[idx, 'Close']
        quantity_ = 100
        open_date_ = df.loc[idx, 'timestamp']
        date_to_compare = pd.to_datetime(df.loc[idx, 'timestamp']).strftime('%Y-%m-%d')
        matching_row = df24[df24['timestamp'] == date_to_compare].index[0]
        rsi_daily_tf = df24.iloc[matching_row]['RSI']
        symbol_ = s
        sl_price = calculate_stop_loss_factor(op, df, idx)
        sl_factor = (sl_price / entry_price_) - 1
        if op.type == 'BUY':
            if rsi_daily_tf < 43 or str(rsi_daily_tf) == 'nan':
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                return
            stoch_ = stoch_buy
            rsi_ = rsi_buy
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit:
                sl_price = entry_price_ * (1 - sl_limit)
            elif abs(sl_factor) < sl_low_limit:
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                return
                # sl_price = entry_price_ * (1 - sl_low_limit)
        else:
            if rsi_daily_tf > 57 or str(rsi_daily_tf) == 'nan':
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                return
            stoch_ = stoch_sell
            rsi_ = rsi_sell
            type_ = 'SELL'
            if sl_factor > sl_limit:
                sl_price = entry_price_ * (1 + sl_limit)
            elif sl_factor < sl_low_limit:
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                return
        create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio)
        update_opportunities(op, type='OPEN')

def simulator():
    path = "../samples/USDT3/2023_4h/"
    path5 = "samples/USDT3/2023_5m/"
    path24 = "samples/USDT3/2023_1d/"
    symbols = Symbol.objects.filter(find_in_api=True)
    for s in symbols:
        print("simulando " + str(s.symbol))
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = min(len(df), 8405)
        csv_file_path5 = f"{path5}{symbol}_simulation.csv"
        df5 = pd.read_csv(csv_file_path5)
        csv_file_path24 = f"{path24}{symbol}_simulation.csv"
        df24 = pd.read_csv(csv_file_path24)
        for v1 in [0]:#quedo fijado en 80 y 20, pq la variacion no mostro impacto signifiactivo
            stoch_buy = round(0.2 - v1, 2)
            stoch_sell = round(0.8 + v1, 2)
            for v2 in [4]:
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for v3 in [1.5]:
                    sl_tp_ratio = v3
                    for v5 in [0.01]:
                        sl_low_limit = v5
                        for v4 in [0.1]:
                            sl_limit = v4
                            for v5 in [0.0075]:
                                '''next try with fa igual a sl low limit'''
                                factor_ajuste = v5
                                print(str(v3) + '  ' + str(v4))
                                for idx in range(num_rows - 150, -1, -1):
                                    anastasia(s, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste)
                                    agripina(s, df, df24, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                                '''pueden haber posiciones abiertas significativas q simplemente se eliminan al final del periodo, cerrarlas en lugar de deletarlas'''
                                op = Oportunities_sim.objects.get(symbol_id=s.pk)
                                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                                try:
                                    Open_position_sim.objects.get(symbol_id=s.pk).delete()
                                except:
                                    pass
simulator()
