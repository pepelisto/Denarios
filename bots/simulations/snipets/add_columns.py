from django.conf import settings
import django
import pandas as pd
import ta
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

# Load your dataset into a Pandas DataFrame (replace 'your_dataset.csv' with your actual file path)
path = "../samples/USDT2/2023_12h/"
symbols = Symbol.objects.filter(find_in_api=True)
for s in symbols:
    print("simulando " + str(s.symbol))
    symbol = s.symbol
    csv_file_path = f"{path}{symbol}_simulation.csv"

    # Read your data into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Reverse the order of the DataFrame
    df = df[::-1].reset_index(drop=True)

    # # Calculate Stochastic RSI
    stoch_rsi = ta.momentum.StochRSIIndicator(df['Close'])
    df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
    df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()

    # # Calculate RSI
    rsi = ta.momentum.RSIIndicator(df['Close'])
    df['rsi_regular'] = rsi.rsi()

    # # Calculate RSI
    # rsi = ta.momentum.RSIIndicator(df['Close'])
    # df['rsi_21'] = rsi.rsi()
    #
    # # Calculate MACD with fast period=6, slow period=12, and signal period=4
    macd = ta.trend.MACD(df['Close'], window_fast=6, window_slow=12, window_sign=4)
    df['macd_2'] = macd.macd()
    df['macd_signal_2'] = macd.macd_signal()
    df['macd_histogram_2'] = macd.macd_diff()
    # Calculate 50-period EMA
    # df['ema_50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    #
    # # Calculate 100-period EMA
    # df['ema_100'] = ta.trend.EMAIndicator(df['Close'], window=100).ema_indicator()

    df = df[::-1].reset_index(drop=True)

    # Save the DataFrame back to a CSV file
    output_csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
    df.to_csv(output_csv_file_path, index=False)
    print(f"Saved DataFrame with indicators to {output_csv_file_path}")