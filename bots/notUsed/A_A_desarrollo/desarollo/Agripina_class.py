from django.conf import settings
import django
from bots.notUsed.A_A.functions.Take_position import BinanceTrader

from Denarios.settings import DATABASES, INSTALLED_APPS
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from app.models import *

class Agripina:

    def __init__(self,s, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, sl_tp_ratio, sl_limit, sl_low_limit, timeframe):
        self.s = s
        self.df = df
        self.sl_tp_ratio = sl_tp_ratio
        self.sl_limit = sl_limit
        self.sl_low_limit = sl_low_limit
        self.timeframe = timeframe

    def update_opportunities(self, op, type=None, stock_rsi=None, macd=None, rsi=None):
        if type is not None:
            op.type = type
        if stock_rsi is not None:
            op.stock_rsi = stock_rsi
        if macd is not None:
            op.macd = macd
        if rsi is not None:
            op.rsi = rsi
        op.save()


    def create_position(self, symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, take_profit,
                        leverage, stopPrice_precision, sl_order_id, position_id):
        Open_position.objects.create(
            symbol=symbol_,
            type=type_,
            entry_price=entry_price_,
            leverage=leverage,
            quantity=quantity_,
            margin=(quantity_/leverage),
            open_date=open_date_,
            stoch=stoch_,
            rsi=rsi_,
            sl_price=sl_price,
            tp_price=take_profit,
            stopPrice_precision=stopPrice_precision,
            timeframe=15,
            sl_order_id=sl_order_id,
            id_position=position_id,
            alt_TP_SL=0,
        )


    def open_position(self, symbol, side, stop_loss_factor, take_profit_factor, usdt_size):

        trader = BinanceTrader()
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
        take_profit, tp_order_id = self.place_order_with_retry(trader, symbol, side, take_profit, 'TAKE_PROFIT_MARKET', position_id, stopPrice_precision, take_profit_factor)

        # Place stop loss order with retry
        stop_loss, data = self.place_order_with_retry(trader, symbol, side, stop_loss, 'STOP_MARKET', position_id, stopPrice_precision, stop_loss_factor)
        sl_order_id = data['orderId']

        return entry_price, stop_loss, take_profit, leverage, stopPrice_precision, sl_order_id, position_id



    def place_order_with_retry(self, trader, symbol, side, price, kind, position_id, stopPrice_precision, factor):
        order_placed = False
        order = None
        while not order_placed:
            try:
                order = trader.place_order_tp_sl(symbol, side, price=price, kind=kind, position_id=position_id)
                print(order)
                order_placed = True
            except ValueError as e:
                error_message = str(e)
                if 'Order would immediately trigger' in error_message:

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
        return price, order


    def calculate_stop_loss_factor(self, op, df):
        sl_price = None
        sl_price_2 = None
        if op.type == 'BUY':
            for i in range(0, 10):
                min_value = df.loc[i, 'low']
                if sl_price is None or min_value < sl_price:
                    sl_price = min_value
            found = False
            starting = 10
            while not found:
                for i in range(starting, starting + 5):
                    min_value_2 = df.loc[i, 'low']
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
                min_value = df.loc[i, 'high']
                if sl_price is None or min_value > sl_price:
                    sl_price = min_value
                found = False
                starting = 10
                while not found:
                    for i in range(starting, starting + 5):
                        min_value_2 = df.loc[i, 'high']
                        if sl_price_2 is None or min_value_2 > sl_price_2:
                            sl_price_2 = min_value_2
                    if sl_price_2 > sl_price:
                        sl_price = sl_price_2
                        sl_price_2 = None
                    else:
                        found = True
                    starting += 5
        return sl_price


    def agripina(self, s, df, stoch_buy, stoch_sell, rsi_buy, rsi_sell, sl_tp_ratio, sl_limit, sl_low_limit):
        op = Oportunities.objects.get(symbol=s.symbol, timeframe=15)
        if op.type == 'OPEN':
            return
        macdhistogram = df['macd_histogram'].iloc[0]
        srsik = df['stoch_osc_k'].iloc[0]
        srsid = df['stoch_osc_d'].iloc[0]
        rsi = df['rsi'].iloc[0]
        #---------------------check the stochastich rsi indicators ----------------------------------------
        if srsik >= stoch_sell and srsid >= stoch_sell:
            if op.type != 'SELL':
                self.update_opportunities(op, type='SELL', stock_rsi=True, macd=False, rsi=False)
        elif srsik <= stoch_buy and srsid <= stoch_buy:
            if op.type != 'BUY':
                self.update_opportunities(op, type='BUY', stock_rsi=True, macd=False, rsi=False)
        # ----------------------check the bearish indicators   ----------------------------------------
        if op.type == 'SELL':
            if not op.macd:
                if macdhistogram < 0:
                    self.update_opportunities(op, macd=True)
            if not op.rsi:
                if rsi <= rsi_sell:
                    self.update_opportunities(op, rsi=True)
        # --------------------check the bullish indicators   ----------------------------------------
        if op.type == 'BUY':
            if not op.macd:
                if macdhistogram > 0:
                    self.update_opportunities(op, macd=True)
            if not op.rsi:
                if rsi >= rsi_buy:
                    self.update_opportunities(op, rsi=True)

        if op.macd and op.rsi and op.stock_rsi:
            entry_price_ = df['close'].iloc[0]
            quantity_ = s.q
            open_date_ = df['timestamp'].iloc[0]
            symbol_ = s.symbol
            sl_price = self.calculate_stop_loss_factor(op, df)
            sl_factor = (sl_price / entry_price_) - 1
            if op.type == 'BUY':
                stoch_ = stoch_buy
                rsi_ = rsi_buy
                type_ = 'BUY'
                if abs(sl_factor) > sl_limit:
                    sl_price = entry_price_ * (1 - sl_limit)
                elif abs(sl_factor) < sl_low_limit:
                    self.update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                    return
            else:
                stoch_ = stoch_sell
                rsi_ = rsi_sell
                type_ = 'SELL'
                if sl_factor > sl_limit:
                    sl_price = entry_price_ * (1 + sl_limit)
                elif sl_factor < sl_low_limit:
                    self.update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)
                    return
            #--------------aqui abrir posicion en binance-----------------------------
            sl_factor = (sl_price / entry_price_) - 1
            usdt_size = s.q
            sym = s.symbol.symbol
            profit_factor = 1 + sl_factor * (-1.05) * sl_tp_ratio
            loss_factor = 1 + sl_factor * (1.05)
            entry_price, stop_loss, take_profit, leverage, stopPrice_precision, sl_order_id, position_id \
                = self.open_position(sym, type_, loss_factor, profit_factor, usdt_size)
            self.create_position(symbol_, type_, entry_price, quantity_, open_date_, stoch_,
                            rsi_, stop_loss, take_profit, leverage, stopPrice_precision, sl_order_id, position_id)
            self.update_opportunities(op, type='OPEN')



