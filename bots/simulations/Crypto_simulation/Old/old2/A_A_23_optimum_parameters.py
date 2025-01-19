import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from django.db.models import Avg, Max, Min, FloatField, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When
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
    )

def close_position(s, po, close_date_, close_method, sl_tp_ratio=None, sl_limit=None, sl_low_limit=None):
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
        stoch_open=9,
        rsi_open=9,
        close_method=close_method,
        tp_price=po.tp_price,
        sl_price=po.sl_price,
        tp_sl_ratio=sl_tp_ratio,
        sl_limit=sl_limit,
        sl_low_limit=sl_low_limit,
        simulation=90,
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def anastasia(s, symbol, df, idx):
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
            close_position(s, po, close_date_, close_method='TP')
            return
        elif not tp_period and sl_period:
            close_position(s, po, close_date_, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = high - tp_p
            sl_indicator = sl_p - low
            if tp_indicator > sl_indicator:
                close_position(s, po, close_date_, close_method='TP')
                return
            else:
                close_position(s, po, close_date_, close_method='SL')
                return

        if sl_p < po.entry_price + po.entry_price * 0.00036 * 2:
            factor = (po.tp_price - po.entry_price) / 3
            aumento = (high - po.entry_price)
            if aumento > factor:
                po.sl_price = po.entry_price + po.entry_price * 0.00036 * 2
                po.save()

        elif sl_p == po.entry_price + po.entry_price * 0.00036 * 2:
            factor = (po.tp_price - po.entry_price) / 3
            aumento = (high - po.entry_price)
            if aumento > factor * 2:
                po.sl_price = po.entry_price + po.entry_price * 0.00036 * 2 + factor
                po.save()

    else:

        if low <= tp_p:
            tp_period = True
        if high >= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            close_position(s, po, close_date_, close_method='TP')
            return
        elif not tp_period and sl_period:
            close_position(s, po, close_date_, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = tp_p - low
            sl_indicator = high - sl_p
            if tp_indicator > sl_indicator:
                close_position(s, po, close_date_, close_method='TP')
                return
            else:
                close_position(s, po, close_date_, close_method='SL')
                return
        if sl_p > po.entry_price - po.entry_price * 0.00036 * 2:
            factor = (po.tp_price - po.entry_price) / 3
            aumento = (low - po.entry_price)
            if aumento < factor:
                po.sl_price = po.entry_price - po.entry_price * 0.00036 * 2
                po.save()

        elif sl_p == po.entry_price - po.entry_price * 0.00036 * 2:
            factor = (po.tp_price - po.entry_price) / 3
            aumento = (low - po.entry_price)
            if aumento < factor * 2:
                po.sl_price = po.entry_price - po.entry_price * 0.00036 * 2 + factor
                po.save()

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

def agripina(s, symbol, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio_buy, sl_tp_ratio_sell,
                   sl_limit_buy , sl_limit_sell,  sl_low_limit_buy, sl_low_limit_sell, pnl_buy, pnl_sell):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    macdhistogram = df.loc[idx, 'MACD histogram']
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
        sl_price = calculate_stop_loss_factor(op, df, idx)
        sl_factor = (sl_price / entry_price_) - 1
        if op.type == 'BUY':
            stoch_ = stoch_buy
            rsi_ = rsi_buy
            type_ = 'BUY'
            if abs(sl_factor) > sl_limit_buy:
                sl_price = entry_price_ * (1 - sl_limit_buy)
            elif abs(sl_factor) < sl_low_limit_buy:
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                return
            sl_tp_ratio = sl_tp_ratio_buy
        else:
            stoch_ = stoch_sell
            rsi_ = rsi_sell
            type_ = 'SELL'
            if sl_factor > sl_limit_sell:
                sl_price = entry_price_ * (1 + sl_limit_sell)
            elif sl_factor < sl_low_limit_sell:
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                return
            sl_tp_ratio = sl_tp_ratio_sell
        create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio)
        update_opportunities(op, type='OPEN')

def get_parameters(s, df, i):
    start_date = datetime(2023, i, 1)
    end_date = datetime(2023, i + 4, 1)
    best = Closed_position_sim.objects.values(
            'symbol__symbol', 'simulation', 'tp_sl_ratio', 'sl_low_limit', 'sl_limit'
            ).filter(
                  symbol__symbol=s.symbol,
                  close_date__range=(start_date, end_date),
                  simulation=15,
            ).annotate(
                pnl_total=Sum('profit'),
            ).order_by('-pnl_total').first()
    pnl_buy = best['pnl_total']
    pnl_sell = best['pnl_total']
    stoch_buy = 20
    stoch_sell = 80
    rsi_buy = 40
    rsi_sell = 60
    sl_tp_ratio_buy = best['tp_sl_ratio']
    sl_tp_ratio_sell = best['tp_sl_ratio']
    sl_low_limit_buy = best['sl_low_limit']
    sl_low_limit_sell = best['sl_low_limit']
    sl_limit_buy = best['sl_limit']
    sl_limit_sell = best['sl_limit']

    return stoch_buy, stoch_sell, rsi_buy, rsi_sell, sl_tp_ratio_buy, sl_tp_ratio_sell, \
            sl_limit_buy , sl_limit_sell,  sl_low_limit_buy, sl_low_limit_sell, pnl_buy, pnl_sell

def simulator():
    path = "../../samples/USDT/2023_15m/"
    symbols = Symbol.objects.filter(find_in_api=True)
    for i in [4]:
        for s in symbols:
            print("simulando " + str(s.symbol))
            print(datetime.now())
            symbol = s.symbol
            csv_file_path = f"{path}{symbol}_simulation.csv"
            df = pd.read_csv(csv_file_path)
            num_rows = len(df)
            try:
                stoch_buy, stoch_sell, rsi_buy, rsi_sell, sl_tp_ratio_buy, sl_tp_ratio_sell, sl_limit_buy, sl_limit_sell, \
                    sl_low_limit_buy, sl_low_limit_sell, pnl_buy, pnl_sell = get_parameters(s, df, i)
            except:
                continue
            if pnl_buy < 10 or not pnl_buy:
                continue
            for idx in range(num_rows - 150, -1, -1):
                date = pd.Timestamp(df.loc[idx, 'timestamp'])
                if date < pd.Timestamp(2023, i + 6, 1) and date > pd.Timestamp(2023, i + 4, 1):
                    anastasia(s, symbol, df, idx)
                    agripina(s, symbol, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, idx, sl_tp_ratio_buy, sl_tp_ratio_sell,
                               sl_limit_buy , sl_limit_sell,  sl_low_limit_buy, sl_low_limit_sell, pnl_buy, pnl_sell)
            op = Oportunities_sim.objects.get(symbol_id=s.pk)
            update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
            try:
                Open_position_sim.objects.get(symbol_id=s.pk).delete()
            except:
                pass
simulator()
