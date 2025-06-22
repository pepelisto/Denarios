import requests
import pandas as pd
import ta
from datetime import datetime
import ta.trend as trend
import numpy as np
from binance.client import Client

class CryptoAnalyzer:
    def __init__(self, symbol, interval, limit, candles, end_date):
        self.symbol = symbol
        self.interval = interval
        self.limit = limit
        self.candles = candles
        self.end_date = end_date
        self.api_key = 'Hj5hgo1bAaNC5QjseJqvs9oy6KX3fYMC7XHV1agdzk1chrS8CGLXsD31hX3jnz4a'
        self.api_secret = 'DoCHrwKl4L0jIiLClRMMAIWmNkDFHmchpqo1SN1naLtgsOekYxFswrNBvx0qQX4u'
        self.client = Client(self.api_key, self.api_secret)

    def fetch_data(self):

        end_timestamp = int(datetime.timestamp(self.end_date) * 1000)
        data = self.client.futures_klines(
                                        symbol=self.symbol,
                                        interval=self.interval,
                                        limit=self.limit,
                                        endTime=end_timestamp
                                    )

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                         'close_time', 'quote_asset_volume', 'num_trades',
                                         'taker_buy_base', 'taker_buy_quote', 'ignore'])

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        return df

    def analyze_crypto(self):
        analyzed_cryptos = []
        df = self.fetch_data()
        for i in range(0, self.candles):
            last_row = df.iloc[-i-1]
            # last_last_row = df.iloc[-i-2]
            analyzed_cryptos.append({
                'Symbol': self.symbol,
                'timestamp': last_row['timestamp'],
                'Open': last_row['open'],
                'Close': last_row['close'],
                'Low': last_row['low'],
                'High': last_row['high'],
                'Volume': last_row['volume'],
                'Num_trades': last_row['num_trades'],
                'Taker_buy_base': last_row['taker_buy_base'],
                'Taker_buy_quote': last_row['taker_buy_quote'],

            })

        df = pd.DataFrame(analyzed_cryptos)
        # Set display options to show all columns in one line
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        return df