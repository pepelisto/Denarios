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
path = "../../Crypto_Get_samples/Get_row_data/USDT9/1h/"
symbols = Symbol.objects.filter(find_in_api=True)#.filter(id__gt=38)
for s in symbols:
    print("simulando " + str(s.symbol))
    symbol = s.symbol
    csv_file_path = f"{path}{symbol}_simulation.csv"

    # Read your data into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Reverse the order of the DataFrame
    df = df[::-1].reset_index(drop=True)


    # Calculate RSI
    rsi = ta.momentum.RSIIndicator(df['Close'])
    df['rsi'] = rsi.rsi()

    # Calculate 100-period EMA
    df['ema_200'] = trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    df['ema_100'] = trend.EMAIndicator(df['Close'], window=100).ema_indicator()
    df['ema_50'] = trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['ema_20'] = trend.EMAIndicator(df['Close'], window=20).ema_indicator()

    # Volume promedio(vol_ma20)
    df['vol_ma20'] = df['Volume'].rolling(window=20).mean()

    # Tipo de vela (candle_type)
    # Puedes ajustar los criterios. Esto define la vela como:
    # - 'bullish_big' si es verde y cuerpo grande
    # - 'bearish_big' si es roja y cuerpo grande
    # - 'neutral' si el cuerpo es chico
    cuerpo = abs(df['Close'] - df['Open'])
    rango_total = df['High'] - df['Low']
    df['candle_type'] = np.where(
        (df['Close'] > df['Open']) & (cuerpo > 0.6 * rango_total), 'bullish_big',
        np.where((df['Close'] < df['Open']) & (cuerpo > 0.6 * rango_total), 'bearish_big', 'neutral')
    )

    df['pullback_zone'] = df.apply(
        lambda row: min(row['ema_20'], row['ema_50']) < row['Close'] < max(row['ema_20'], row['ema_50']),
        axis=1
    )
    # Condición booleana simple por vela
    df['trend_long_raw'] = (df['ema_20'] > df['ema_50']) & (df['ema_50'] > df['ema_200'])

    # Confirmación sostenida en 3 velas
    df['trend_long'] = df['trend_long_raw'].rolling(window=3).apply(lambda x: x.all(), raw=True).fillna(0).astype(
        bool)

    # Idem para short
    df['trend_short_raw'] = (df['ema_20'] < df['ema_50']) & (df['ema_50'] < df['ema_200'])
    df['trend_short'] = df['trend_short_raw'].rolling(window=3).apply(lambda x: x.all(), raw=True).fillna(0).astype(
        bool)

    # Para LONG: retroceso en vela roja (bearish), Volumen alto
    df['pullback_confirmed_long'] = (
            df['trend_long'] &
            df['pullback_zone'] &
            (df['candle_type'] == 'bearish_big') &
            (df['Volume'] > df['vol_ma20'])
    )

    # Para SHORT: retroceso en vela verde (bullish), Volumen alto
    df['pullback_confirmed_short'] = (
            df['trend_short'] &
            df['pullback_zone'] &
            (df['candle_type'] == 'bullish_big') &
            (df['Volume'] > df['vol_ma20'])
    )
    df = df[::-1].reset_index(drop=True)

    # Save the DataFrame back to a CSV file
    output_csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
    df.to_csv(output_csv_file_path, index=False)
    print(f"Saved DataFrame with indicators to {output_csv_file_path}")