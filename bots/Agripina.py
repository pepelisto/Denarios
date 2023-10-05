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
from app.models import Symbol

def apply_conditions(df):
    # verifica que el K% del periodo anterior de RSI stockastico es menor a 0,2, esta sobre vendido
    df['low RSI'] = ((df['n-2 Stoch. RSI K'] < 0.35) & (df['n-1 Stoch. RSI K'] < 0.8) |
                     (df['n-3 Stoch. RSI K'] < 0.35) & (df['n-1 Stoch. RSI K'] < 0.8)).astype(int)

    df['high RSI'] = ((df['n-2 Stoch. RSI K'] > 0.65) & (df['n-1 Stoch. RSI K'] > 0.2) |
                      (df['n-3 Stoch. RSI K'] > 0.65) & (df['n-1 Stoch. RSI K'] > 0.2)).astype(int)

    df['bullish MACD'] = (
            # (df['n-2 MACD'] < df['n-2 MACD Signal']) & (df['n-1 MACD'] > df['n-1 MACD Signal']) |
                          (df['n-1 MACD'] < df['n-1 MACD Signal']) & (df['n MACD'] > df['n MACD Signal'])).astype(int)

    df['bearish MACD'] = (
            # (df['n-2 MACD'] > df['n-2 MACD Signal']) & (df['n-1 MACD'] < df['n-1 MACD Signal']) |
                          (df['n-1 MACD'] > df['n-1 MACD Signal']) & (df['n MACD'] < df['n MACD Signal'])).astype(int)

    df['bullish ma50'] = (df['n-1 Close'] > df['n-1 50-Hourly MAP']).astype(int)

    df['bearish ma50'] = (df['n-1 Close'] < df['n-1 50-Hourly MAP']).astype(int)

    df['long'] = ((df['bullish ma50'] + df['bullish MACD'] + df['low RSI']) >= 3).astype(int)

    df['short'] = ((df['bearish ma50'] + df['bearish MACD'] + df['high RSI']) >= 3).astype(int)

    # Set display options to show all columns in one line
    # pd.set_option('display.expand_frame_repr', False)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # print(df)

    si_df = df[['Symbol', 'timestamp', 'n Close', 'short', 'long']].copy()

    return si_df

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

                # if it doesn't work i could try this aproach
                # position_info_a = trader.get_position_info(symbol, position_id=position_id)
                # markPrice = float(position_info_a['markPrice'])
                # new_price = round(markPrice * factor, stopPrice_precision)
                # price = new_price

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

def agripina():
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            symbol = row[0].strip()
            if symbol:
                symbols = [symbol]
                interval = '1h'
                limit = 400
                data_frame = CryptoAnalyzer(symbols=symbols, interval=interval, limit=limit).analyze_crypto()
                result = apply_conditions(data_frame)

                if result['short'].iloc[0] == 1:
                    short_delta_av = float(row[2]) / 100
                    if short_delta_av > 0 and check_timestamp(result):
                        loss_factor = (short_delta_av + 1)
                        profit_factor = (-short_delta_av + 1)
                        side = 'SELL'

                        open_position(symbol, side, loss_factor, profit_factor)

                if result['long'].iloc[0] == 1:
                    long_delta_av = float(row[1]) / 100
                    if long_delta_av > 0 and check_timestamp(result):
                        loss_factor = (-long_delta_av + 1)
                        profit_factor = (long_delta_av + 1)
                        side = 'BUY'

                        open_position(symbol, side, loss_factor, profit_factor)

                print(result)

def run_scheduled_pattern(start_hour):
    current_time = datetime.datetime.now()
    next_start_time = current_time.replace(hour=start_hour, minute=1, second=0, microsecond=0)
    while True:
        current_time = datetime.datetime.now()
        if current_time >= next_start_time:
            agripina()
            next_start_time = next_start_time + datetime.timedelta(minutes=1)
        # Calculate the remaining time until the next start time
        remaining_time = (next_start_time - datetime.datetime.now()).total_seconds()

        if remaining_time > 0:
            print(f"Waiting for {remaining_time/60} minutes until {next_start_time}")
            time.sleep(remaining_time)

file_path = 'symbols.csv'

# For Gwrman time zone add 5 hours to brazilian time zone
start_hour = 00

run_scheduled_pattern(start_hour)