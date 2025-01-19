
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

def close_position(s, po, symbol, exit_price, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method):
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
        simulation=151,
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
    exit_price = df.loc[idx, 'Close']
    close_date_ = df.loc[idx, 'timestamp']
    tp_p = po.tp_price
    sl_p = po.sl_price
    if type_ == 'BUY':
        if exit_price >= tp_p:
            close_position(s, po, symbol, exit_price, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
        elif exit_price <= sl_p:
            close_position(s, po, symbol, exit_price, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
        # elif sl_p != po.entry_price + po.entry_price * 0.00036 * 2:
        #     factor = (abs((sl_p / po.entry_price) - 1)) * (sl_tp_ratio / 2)
        #     aumento = (exit_price / po.entry_price) - 1
        #     if aumento > factor:
        #        po.sl_price = po.entry_price + po.entry_price * 0.00036 * 2
        #        po.save()
    else:
        if exit_price <= tp_p:
            close_position(s, po, symbol, exit_price, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
        elif exit_price >= sl_p:
            close_position(s, po, symbol, exit_price, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
        # elif sl_p != po.entry_price - po.entry_price * 0.00036 * 2:
        #     factor = ((sl_p / po.entry_price) - 1) * (sl_tp_ratio / 2)
        #     aumento = (-1)*((exit_price / po.entry_price) - 1)
        #     if aumento > factor:
        #        po.sl_price = po.entry_price - po.entry_price * 0.00036 * 2
        #        po.save()

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
            for i in range(starting, starting + 3):
                min_value_2 = df.loc[idx + i, 'Low']
                if sl_price_2 is None or min_value_2 < sl_price_2:
                    sl_price_2 = min_value_2
            if sl_price_2 < sl_price:
                sl_price = sl_price_2
                sl_price_2 = None
            else:
                found = True
            starting += 3
    else:
        for i in range(0, 10):
            min_value = df.loc[idx + i, 'High']
            if sl_price is None or min_value > sl_price:
                sl_price = min_value
            found = False
            starting = 10
            while not found:
                for i in range(starting, starting + 3):
                    min_value_2 = df.loc[idx + i, 'High']
                    if sl_price_2 is None or min_value_2 > sl_price_2:
                        sl_price_2 = min_value_2
                if sl_price_2 > sl_price:
                    sl_price = sl_price_2
                    sl_price_2 = None
                else:
                    found = True
                starting += 3
    return sl_price

def agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    macdhistogram = df.loc[idx, 'MACD histogram']
    srsik = df.loc[idx, 'St k']
    srsid = df.loc[idx, 'St d']
    rsi = df.loc[idx, 'RSI']
    #---------------------check the stochastich rsi indicators ----------------------------------------
    if srsik >= srsi_sell and srsid >= srsi_sell:
        if op.type != 'SELL':
            update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
    elif srsik <= srsi_buy and srsid <= srsi_buy:
        if op.type != 'BUY':
            update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)
    # ----------------------check the bearish indicators   ----------------------------------------
    if op.type == 'SELL':
        if not op.macd:
            if macdhistogram < 0:
                update_opportunities(op, macd=True)
        if not op.rsi:
            if rsi <= rsi_sell:
                update_opportunities(op, rsi=True)
    # --------------------check the bullish indicators   ----------------------------------------
    if op.type == 'BUY':
        if not op.macd:
            if macdhistogram > 0:
                update_opportunities(op, macd=True)
        if not op.rsi:
            if rsi >= rsi_buy:
                update_opportunities(op, rsi=True)

    if op.macd and op.rsi and op.stock_rsi:
        entry_price_ = df.loc[idx, 'Close']
        quantity_ = 100
        open_date_ = df.loc[idx, 'timestamp']
        symbol_ = s
        if op.type == 'BUY':
            srsi_ = srsi_buy
            rsi_ = rsi_buy
            type_ = 'BUY'
        else:
            srsi_ = srsi_sell
            rsi_ = rsi_sell
            type_ = 'SELL'
        sl_price = calculate_stop_loss_factor(op, df, idx)
        sl_factor = (sl_price / entry_price_) - 1
        if abs(sl_factor) * sl_tp_ratio > sl_low_limit:
            if abs(sl_factor) > sl_limit:
                sign = np.sign(sl_factor)
                sl_factor = sl_limit * sign
                sl_price = ((sl_factor) + 1) * entry_price_
            create_position(symbol_, type_, entry_price_, quantity_, open_date_, srsi_, rsi_, sl_price, sl_tp_ratio)
            update_opportunities(op, type='OPEN')
        else:
            update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def simulator():
    path = "../../samples/USDT/2023_15m/"
    symbols = Symbol.objects.filter(find_in_api=True)
    for s in symbols:
        print("simulando " + str(s.symbol))
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = len(df)
        for v1 in [0]:
            srsi_buy = round(20 - v1, 2)
            srsi_sell = round(80 + v1, 2)
            print("variable 1", v1, " ", datetime.datetime.now())
            for v2 in [0]:
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for v3 in [3]:
                    sl_tp_ratio = v3
                    for v5 in [0.001]:# este quedo fijoo para siempre
                        sl_low_limit = v5
                        for v4 in [0.015]:
                            sl_limit = v4
                            for idx in range(num_rows - 150, -1, -1):
                                anastasia(s, symbol, df, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                                agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                            op = Oportunities_sim.objects.get(symbol_id=s.pk)
                            update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                            try:
                                Open_position_sim.objects.get(symbol_id=s.pk).delete()
                            except:
                                pass
simulator()
