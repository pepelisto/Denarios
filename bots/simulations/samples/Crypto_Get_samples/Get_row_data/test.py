from binance.client import Client
import pandas as pd
from datetime import datetime

api_key = 'dMMzhZlQSknlim7rDobSSTkKF62fI1vlK0SCE7bksvW9PsY0Si5OKXA4oBxyvF6x'
api_secret = 'M0nhMnp9K4YvPn3O6Cb7BM6HlisMQ6NRkCeZWh4z7uIDqnqDljpPY8D2i8CsveNJ'

client = Client(api_key, api_secret)

def fetch_data(symbol, interval="5m", limit=1000, end_date=None):
    end_ts = int(end_date.timestamp() * 1000) if end_date else None

    candles = client.futures_klines(
        symbol=symbol,
        interval=interval,
        limit=limit,
        endTime=end_ts
    )

    df = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

    return df