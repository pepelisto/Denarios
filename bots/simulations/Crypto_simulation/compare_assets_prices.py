
import pandas as pd
from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
# from Funciones.DB_habndle import *
from CFunciones.Merger_df import merge_external_data
from Funciones.print_comparisson import plot_close_trajectories

django.setup()

from app.models import *


path = "../samples/USDT7/4h/"
pathSP500 = "../samples/SP500/data/"
symbols = Symbol.objects.filter(find_in_api=True)
i = 1
for s in symbols:

    symbol = s.symbol
    csv_file_path = f"{path}{symbol}_simulation_3.csv"

    # Combinar el DataFrame principal con SP500
    external_columns = ["MACD_Hist", "MACD_dif", "Close", "EMA_50", "D_EMA_50", "RSI", "ATR"]
    df = merge_external_data(
        main_df_path=csv_file_path,
        external_df_path=f"{pathSP500}sp500_indicators.csv",
        external_columns=external_columns,
        prefix="sp500",
        market_close_hour=20
    )

    # Llamar a la función para graficar
    plot_close_trajectories(
        df=df,
        symbol_close_col="Close",        # Close del símbolo
        external_close_col="Close_sp500",  # Close del SP500
        title="Comparación de Close: Symbol vs SP500"
    )

