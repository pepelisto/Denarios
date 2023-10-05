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
path = "../samples/USDT/2023_60m/"
symbols = Symbol.objects.filter(find_in_api=True)
for s in symbols:
    print("simulando " + str(s.symbol))
    symbol = s.symbol
    csv_file_path = f"{path}{symbol}_simulation.csv"

    # Read your data into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Reverse the order of the DataFrame
    df = df[::-1].reset_index(drop=True)

    # Calculate RSI
    rsi = ta.momentum.RSIIndicator(df['Close'], window=56)
    df['rsi_56'] = rsi.rsi()

    # # Calculate RSI
    # rsi = ta.momentum.RSIIndicator(df['Close'], window=112)
    # df['rsi_112'] = rsi.rsi()
    #
    # # Calculate RSI
    # rsi = ta.momentum.RSIIndicator(df['Close'], window=224)
    # df['rsi_224'] = rsi.rsi()

    df = df[::-1].reset_index(drop=True)

    # Save the DataFrame back to a CSV file
    output_csv_file_path = f"{path}{symbol}_simulation_with_indicators.csv"
    df.to_csv(output_csv_file_path, index=False)
    print(f"Saved DataFrame with indicators to {output_csv_file_path}")