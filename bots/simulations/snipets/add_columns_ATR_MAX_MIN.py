from django.conf import settings
import django
import pandas as pd
import ta
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

# Load your dataset into a Pandas DataFrame (replace 'your_dataset.csv' with your actual file path)
path = "../samples/USDT6/4h/"
symbols = Symbol.objects.filter(find_in_api=True)#.filter(id__gt=38)
for s in symbols:
    print("simulando " + str(s.symbol))
    symbol = s.symbol
    csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"

    # Read your data into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Reverse the order of the DataFrame
    df = df[::-1].reset_index(drop=True)

    # Add a new column 'max_high_20' with the maximum value of 'high' over the last 20 rows
    df['max_high_20'] = df['High'].rolling(window=20, min_periods=1).max()
    df['min_low_20'] = df['Low'].rolling(window=20, min_periods=1).min()

    df['max_high_10'] = df['High'].rolling(window=10, min_periods=1).max()
    df['min_low_10'] = df['Low'].rolling(window=10, min_periods=1).min()

    # Step 1: Calculate True Range (TR)
    df['high-low'] = df['High'] - df['Low']
    df['high-close_prev'] = abs(df['High'] - df['Close'].shift(1))
    df['low-close_prev'] = abs(df['Low'] - df['Close'].shift(1))
    df['true_range'] = df[['high-low', 'high-close_prev', 'low-close_prev']].max(axis=1)

    # Step 2: Calculate Average True Range (ATR)
    atr_period = 14  # You can adjust this period as needed
    df['atr'] = df['true_range'].rolling(window=atr_period, min_periods=1).mean()

    # Drop intermediate columns used for TR calculation
    df = df.drop(['high-low', 'high-close_prev', 'low-close_prev'], axis=1)

    df = df[::-1].reset_index(drop=True)

    # Save the DataFrame back to a CSV file
    output_csv_file_path = f"{path}{symbol}_simulation_with_indicators_2.csv"
    df.to_csv(output_csv_file_path, index=False)
    print(f"Saved DataFrame with indicators to {output_csv_file_path}")