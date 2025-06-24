from django.conf import settings
import django
import pandas as pd
import ta
import numpy as np
import ta.trend as trend
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

# Load your dataset into a Pandas DataFrame (replace 'your_dataset.csv' with your actual file path)
path = "../../Crypto_Get_samples/Get_row_data/USDT9/5m/"
symbols = Symbol.objects.filter(find_in_api=True)#.filter(id__gt=38)
for s in symbols:
    print("simulando " + str(s.symbol))
    symbol = s.symbol
    csv_file_path = f"{path}{symbol}_simulation.csv"

    # Read your data into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Reverse the order of the DataFrame
    df = df[::-1].reset_index(drop=True)

    # EMA para microtendencia
    df['ema_9'] = trend.EMAIndicator(df['Close'], window=9).ema_indicator()

    # Volumen promedio corto
    df['vol_ma10'] = df['Volume'].rolling(window=10).mean()

    # Vela envolvente
    df['bullish_engulfing'] = (
            (df['Close'] > df['Open']) &
            (df['Close'].shift(1) < df['Open'].shift(1)) &
            (df['Close'] > df['Open'].shift(1)) &
            (df['Open'] < df['Close'].shift(1))
    )

    df['bearish_engulfing'] = (
            (df['Close'] < df['Open']) &
            (df['Close'].shift(1) > df['Open'].shift(1)) &
            (df['Close'] < df['Open'].shift(1)) &
            (df['Open'] > df['Close'].shift(1))
    )

    # Pinbar bullish/bearish
    body = abs(df['Close'] - df['Open'])
    df['pinbar_bullish'] = (
        ((df[['Open', 'Close']].min(axis=1) - df['Low']) > 1.5 * body)
    )
    df['pinbar_bearish'] = (
        ((df['High'] - df[['Open', 'Close']].max(axis=1)) > 1.5 * body)
    )

    # Volumen explosivo
    df['volume_burst'] = df['Volume'] > df['vol_ma10']

    # Entrada refinada
    df['entry_long'] = (
            (df['Close'] > df['ema_9']) &
            df['volume_burst'] &
            (df['bullish_engulfing'] | df['pinbar_bullish'])
    )

    df['entry_short'] = (
            (df['Close'] < df['ema_9']) &
            df['volume_burst'] &
            (df['bearish_engulfing'] | df['pinbar_bearish'])
    )



    df = df[::-1].reset_index(drop=True)

    # Save the DataFrame back to a CSV file
    output_csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
    df.to_csv(output_csv_file_path, index=False)
    print(f"Saved DataFrame with indicators to {output_csv_file_path}")