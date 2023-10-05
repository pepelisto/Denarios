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

def open_position(symbol, side, stop_loss_factor, take_profit_factor):

    # Check if there is any open position for the given symbol
    trader = BinanceTrader()
    open_positions = trader.get_open_positions(symbol)
    if open_positions:
        print(f"There are already open positions for symbol {symbol}. Skipping...")
        return

    # Check if there is any closed position for the given symbol in the last hour
    closed_positions = trader.get_closed_positions(symbol)
    if closed_positions:
        current_time = datetime.datetime.now()
        for position in closed_positions:
            close_time = datetime.datetime.fromtimestamp(position['updateTime'] / 1000)
            time_diff = current_time - close_time
            if time_diff.total_seconds() <= 3600:
                print(f"There is a closed position for symbol {symbol} in the last hour. Skipping...")
                return

    # Open position at market price
    usdt_size = 50
    leverage = 19

    set_leverage = trader.set_leverage(symbol, leverage)
    print(set_leverage)

    try:
        trade_market, stopPrice_precision = trader.place_order(symbol, side, usdt_size, leverage)
        print(trade_market)
    except Exception as e:
        print(f"Error placing order for symbol {symbol}: {e}")
        return

    position_id = trade_market['orderId']
    position_info = trader.get_position_info(symbol, position_id=position_id)
    entry_price = float(position_info['entryPrice'])

    stop_loss = round(entry_price * stop_loss_factor, stopPrice_precision)
    take_profit = round(entry_price * take_profit_factor, stopPrice_precision)

    # Place take profit order with retry
    place_order_with_retry(trader, symbol, side, take_profit, 'TAKE_PROFIT_MARKET', position_id, stopPrice_precision, take_profit_factor)

    # Place stop loss order with retry
    place_order_with_retry(trader, symbol, side, stop_loss, 'STOP_MARKET', position_id, stopPrice_precision, stop_loss_factor)

def place_order_with_retry(trader, symbol, side, price, kind, position_id, stopPrice_precision, factor):
    order_placed = False
    while not order_placed:
        try:
            order = trader.place_order_tp_sl(symbol, side, price=price, kind=kind, position_id=position_id)
            print(order)
            order_placed = True
        except ValueError as e:
            error_message = str(e)
            if 'Order would immediately trigger' in error_message:
                # Re-calculate order price based on the current market price
                market_price = trader.get_ticker_price(symbol)
                new_price = round(market_price * factor, stopPrice_precision)
                price = new_price

            elif 'Time in Force (TIF) GTE can only be used with open positions or open orders' in error_message:
                print("position closed before setting the SL order")
                order_placed = True
            else:
                print("other error ocurred")
                # Other error occurred, raise the exception
                raise


def check_timestamp(result):
    current_time = datetime.datetime.now()

    ##### This two lines bellow for Brazilian time zone--------------
    hora = current_time + datetime.timedelta(minutes=180)
    hora_anterior = current_time + datetime.timedelta(minutes=120)

    ##### This two lines bellow for German time zone-----------------
    # hora = current_time - datetime.timedelta(minutes=120)
    # hora_anterior = current_time - datetime.timedelta(minutes=180)

    timestamp = result['timestamp'].iloc[0]
    return timestamp <= hora and timestamp >= hora_anterior

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

def agripina():
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
                update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
        elif srsik < 0.15 and srsid < 0.15:
            if op.type != 'BUY':
                update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)

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
            # open position or simulate one
            continue

def run_scheduled_pattern(start_hour):
    current_time = datetime.datetime.now()
    next_start_time = current_time.replace(hour=start_hour, minute=55, second=0, microsecond=0)
    while True:
        current_time = datetime.datetime.now()
        if current_time >= next_start_time:
            agripina()
            next_start_time = next_start_time + datetime.timedelta(minutes=5)
        # Calculate the remaining time until the next start time
        remaining_time = (next_start_time - datetime.datetime.now()).total_seconds()

        if remaining_time > 0:
            print(f"Waiting for {remaining_time/60} minutes until {next_start_time}")
            time.sleep(remaining_time)

# For Gwrman time zone add 5 hours to brazilian time zone
start_hour = 15

run_scheduled_pattern(start_hour)