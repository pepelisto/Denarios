
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

def update_opportunities(op, type=None, stock_rsi=None, macd=None, rsi=None, var_1=None):
    if type is not None:
        op.type = type
    if stock_rsi is not None:
        op.stock_rsi = stock_rsi
    if macd is not None:
        op.macd = macd
    if rsi is not None:
        op.rsi = rsi
    if var_1 is not None:
        op.var_1 = var_1
    op.save()

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio):
    sl_factor = (sl_price/entry_price_) - 1
    tp__ = entry_price_ + entry_price_ * sl_factor * (-1.05) * sl_tp_ratio
    sl__ = entry_price_ + entry_price_ * sl_factor * (1.05)
    factor_ajuste = (abs((1 - entry_price_ / sl_price)) + 0.001) * 1.5
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
        ratr=factor_ajuste,  #se usa como factor de ajuste inicial
        atr=0,
    )

def close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, close_method):
    if close_method == "TP":
        exit_price = po.tp_price
    else:
        exit_price = po.sl_price
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
        stoch_open=round(abs(0.5 - po.stoch), 2),
        rsi_open=abs(50 - po.rsi),
        close_method=close_method,
        tp_price=po.tp_price,
        sl_price=po.sl_price,
        tp_sl_ratio=sl_tp_ratio,
        sl_limit=sl_limit,
        sl_low_limit=sl_low_limit,
        ratr=factor_ajuste,
        simulation=5,
        sim_info='sl only modified ,  '
                 '',
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

def anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit):
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

            aumento = (close - po.entry_price) / po.entry_price
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
            update_position(po, alt, stop_loss)

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
            update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
    elif srsik <= stoch_buy and srsid <= stoch_buy:
        if op.type != 'BUY':
            update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)
    # ----------------------check the bearish indicators   ----------------------------------------
    if op.type == 'SELL':
        if srsik <= 0.20 or srsid <= 0.20:
            update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False, var_1=0)
        else:
            if not op.macd and macdhistogram < macdhistogram_previo:
                update_opportunities(op, macd=True)
            elif op.macd and macdhistogram > macdhistogram_previo:
                update_opportunities(op, macd=False)
            if not op.rsi and rsi <= rsi_sell: # >= 30:
               update_opportunities(op, rsi=True)
            elif op.rsi and rsi >= rsi_sell: #or rsi_regular <= 30):
                update_opportunities(op, rsi=False)
            if not op.var_1 == 1 and ema_100 > close:
                update_opportunities(op, var_1=1)
            elif op.var_1 == 1 and ema_100 < close:
                update_opportunities(op, var_1=0)

    # --------------------check the bullish indicators   ----------------------------------------
    if op.type == 'BUY':
        if srsik >= 0.80 or srsid >= 0.80:
            update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False, var_1=0)
        else:
            if not op.macd and macdhistogram > macdhistogram_previo:
                update_opportunities(op, macd=True)
            elif op.macd and macdhistogram < macdhistogram_previo:
                update_opportunities(op, macd=False)
            if not op.rsi and rsi >= rsi_buy: # <= 70:
                update_opportunities(op, rsi=True)
            elif op.rsi and rsi <= rsi_buy: # or rsi_regular >= 70):
                update_opportunities(op, rsi=False)
            if not op.var_1 == 1 and ema_100 < close:
                update_opportunities(op, var_1=1)
            elif op.var_1 == 1 and ema_100 > close:
                update_opportunities(op, var_1=0)

    if op.macd and op.rsi and op.stock_rsi and op.var_1 == 1:
        entry_price_ = df.loc[idx, 'Close']
        open_date_ = df.loc[idx, 'timestamp']
        symbol_ = s
        s_high = df.loc[idx, 'max_high_20']
        s_low = df.loc[idx, 'min_low_20']
        if op.type == 'BUY':
            quantity_ = round(25 + (15 * (rsi - 50)), 0)
            sl_price = s_low
            sl_factor = (sl_price / entry_price_) - 1
            # quantity_ = 100
            stoch_ = stoch_buy
            rsi_ = rsi_buy
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit:
                sl_price = entry_price_ * (1 - sl_limit)

        else:
            quantity_ = round(25 + (15 * (50 - rsi)), 0)
            sl_price = s_high
            sl_factor = (sl_price / entry_price_) - 1
            # quantity_ = 100
            stoch_ = stoch_sell
            rsi_ = rsi_sell
            type_ = 'SELL'
            if sl_factor > sl_limit:
                sl_price = entry_price_ * (1 + sl_limit)

        create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio)
        update_opportunities(op, type='OPEN')

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
            for v2 in [4]:
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for v3 in [3]:
                    sl_tp_ratio = v3
                    for v5 in [0]:
                        sl_low_limit = v5
                        for v4 in [0.1]:
                            sl_limit = v4
                            for idx in range(num_rows - 150, -1, -1):
                                anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                                agripina(s, symbol, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                            op = Oportunities_sim.objects.get(symbol_id=s.pk)
                            update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                            try:
                                Open_position_sim.objects.get(symbol_id=s.pk).delete()
                            except:
                                pass
simulator()

