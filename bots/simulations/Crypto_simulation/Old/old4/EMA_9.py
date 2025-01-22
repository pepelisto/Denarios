
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

def update_opportunities(op, type=None, stock_rsi=None, macd=None, rsi=None, var_1=None, var_2=None, var_3=None):
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
    if var_2 is not None:
        op.var_2 = var_2
    if var_3 is not None:
        op.var_3 = var_3

    op.save()

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, sl_price, sl_tp_ratio):
    sl_factor = (sl_price/entry_price_) - 1
    tp__ = entry_price_ + entry_price_ * sl_factor * (-1.05) * sl_tp_ratio
    sl__ = entry_price_ + entry_price_ * sl_factor * (1.05)
    factor_ajuste = (abs((1 - entry_price_ / sl_price))) * 1.5
    Open_position_sim.objects.create(
        symbol=symbol_,
        type=type_,
        entry_price=entry_price_,
        quantity=quantity_,
        open_date=open_date_,
        sl_price=sl__,
        tp_price=tp__,
        ratr=factor_ajuste,  #se usa como factor de ajuste inicial
        atr=0,
    )

def close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method):
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
        close_method=close_method,
        tp_price=po.tp_price,
        sl_price=po.sl_price,
        tp_sl_ratio=sl_tp_ratio,
        sl_limit=sl_limit,
        ratr=factor_ajuste,
        simulation=9000,
        sim_info='9 ema, sin ajust TP  ',
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', var_1=None, var_2=None)

def update_position(po, alt_TP_SL=None, sl_price=None, tp_price=None):
    if tp_price is not None:
        po.tp_price = tp_price
    if alt_TP_SL is not None:
        po.atr = alt_TP_SL
    if sl_price is not None:
        po.sl_price = sl_price
    po.save()

def anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit):
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
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='TP')
                return
            elif not tp_period and sl_period:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='SL')
                return
            elif tp_period and sl_period:
                tp_indicator = high - tp_p
                sl_indicator = sl_p - low
                if tp_indicator > sl_indicator:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='TP')
                    print("dividido TP buy")
                    return
                else:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='SL')
                    print("dividido SL buy")
                    return

            aumento = (close - po.entry_price) / po.entry_price
            if alteraciones == 0:
                if aumento > factor_ajuste:
                    ajuste = True
                    stop_loss = sl_p + po.entry_price * (factor_ajuste / 3) * 4
                    take_profit = tp_p + po.entry_price * (factor_ajuste / 3) * 2
            else:
                if aumento > factor_ajuste + (alteraciones + 1) * (factor_ajuste / 3):
                    ajuste = True
                    stop_loss = sl_p + po.entry_price * (factor_ajuste / 3)
                    take_profit = tp_p + po.entry_price * (factor_ajuste / 3)

        else:
            if low <= tp_p:
                tp_period = True
            if high >= sl_p:
                sl_period = True
            if tp_period and not sl_period:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='TP')
                return
            elif not tp_period and sl_period:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='SL')
                return
            elif tp_period and sl_period:
                tp_indicator = tp_p - low
                sl_indicator = high - sl_p
                if tp_indicator > sl_indicator:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='TP')
                    print("dividido TP sell")
                    return
                else:
                    close_position(s, po, close_date_, sl_tp_ratio, sl_limit, factor_ajuste, close_method='SL')
                    print("dividido SL sell")
                    return

            aumento = -((close - po.entry_price) / po.entry_price)
            if alteraciones == 0:
                if aumento > factor_ajuste:
                    ajuste = True
                    stop_loss = sl_p - po.entry_price * (factor_ajuste / 3) * 4
                    take_profit = tp_p - po.entry_price * (factor_ajuste / 3) * 2
            else:
                if aumento > factor_ajuste + (alteraciones + 1) * (factor_ajuste / 3):
                    ajuste = True
                    stop_loss = sl_p - po.entry_price * (factor_ajuste / 3)
                    take_profit = tp_p - po.entry_price * (factor_ajuste / 3)

        if ajuste:
            alt = alteraciones + 1
            update_position(po, alt, stop_loss, take_profit)


def agripina(s, symbol, df, idx, sl_tp_ratio, sl_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    ema_0 = df.loc[idx, 'ema_9']
    ema_1 = df.loc[idx + 1, 'ema_9']
    ema_2 = df.loc[idx + 2, 'ema_9']
    ema_3 = df.loc[idx + 3, 'ema_9']
    ema_4 = df.loc[idx + 4, 'ema_9']
    ema_5 = df.loc[idx + 5, 'ema_9']
    ema_6 = df.loc[idx + 6, 'ema_9']
    ema_7 = df.loc[idx + 7, 'ema_9']
    ema_8 = df.loc[idx + 8, 'ema_9']
    ema_9 = df.loc[idx + 9, 'ema_9']
    rsi = df.loc[idx + 1, 'rsi_regular']
    close = df.loc[idx, 'Close']

    #--------------------- check the 9 EMA to set triggers----------------------------------------

    if ema_1 > ema_2 > ema_3:# > ema_4 > ema_5 > ema_6 > ema_7 > ema_8 > ema_9:
        if close < ema_0 and rsi > 60:
            stop_loss = df.loc[idx, 'High']
            entry_price_triger = df.loc[idx, 'Low']
            update_opportunities(op, type='SELL', var_1=stop_loss, var_2=entry_price_triger)
            return

    elif ema_1 < ema_2 < ema_3:# < ema_4 < ema_5 < ema_6 < ema_7 < ema_8 < ema_9:
        if close > ema_0 and rsi < 40:
            stop_loss = df.loc[idx, 'Low']
            entry_price_triger = df.loc[idx, 'High']
            update_opportunities(op, type='BUY',  var_1=stop_loss, var_2=entry_price_triger)
            return

    # -------------------- check the if trigers are met and open  ----------------------------------------
    if op.type == 'BUY':
        high = df.loc[idx, 'High']
        if high > op.var_2:
            entry_price_ = op.var_2
            open_date_ = df.loc[idx, 'timestamp']
            symbol_ = s
            sl_price = op.var_1
            sl_factor = (sl_price / entry_price_) - 1
            quantity_ = 100
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit:
                sl_price = entry_price_ * (1 - sl_limit)
            create_position(symbol_, type_, entry_price_, quantity_, open_date_, sl_price, sl_tp_ratio)
            update_opportunities(op, type='OPEN')

    elif op.type == 'SELL':
        low = df.loc[idx, 'Low']
        if low < op.var_2:
            entry_price_ = op.var_2
            open_date_ = df.loc[idx, 'timestamp']
            symbol_ = s
            sl_price = op.var_1
            sl_factor = (sl_price / entry_price_) - 1
            quantity_ = 100
            type_ = 'SELL'
            if sl_factor > sl_limit:
                sl_price = entry_price_ * (1 + sl_limit)
            create_position(symbol_, type_, entry_price_, quantity_, open_date_, sl_price, sl_tp_ratio)
            update_opportunities(op, type='OPEN')


def simulator():
    path = "samples/USDT6/4h/"
    path5 = "samples/USDT6/5m/"
    symbols = Symbol.objects.filter(find_in_api=True)
    i = 1
    for s in symbols:
        print("simulando " + str(s.symbol) + " - " + str(i))
        i += 1
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation_with_9ema.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = min(len(df), 1100)
        csv_file_path5 = f"{path5}{symbol}_simulation.csv"
        df5 = pd.read_csv(csv_file_path5)
        for v3 in [2]:
            sl_tp_ratio = v3
            for v4 in [0.08]:
                sl_limit = v4
                for idx in range(num_rows - 150, -1, -1):
                    anastasia(s, symbol, df, df5, idx, sl_tp_ratio, sl_limit)
                    agripina(s, symbol, df,  idx, sl_tp_ratio, sl_limit)
                op = Oportunities_sim.objects.get(symbol_id=s.pk)
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                try:
                    Open_position_sim.objects.get(symbol_id=s.pk).delete()
                except:
                    pass
simulator()

