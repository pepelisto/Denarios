import requests
import pandas as pd
import ta
from datetime import datetime


class CryptoAnalyzer:
    def __init__(self, symbols, interval, limit, candles, end_date):
        self.symbols = symbols
        self.interval = interval
        self.limit = limit
        self.candles = candles
        self.end_date = end_date

    def fetch_data(self, symbol):
        end_timestamp = int(datetime.timestamp(self.end_date) * 1000)
        url = f"https://fapi.binance.com/fapi/v1/markPriceKlines?symbol={symbol.upper()}&interval={self.interval}&limit={self.limit}&endTime={end_timestamp}"
        response = requests.get(url)
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

        # # Calculate MFI
        # mfi = ta.momentum.MFIIndicator(df['high'], df['low'], df['close'], df['volume'], window=14)  # You can adjust the window as needed
        # df['mfi'] = mfi.money_flow_index()

        # Calculate Stochastic RSI
        # stoch_rsi = ta.momentum.StochRSIIndicator(df['close'])
        # df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
        # df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()

        # Calculate Stochastic Oscillator
        stoch_osc = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)  # You can adjust the window and smooth_window as needed
        df['stoch_osc_k'] = stoch_osc.stoch()
        df['stoch_osc_d'] = stoch_osc.stoch_signal()

        # Calculate MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()

        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df['close'])
        df['rsi'] = rsi.rsi()

        # Calculate Average True Range (ATR)
        atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14)
        df['atr'] = atr.average_true_range()

        # Calculate Relative ATR (RATR) or Normalized ATR (NATR)
        avg_close = df['close'].rolling(window=14).mean()  # Adjust the window as needed
        df['ratr'] = df['atr'] / avg_close

        return df

    def analyze_crypto(self):
        analyzed_cryptos = []
        for symbol in self.symbols:
            try:
                df = self.fetch_data(symbol)
                if df is None:
                    continue
                df = self.calculate_indicators(df)
                if df is None:
                    continue
                for i in range(0, self.candles):
                    last_row = df.iloc[-i-1]
                    last_last_row = df.iloc[-i-2]
                    analyzed_cryptos.append({
                        'Symbol': symbol,
                        'timestamp': last_row['timestamp'],
                        'Open': last_row['open'],
                        'Close': last_row['close'],
                        'Low': last_row['low'],
                        'High': last_row['high'],
                        'MACD histogram': last_row['macd_histogram'],
                        'MACD': last_row['macd'],
                        'MACD Signal': last_row['macd_signal'],
                        'MACD n-1': last_last_row['macd'],
                        'MACD n-1 Signal': last_last_row['macd_signal'],
                        'St k': last_row['stoch_osc_k'],
                        'St d': last_row['stoch_osc_d'],
                        'RSI': last_row['rsi'],
                    })
            except:
                continue
        df = pd.DataFrame(analyzed_cryptos)

        # Set display options to show all columns in one line
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        # print(df)
        return df