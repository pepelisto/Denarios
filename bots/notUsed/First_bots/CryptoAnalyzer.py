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

        # Calculate Stochastic RSI
        stoch_rsi = ta.momentum.StochRSIIndicator(df['close'])
        df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
        df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()

        # Calculate MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()

        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df['close'])
        df['rsi'] = rsi.rsi()

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
                last_row = df.iloc[-1]
                # lest_last_row = df.iloc[-2]
                analyzed_cryptos.append({
                    'Symbol': symbol,
                    'timestamp': last_row['timestamp'],
                    'Open': last_row['open'],
                    'Close': last_row['close'],
                    'MACD histogram': last_row['macd_histogram'],
                    # 'MACD': last_row['macd'],
                    # 'MACD Signal': last_row['macd_signal'],
                    # 'MACD n-1': lest_last_row['macd'],
                    # 'MACD n-1 Signal': lest_last_row['macd_signal'],
                    'SRSI k': last_row['stoch_rsi_k'],
                    'SRSI d': last_row['stoch_rsi_d'],
                    'RSI': last_row['rsi'],
                })
            except:
                continue
        df = pd.DataFrame(analyzed_cryptos)
        # Set display options to show all columns in one line
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        print(df)
        return df