import requests
import pandas as pd
import ta
import time


class CryptoAnalyzer:
    def __init__(self, symbols, interval, limit):
        self.symbols = symbols
        self.interval = interval
        self.limit = limit

    def fetch_data(self, symbol):
        url = f"https://fapi.binance.com/fapi/v1/markPriceKlines?symbol={symbol.upper()}&interval={self.interval}&limit={self.limit}"
        res = False
        while not res:
            try:
                response = requests.get(url)
                res = True
            except ValueError as e:
                print('error getting data from binance api, waiting for 2 minutes ')
                time.sleep(120)
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                         'close_time', 'quote_asset_volume', 'num_trades',
                                         'taker_buy_base', 'taker_buy_quote', 'ignore'])

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        return df

    def calculate_indicators(self, df):
        if df is None:
            return None

        # Calculate Stochastic Oscillator
        stoch_osc = ta.momentum.StochRSIIndicator(df['close'])
        df['stoch_osc_k'] = stoch_osc.stochrsi_k()
        df['stoch_osc_d'] = stoch_osc.stochrsi_d()

        # Calculate MACD
        macd = ta.trend.MACD(df['close'], window_fast=6, window_slow=12, window_sign=4)
        df['macd_histogram'] = macd.macd_diff()

        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df['close'], window=56)
        df['rsi'] = rsi.rsi()

        # Calculate RSI
        rsi_fast = ta.momentum.RSIIndicator(df['close'])
        df['rsi_fast'] = rsi_fast.rsi()

        return df

    def analyze_crypto(self):
        for symbol in self.symbols:
            df = self.fetch_data(symbol)
            if df is None:
                continue
            df = self.calculate_indicators(df)
            if df is None:
                continue
        return df