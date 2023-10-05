
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

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, srsi_, rsi_, sl_price, sl_tp_ratio):
    sl_factor = (sl_price/entry_price_) - 1
    tp__ = entry_price_ + entry_price_ * sl_factor * (-1.05) * sl_tp_ratio
    sl__ = entry_price_ + entry_price_ * sl_factor * (1.05)
    Open_position_sim.objects.create(
        symbol=symbol_,
        type=type_,
        entry_price=entry_price_,
        quantity=quantity_,
        open_date=open_date_,
        srsi=srsi_,
        rsi=rsi_,
        sl_price=sl__,
        tp_price=tp__,
    )

def close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method):
    if close_method == "TP":
        exit_price = po.tp_price
    else:
        exit_price = po.sl_price
    if po.type == "BUY":
        delta = exit_price/po.entry_price - 1
    else:
        delta = -((exit_price / po.entry_price) - 1)
    quantity_ = round(po.quantity * (1 + delta), 2)
    fee_entry = round(po.quantity * 0.00036, 5)
    fee_exit = round(quantity_ * 0.00036, 5)
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
        srsi_open=sl_low_limit,
        rsi_open=po.rsi,
        close_method=close_method,
        tp_price=po.tp_price,
        sl_price=po.sl_price,
        tp_sl_ratio=sl_tp_ratio,
        sl_limit=sl_limit,
        simulation=13,
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def anastasia(s, symbol, df, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    type_ = po.type
    close = df.loc[idx, 'Close']
    high = df.loc[idx, 'High']
    low = df.loc[idx, 'Low']
    close_date_ = df.loc[idx, 'timestamp']
    tp_p = po.tp_price
    sl_p = po.sl_price
    tp_period = False
    sl_period = False
    if type_ == 'BUY':
        if high >= tp_p:
            tp_period = True
        if low <= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
            return
        elif not tp_period and sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = high - tp_p
            sl_indicator = sl_p - low
            if tp_indicator > sl_indicator:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
                return
            else:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
                return

        if sl_tp_ratio > 1:
            if sl_p < po.entry_price + po.entry_price * 0.00036 * 2:
                factor = (po.tp_price - po.entry_price) / 3
                aumento = (high - po.entry_price)
                if aumento > factor:
                    # print('precio Buy 1 ajustado ' + str(po.sl_price))
                    po.sl_price = po.entry_price + po.entry_price * 0.00036 * 2
                    po.save()
                    # print('high ' + str(high))
                    # print('precio entry ' + str(po.entry_price))
                    # print('nuevo SL ' + str(po.sl_price))
                    # print('-------------------------------------------------------')

            elif sl_p == po.entry_price + po.entry_price * 0.00036 * 2:
                factor = (po.tp_price - po.entry_price) / 3
                aumento = (high - po.entry_price)
                if aumento > factor * 2:
                    # print('precio Buy 2 ajustado ' + str(po.sl_price))
                    po.sl_price = po.entry_price + po.entry_price * 0.00036 * 2 + factor
                    po.save()
                    # print('high ' + str(high))
                    # print('precio entry ' + str(po.entry_price))
                    # print('nuevo SL ' + str(po.sl_price))
                    # print('-------------------------------------------------------')

    else:
        if low <= tp_p:
            tp_period = True
        if high >= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
            return
        elif not tp_period and sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = tp_p - low
            sl_indicator = high - sl_p
            if tp_indicator > sl_indicator:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
                return
            else:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
                return
        if sl_tp_ratio > 1:
            if sl_p > po.entry_price - po.entry_price * 0.00036 * 2:
                factor = (po.tp_price - po.entry_price) / 3
                aumento = (low - po.entry_price)
                if aumento < factor:
                    # print('precio SELL 1 ajustado ' + str(po.sl_price))
                    po.sl_price = po.entry_price - po.entry_price * 0.00036 * 2
                    po.save()
                    # print('Low ' + str(low))
                    # print('precio entry ' + str(po.entry_price))
                    # print('nuevo SL ' + str(po.sl_price))
                    # print('-------------------------------------------------------')
            elif sl_p == po.entry_price - po.entry_price * 0.00036 * 2:
                factor = (po.tp_price - po.entry_price) / 3
                aumento = (low - po.entry_price)
                if aumento < factor * 2:
                    # print('precio SELL 2 ajustado ' + str(po.sl_price))
                    po.sl_price = po.entry_price - po.entry_price * 0.00036 * 2 + factor
                    po.save()
                    # print('Low ' + str(low))
                    # print('TP ' + str(po.tp_price))
                    # print('precio entry ' + str(po.entry_price))
                    # print('nuevo SL ' + str(po.sl_price))
                    # print('-------------------------------------------------------')

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
            for i in range(starting, starting + 10):
                min_value_2 = df.loc[idx + i, 'Low']
                if sl_price_2 is None or min_value_2 < sl_price_2:
                    sl_price_2 = min_value_2
            if sl_price_2 < sl_price:
                sl_price = sl_price_2
                sl_price_2 = None
            else:
                found = True
            starting += 10
    else:
        for i in range(0, 10):
            min_value = df.loc[idx + i, 'High']
            if sl_price is None or min_value > sl_price:
                sl_price = min_value
            found = False
            starting = 10
            while not found:
                for i in range(starting, starting + 10):
                    min_value_2 = df.loc[idx + i, 'High']
                    if sl_price_2 is None or min_value_2 > sl_price_2:
                        sl_price_2 = min_value_2
                if sl_price_2 > sl_price:
                    sl_price = sl_price_2
                    sl_price_2 = None
                else:
                    found = True
                starting += 10
    return sl_price

def agripina(s, symbol, df, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    macd_n = df.loc[idx, 'MACD']
    macd_n_1 = df.loc[idx, 'MACD n-1']
    rsi = df.loc[idx, 'RSI']
    #---------------------check the stochastich rsi indicators ----------------------------------------
    if rsi >= rsi_sell:
        if op.type != 'SELL':
            update_opportunities(op, type='SELL', stock_rsi=False, macd=False, rsi=True)
    elif rsi <= rsi_buy:
        if op.type != 'BUY':
            update_opportunities(op, type='BUY', stock_rsi=False, macd=False, rsi=True)
    # ----------------------check the bearish indicators   ----------------------------------------
    if op.type == 'SELL':
        if not op.macd:
            if macd_n_1 > macd_n:
                update_opportunities(op, macd=True)
    # --------------------check the bullish indicators   ----------------------------------------
    if op.type == 'BUY':
        if not op.macd:
            if macd_n_1 < macd_n:
                update_opportunities(op, macd=True)

    if op.macd and op.rsi:
        entry_price_ = df.loc[idx, 'Close']
        quantity_ = 100
        open_date_ = df.loc[idx, 'timestamp']
        symbol_ = s
        sl_price = calculate_stop_loss_factor(op, df, idx)
        sl_factor = (sl_price / entry_price_) - 1
        if op.type == 'BUY':
            srsi_ = 0
            rsi_ = rsi_buy
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit:
                sl_price = entry_price_ * (1 - sl_limit)
            elif abs(sl_factor) < sl_low_limit:
                sl_price = entry_price_ * (1 - sl_low_limit)
        else:
            srsi_ = 0
            rsi_ = rsi_sell
            type_ = 'SELL'
            if sl_factor > sl_limit:
                sl_price = entry_price_ * (1 + sl_limit)
            elif sl_factor < sl_low_limit:
                sl_price = entry_price_ * (1 + sl_low_limit)

        create_position(symbol_, type_, entry_price_, quantity_, open_date_, srsi_, rsi_, sl_price, sl_tp_ratio)
        update_opportunities(op, type='OPEN')


def simulator():
    path = "../samples/USDT/2023_15m/"
    symbols = Symbol.objects.filter(find_in_api=True)[3:]
    for s in symbols:
        print("simulando " + str(s.symbol))
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = len(df)
        for v2 in [10]:# probar con numeros mas grandes
            rsi_sell = 70 + v2
            rsi_buy = 30 - v2
            for v3 in [1]:
                sl_tp_ratio = v3
                for v5 in [0.01]:
                    sl_low_limit = v5
                    for v4 in [0.011]:#dps 0.015 denuevo y solo el 10 arriba
                        sl_limit = v4
                        print(str(v3) + '  ' + str(v4))
                        for idx in range(num_rows - 150, -1, -1):
                            anastasia(s, symbol, df, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                            agripina(s, symbol, df, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                        op = Oportunities_sim.objects.get(symbol_id=s.pk)
                        update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                        try:
                            Open_position_sim.objects.get(symbol_id=s.pk).delete()
                        except:
                            pass
simulator()
