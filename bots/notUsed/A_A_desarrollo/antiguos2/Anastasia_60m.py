from django.conf import settings
import django
from bots.notUsed.A_A.functions.CryptoAnalyzer import CryptoAnalyzer
from bots.notUsed.A_A.functions.Take_position import BinanceTrader
import time
import datetime
from django.db import transaction, DatabaseError

from Denarios.settings import DATABASES, INSTALLED_APPS
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from app.models import *

MAX_RETRIES = 10

def retry_on_database_error(func, *args, **kwargs):
    for _ in range(MAX_RETRIES):
        try:
            result = func(*args, **kwargs)
            return result
        except DatabaseError as e:
            print(f"Database error: {e}. Retrying...")
            time.sleep(2)  # Add a 2-second delay before retrying
    print(f"Max retries reached. Unable to complete the operation.")
    return None

@transaction.atomic
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

@transaction.atomic
def update_position(po, sl_order_id=None, alt_TP_SL=None, sl_price=None):
    if sl_order_id is not None:
        po.sl_order_id = sl_order_id
    if alt_TP_SL is not None:
        po.alt_TP_SL = alt_TP_SL
    if sl_price is not None:
        po.sl_price = sl_price
    po.save()

@transaction.atomic
def delete_position(symbol, timeframe):
    Open_position.objects.get(symbol_id=symbol, timeframe=timeframe).delete()

@transaction.atomic
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
    Closed_position.objects.create(
        symbol=s.symbol,
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
        alt_TP_SL=po.alt_TP_SL,
        timeframe=60,
    )
    retry_on_database_error(delete_position, s.symbol.pk, 15)
    op = Oportunities.objects.get(symbol_id=s.symbol.pk, timeframe=60)
    retry_on_database_error(update_opportunities, op, type='NONE', stock_rsi=False, macd=False, rsi=False)


def adjust_sl(symbol, side, stop_loss, stopPrice_precision, order_id):
    trader = BinanceTrader()
    r = trader.cancel_order(symbol, order_id)
    print(r)
    # Place stop loss order with retry
    new_sl, new_order_id = place_order_with_retry(trader, symbol, side, stop_loss, 'STOP_MARKET', stopPrice_precision)
    return new_sl, new_order_id


def place_order_with_retry(trader, symbol, side, price, kind, stopPrice_precision):
    order_placed = False
    order = None
    while not order_placed:
        try:
            order = trader.place_order_tp_sl(symbol, side, price=price, kind=kind)
            print(order)
            order_placed = True
        except ValueError as e:
            error_message = str(e)
            if 'Order would immediately trigger' in error_message:
                if side == 'BUY':
                    new_price = round(price - price * 0.0005, stopPrice_precision)
                    price = new_price
                else:
                    new_price = round(price + price * 0.0005, stopPrice_precision)
                    price = new_price

            elif 'Time in Force (TIF) GTE can only be used with open positions or open orders' in error_message:
                print("position closed before setting the SL order")
                order_placed = True
            else:
                print("other error ocurred")
                # Other error occurred, raise the exception
                raise
    return price, order


def anastasia(s, df, sl_tp_ratio, sl_limit, sl_low_limit):
    try:
        po = Open_position.objects.get(symbol_id=s.symbol.pk, timeframe=60)
    except:
        return
    type_ = po.type
    close = df['close'].iloc[0]
    high = df['high'].iloc[0]
    low = df['low'].iloc[0]
    close_date_ = df['timestamp'].iloc[0]
    tp_p = po.tp_price
    sl_p = po.sl_price
    alteraciones = po.alt_TP_SL
    precision = po.stopPrice_precision
    tp_period = False
    sl_period = False
    ajuste = False
    if type_ == 'BUY':
        if high >= tp_p:
            tp_period = True
        if low <= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
            return
        elif not tp_period and sl_period:
            retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = high - tp_p
            sl_indicator = sl_p - low
            if tp_indicator > sl_indicator:
                retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
                return
            else:
                retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
                return
        aumento = (high - po.entry_price)/po.entry_price
        if aumento > (alteraciones + 1) * 0.003:
            ajuste = True
            stop_loss = round(sl_p + po.entry_price * 0.003, precision)


    else:
        if low <= tp_p:
            tp_period = True
        if high >= sl_p:
            sl_period = True
        if tp_period and not sl_period:
            retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
            return
        elif not tp_period and sl_period:
            retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
            return
        elif tp_period and sl_period:
            tp_indicator = tp_p - low
            sl_indicator = high - sl_p
            if tp_indicator > sl_indicator:
                retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='TP')
                return
            else:
                retry_on_database_error(close_position, s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, close_method='SL')
                return
        aumento = -((low - po.entry_price)/po.entry_price)
        if aumento > (alteraciones + 1) * 0.003:
            ajuste = True
            stop_loss = round(sl_p - po.entry_price * 0.003, precision)


    if ajuste:
        sl_order_id = po.sl_order_id
        side = po.type
        symbol = s.symbol.symbol
        new_sl, new_order_id = adjust_sl(symbol, side, stop_loss, precision, sl_order_id)
        atl = alteraciones + 1
        retry_on_database_error(update_position, po, new_order_id, atl, new_sl)


def traeder():
    open_positions = Open_position.objects.filter(timeframe=60).values_list('symbol_id', flat=True)
    if not open_positions.exists():
        return
    symbols = Optimum_parameter.objects.filter(symbol__id__in=open_positions, timeframe=60).order_by('-pnl')
    for s in symbols:
        symbols = [s.symbol.symbol]
        interval = '1h'
        limit = 400
        df = CryptoAnalyzer(symbols=symbols, interval=interval, limit=limit).analyze_crypto()
        df = df[::-1].reset_index(drop=True)
        sl_tp_ratio = s.tp_sl_ratio
        sl_limit = s.sl_limit
        sl_low_limit = s.sl_low_limit
        anastasia(s, df, sl_tp_ratio, sl_limit, sl_low_limit)


def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        next_start_time = current_time + datetime.timedelta(seconds=45)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        time.sleep(remaining_time)
        traeder()


# traeder()
run_scheduled_pattern()
