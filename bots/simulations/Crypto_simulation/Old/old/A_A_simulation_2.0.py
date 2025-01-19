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

def close_position(s, po, symbol, exit_price, close_date_, close_method):
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
        close_method=close_method,
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)


def anastasia(s, symbol, df, idx):
    # por ahora los valores con mejor resultados son rsi arriba de 80, a veces 85, y dps con valores de TP
    # 0,018 y 0,01 y SL de 0,0066 y 0,012 ambos dan resultados satisfactorios
    try:
        po = Open_position_sim.objects.get(symbol_id=s.pk)
    except:
        return
    type_ = po.type
    exit_price = df.loc[idx, 'Close']
    close_date_ = df.loc[idx, 'timestamp']
    open_price_ = po.entry_price
    delta = exit_price/open_price_ - 1
    if type_ == 'BUY':
        if delta >= 0.012:
            close_position(s, po, symbol, exit_price, close_date_, close_method='TP')
        elif delta <= -0.012:
            close_position(s, po, symbol, exit_price, close_date_, close_method='SL')
    else:
        if delta <= -0.012:
            close_position(s, po, symbol, exit_price, close_date_, close_method='TP')
        elif delta >= 0.012:
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


def simulator():
    path = "../samples/7/"
    symbols = [Symbol.objects.get(symbol='XRPBUSD')] #quitar los grampos cuando haga la simulacion total
    #loop for each symbols
    for s in symbols:
        symbol = s.symbol
        csv_file_path = f"{path}{symbol}_simulation.csv"
        df = pd.read_csv(csv_file_path)
        num_rows = len(df)
        for v1 in [0]:
            srsi_buy = round(0.2 - v1, 2)
            srsi_sell = round(0.8 + v1, 2)
            print("variable 1", v1, " ", datetime.datetime.now())
            for v2 in [0]:
                rsi_buy = 50 + v2
                rsi_sell = 50 - v2
                for idx in range(num_rows - 1, -1, -1):
                    anastasia(s, symbol, df, idx)
                    agripina(s, symbol, df, srsi_buy, srsi_sell, rsi_buy, rsi_sell, idx)
                op = Oportunities_sim.objects.get(symbol_id=s.pk)
                update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                try:
                    Open_position_sim.objects.get(symbol_id=s.pk).delete()
                except:
                    pass
simulator()
