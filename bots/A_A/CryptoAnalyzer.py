import requests
import pandas as pd
import ta


class CryptoAnalyzer:
    def __init__(self, symbols, interval, limit):
        self.symbols = symbols
        self.interval = interval
        self.limit = limit

    def fetch_data(self, symbol):
        url = f"https://fapi.binance.com/fapi/v1/markPriceKlines?symbol={symbol.upper()}&interval={self.interval}&limit={self.limit}"
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

        # Calculate Stochastic Oscillator
        stoch_osc = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)  # You can adjust the window and smooth_window as needed
        df['stoch_osc_k'] = stoch_osc.stoch()
        df['stoch_osc_d'] = stoch_osc.stoch_signal()

        # df['stoch_osc_k'] = ta.momentum.StochasticOscillator((df['high'], df['low'], df['close'], 14, 3))
        # df['stoch_osc_d'] = df['stoch_osc_k'].rolling(3).mean()


        # Calculate MACD
        macd = ta.trend.MACD(df['close'])
        df['macd_histogram'] = macd.macd_diff()

        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df['close'])
        df['rsi'] = rsi.rsi()

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