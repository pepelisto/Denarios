import requests
import pandas as pd
from CryptoAnalyzer import CryptoAnalyzer
import csv
from Take_position import BinanceTrader
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

symbols = Symbol.objects.all()
for s in symbols:
    symbol = s.symbol
    symbols = [symbol]
    interval = '5m'
    limit = 400
    data_frame = CryptoAnalyzer(symbols=symbols, interval=interval, limit=limit).analyze_crypto()
    macdhistogram = data_frame['MACD histogram'].iloc[0]
    srsik = data_frame['SRSI k'].iloc[0]
    srsid = data_frame['SRSI d'].iloc[0]
    rsi = data_frame['RSI'].iloc[0]
    op = Oportunities.objects.get(symbol_id=s.pk)

    if srsik > 0.85 and srsid > 0.85:
        if op.type != 'SELL':
            update_opportunities(op, type='SELL', stock_rsi=False, macd=False, rsi=False)
    elif srsik < 0.15 and srsid < 0.15:
        if op.type != 'BUY':
            update_opportunities(op, type='BUY', stock_rsi=False, macd=False, rsi=False)

    if op.type == 'SELL':
        if not op.macd:
            if macdhistogram < 0:
                update_opportunities(op, macd=True)
        if not op.rsi:
            if rsi < 50:
                update_opportunities(op, rsi=True)

    if op.type == 'BUY':
        if not op.macd:
            if macdhistogram > 0:
                update_opportunities(op, macd=True)
        if not op.rsi:
            if rsi < 50:
                update_opportunities(op, rsi=True)

    if op.macd and op.rsi and op.stock_rsi:
       #open position or simulate one
       continue