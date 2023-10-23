
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

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, tp_price):
    sl_factor = (sl_price/entry_price_) - 1
    tp__ = tp_price
    sl__ = entry_price_ + entry_price_ * sl_factor * (1.005)
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
        ratr=0,
    )

def close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method, exit_price=None):
    if close_method == "SL" and exit_price is None:
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
    print(close_method + '   type: ' + po.type + '   PNL: ' + str(profit_))
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
        simulation=4,
        sim_info='desideria5 con histograma confirmation, hasta rsi stockastic opuesto o SL hasta cambio de pendiente',
        ratr=+1,
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def anastasia(s, df, idx, sl_tp_ratio, sl_limit, sl_low_limit, rsi_buy_exit, rsi_sell_exit):
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    type_ = po.type
    close = df.loc[idx, 'Close']
    high = df.loc[idx, 'High']
    low = df.loc[idx, 'Low']
    rsi = df.loc[idx, 'stoch_rsi_k']
    rsi_anterior = df.loc[idx + 1, 'stoch_rsi_k']
    close_date_ = df.loc[idx, 'timestamp']
    sl_p = po.sl_price
    tp_period = False
    sl_period = False
    period = po.ratr
    if type_ == 'BUY':
        tp_p = po.entry_price * (1 + 0.0009)
        if close >= tp_p and rsi < rsi_anterior:
            # (rsi > rsi_buy_exit or rsi_anterior > rsi_buy_exit)  \
            #     and  df.loc[idx, 'MACD histogram'] > df.loc[idx + 1, 'MACD histogram'] > df.loc[idx + 2, 'MACD histogram'] \
            #     and rsi < rsi_anterior:
            tp_period = True
        if low <= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP', exit_price=close)
            return
        elif not tp_period and sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = close - tp_p
            sl_indicator = sl_p - low
            if tp_indicator > sl_indicator:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP', exit_price=close)
                return
            else:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
                return
        elif close <= tp_p and rsi < rsi_anterior:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL', exit_price=close)
            return
        else:
            po.ratr += 1
            po.save()
    else:
        tp_p = po.entry_price * (1 - 0.0009)
        if close <= tp_p and rsi < rsi_sell_exit:
                # (rsi < rsi_sell_exit or rsi_anterior < rsi_sell_exit) \
                # and  df.loc[idx, 'MACD histogram'] < df.loc[idx + 1, 'MACD histogram'] < df.loc[idx + 2, 'MACD histogram'] \
                # and rsi > rsi_anterior:
            tp_period = True
        if high >= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP', exit_price=close)
            return
        elif not tp_period and sl_period:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = tp_p - close
            sl_indicator = high - sl_p
            if tp_indicator > sl_indicator:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP', exit_price=close)
                return
            else:
                close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
                return
        elif close >= tp_p and rsi < rsi_sell_exit:
            close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL', exit_price=close)
            return
        else:
            po.ratr += 1
            po.save()

def agripina(s, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    srsik = df.loc[idx, 'stoch_rsi_k']
    srsid = df.loc[idx, 'stoch_rsi_d']
    #---------------------check the stochastich rsi indicators ----------------------------------------
    if srsik >= stoch_sell and srsid >= stoch_sell:
        if op.type != 'SELL':
            update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
    elif srsik <= stoch_buy and srsid <= stoch_buy:
        if op.type != 'BUY':
            update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)
    # ----------------------check the bearish indicators   ----------------------------------------
    if op.type == 'SELL':
        if df.loc[idx, 'stoch_rsi_k'] < df.loc[idx + 1, 'stoch_rsi_k']:
            if df.loc[idx, 'MACD histogram'] < df.loc[idx + 1, 'MACD histogram']:
                update_opportunities(op, macd=True, rsi=True)
            else:
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

    # --------------------check the bullish indicators   ----------------------------------------
    if op.type == 'BUY':
        if df.loc[idx, 'stoch_rsi_k'] > df.loc[idx + 1, 'stoch_rsi_k']:
            if df.loc[idx, 'MACD histogram'] > df.loc[idx + 1, 'MACD histogram']:
                update_opportunities(op, macd=True, rsi=True)
            else:
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

    if op.macd and op.rsi and op.stock_rsi:
        entry_price_ = df.loc[idx, 'Close']
        quantity_ = 100
        open_date_ = df.loc[idx, 'timestamp']
        symbol_ = s
        if op.type == 'BUY':
            tp_price = None
            sl_price = entry_price_ * (1 - sl_limit)
            stoch_ = stoch_buy
            rsi_ = rsi_buy
            type_ = 'BUY'

        else:
            tp_price = None
            sl_price = entry_price_ * (1 + sl_limit)
            stoch_ = stoch_sell
            rsi_ = rsi_sell
            type_ = 'SELL'

        create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, tp_price)
        update_opportunities(op, type='OPEN')

def simulator():
    path = "samples/USDT/2023_4h/"
    symbols = Symbol.objects.filter(find_in_api=True)
    for s in symbols:
        print("simulando " + str(s.symbol))
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = min(len(df), 2000)
        for v1 in [0]:#quedo fijado en 80 y 20, pq la variacion no mostro impacto signifiactivo
            stoch_buy = round(0.20 - v1, 2)
            stoch_sell = round(0.80 + v1, 2)
            rsi_buy = 0.2
            rsi_sell = 0.8
            sl_tp_ratio = 4
            sl_low_limit = 0.025
            for v in [0.05]:
                sl_limit = v
                for idx in range(num_rows - 150, -1, -1):
                    anastasia(s, df, idx, sl_tp_ratio, sl_limit, sl_low_limit, rsi_sell, rsi_buy)
                    agripina(s, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio, sl_limit, sl_low_limit)
                op = Oportunities_sim.objects.get(symbol_id=s.pk)
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                try:
                    Open_position_sim.objects.get(symbol_id=s.pk).delete()
                except:
                    pass
simulator()
