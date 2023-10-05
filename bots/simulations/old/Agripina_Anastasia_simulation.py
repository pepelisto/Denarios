import requests
import pandas as pd
import datetime
import time
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

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, srsi_, rsi_):
    Open_position_sim.objects.create(
        symbol=symbol_,
        type=type_,
        entry_price=entry_price_,
        quantity=quantity_,
        open_date=open_date_,
        srsi=srsi_,
        rsi=rsi_,
    )

def close_position(s, po, symbol, exit_price, close_date_, close_method, srsid_=None, srsik_=None):
    if po.type == "BUY":
        delta = exit_price/po.entry_price - 1
    else:
        delta = -((exit_price / po.entry_price) - 1)
    quantity_ = round(po.quantity * (1 + delta), 2)
    fee_entry = round(po.quantity * 0.00027, 5)
    fee_exit = round(quantity_ * 0.00027, 5)
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
        srsi_open=po.srsi,
        rsi_open=po.rsi,
        srsid_close=srsid_,
        srsik_close=srsik_,
        close_method=close_method,
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def anastasia(s, symbol, df, srsid_close_buy, srsid_close_sell, srsik_close_buy, srsik_close_sell, idx):
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    type_ = po.type
    srsik = df.loc[idx, 'SRSI k']
    srsid = df.loc[idx, 'SRSI d']
    rsi = df.loc[idx, 'RSI']
    macdhistogram = df.loc[idx, 'MACD histogram']
    exit_price = df.loc[idx, 'Close']
    close_date_ = df.loc[idx, 'timestamp']
    if type_ == 'BUY':
        if srsid_close_buy is not None:
            if srsid >= srsid_close_buy:
                close_position(s, po, symbol, exit_price, close_date_, close_method='SRSID', srsid_=srsid_close_buy)
                return
        else:
            if srsik >= srsik_close_buy:
                close_position(s, po, symbol, exit_price, close_date_, close_method='SRSIK', srsik_=srsik_close_buy)
                return
        if rsi < 50:
            close_position(s, po, symbol, exit_price, close_date_, close_method='RSI',
                           srsik_=srsik_close_buy, srsid_=srsid_close_buy)
            return
        if macdhistogram < 0:
            close_position(s, po, symbol, exit_price, close_date_, close_method='MACD',
                           srsik_=srsik_close_buy, srsid_=srsid_close_buy)

    else:
        if srsid_close_sell is not None:
            if srsid <= srsid_close_sell:
                close_position(s, po, symbol, exit_price, close_date_, close_method='SRSID', srsid_=srsid_close_sell)
                return
        else:
            if srsik <= srsik_close_sell:
                close_position(s, po, symbol, exit_price, close_date_, close_method='SRSIK', srsik_=srsik_close_sell)
                return
        if rsi > 50:
            close_position(s, po, symbol, exit_price, close_date_, close_method='RSI',
                           srsik_=srsik_close_sell, srsid_=srsid_close_sell)
            return
        if macdhistogram > 0:
            close_position(s, po, symbol, exit_price, close_date_, close_method='MACD',
                           srsik_=srsik_close_sell, srsid_=srsid_close_sell)


def anastasia_no_variable(s, symbol, df, idx):
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    type_ = po.type
    exit_price = df.loc[idx, 'Close']
    close_date_ = df.loc[idx, 'timestamp']
    open_price_ = po.entry_price
    delta = 1 - exit_price/open_price_
    if type_ == 'BUY':
        if delta >= 0.02:
            close_position(s, po, symbol, exit_price, close_date_, close_method='TP')
        elif delta <= -0.012:
            close_position(s, po, symbol, exit_price, close_date_, close_method='SL')
    else:
        if delta <= -0.012:
            close_position(s, po, symbol, exit_price, close_date_, close_method='TP')
        elif delta >= 0.02:
            close_position(s, po, symbol, exit_price, close_date_, close_method='SL')

def agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx):
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    if op.type == 'OPEN':
        return
    macdhistogram = df.loc[idx, 'MACD histogram']
    srsik = df.loc[idx, 'SRSI k']
    srsid = df.loc[idx, 'SRSI d']
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
        create_position(symbol_, type_, entry_price_, quantity_, open_date_, srsi_, rsi_)
        update_opportunities(op, type='OPEN')


def simulator_largo():
    path = "../samples/"
    symbols = [Symbol.objects.get(symbol='BTCBUSD')] #quitar los grampos cuando haga la simulacion total
    #loop for each symbols
    for s in symbols:
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = len(df)
        for v1 in range(21):
            print("variable 1", v1, " ", datetime.datetime.now())
            srsi_buy = 0 + (v1/100)
            srsi_sell = 1 - (v1/100)
            for v2 in range(10):
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for v3 in range(42):
                    if v3 < 22:
                        srsid_close_buy = 1 - (v3/100)
                        srsid_close_sell = 0 + (v3/100)
                        srsik_close_buy = None
                        srsik_close_sell = None
                    else:
                        srsid_close_buy = None
                        srsid_close_sell = None
                        srsik_close_buy = 1 - ((v3 - 22)/100)
                        srsik_close_sell = 0 + ((v3 - 22)/100)
                    op = Oportunities_sim.objects.get(symbol_id=s.pk)
                    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                    try:
                        Open_position_sim.objects.get(symbol_id=s.pk).delete()
                    except:
                        pass
                    for idx in range(num_rows - 1, -1, -1):
                        anastasia(s, symbol, df, srsid_close_buy, srsid_close_sell, srsik_close_buy, srsik_close_sell, idx)
                        agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx)

# def simulator():
#     path = "samples/"
#     symbols = [Symbol.objects.get(symbol='BTCBUSD')] #quitar los grampos cuando haga la simulacion total
#     #loop for each symbols
#     for s in symbols:
#         symbol = s.symbol
#         csv_file_path = f"{path}{symbol}_simulation.csv"
#         df = pd.read_csv(csv_file_path)
#         num_rows = len(df)
#         for v1 in [0, 0.05, 0.09, 0.12]:
#             srsi_buy = round(0.15 - v1, 2)
#             srsi_sell = round(0.85 + v1, 2)
#             print("variable 1", v1, " ", datetime.datetime.now())
#             for v2 in [0, 2, 5]:
#                 rsi_buy = 50 + v2
#                 rsi_sell = 50 - v2
#                 z = 0
#                 for v3 in [0, 0.05, 0.09, 0.12, 0, 0.05, 0.09, 0.12]:
#                     if z < 4:
#                         srsid_close_buy = round(0.85 + v3, 2)
#                         srsid_close_sell = round(0.15 - v3, 2)
#                         srsik_close_buy = None
#                         srsik_close_sell = None
#                     else:
#                         srsid_close_buy = None
#                         srsid_close_sell = None
#                         srsik_close_buy = round(0.85 + v3, 2)
#                         srsik_close_sell = round(0.15 - v3, 2)
#                     z += 1
#                     op = Oportunities_sim.objects.get(symbol_id=s.pk)
#                     update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
#                     try:
#                         Open_position_sim.objects.get(symbol_id=s.pk).delete()
#                     except:
#                         pass
#                     for idx in range(num_rows - 1, -1, -1):
#                         anastasia(s, symbol, df, srsid_close_buy, srsid_close_sell, srsik_close_buy, srsik_close_sell, idx)
#                         agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx)


def simulator_open_variable_only():
    path = "../samples/"
    symbols = [Symbol.objects.get(symbol='BTCBUSD')] #quitar los grampos cuando haga la simulacion total
    #loop for each symbols
    for s in symbols:
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = len(df)
        for v1 in [0, 0.05, 0.1]: #,0.05, 0.09, 0.12
            srsi_buy = round(0.15 - v1, 2)
            srsi_sell = round(0.85 + v1, 2)
            print("variable 1", v1, " ", datetime.datetime.now())
            for v2 in [0, 2]:
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for idx in range(num_rows - 1, -1, -1):
                    anastasia_no_variable(s, symbol, df, idx)
                    agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx)
                op = Oportunities_sim.objects.get(symbol_id=s.pk)
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                try:
                    Open_position_sim.objects.get(symbol_id=s.pk).delete()
                except:
                    pass

simulator_open_variable_only()
