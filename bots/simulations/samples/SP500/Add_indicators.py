import pandas as pd
import ta


def calculate_sp500_indicators(input_csv="data/sp500_1d.csv", output_csv="data/sp500_indicators.csv"):
    # Leer datos
    df = pd.read_csv(input_csv)

    # Convertir Date a datetime
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # Calcular indicadores
    # EMA
    df["EMA_50"] = ta.trend.EMAIndicator(df["Close"], window=50).ema_indicator()
    df["EMA_100"] = ta.trend.EMAIndicator(df["Close"], window=100).ema_indicator()
    # Distancia porcentual entre Close y EMA
    df["D_EMA_50"] = ((df["Close"] - df["EMA_50"]) / df["EMA_50"]) * 100
    df["D_EMA_100"] = ((df["Close"] - df["EMA_100"]) / df["EMA_100"]) * 100

    # MACD
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"] = macd.macd_diff()

    # # Crecimiento del histograma MACD (1 si positivo, 0 si negativo)
    # df["MACD_gr"] = (df["MACD_Hist"].diff() > 0).astype(int)

    # Crecimiento absoluto del histograma MACD
    df["MACD_dif"] = df["MACD_Hist"].diff()

    # RSI
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    # ATR
    df["ATR"] = ta.volatility.AverageTrueRange(
        high=df["High"], low=df["Low"], close=df["Close"], window=14
    ).average_true_range()

    print(df)
    # Guardar con indicadores
    df.to_csv(output_csv)
    print(f"Indicadores calculados y guardados en: {output_csv}")

    return df


# Ejemplo de uso
if __name__ == "__main__":
    calculate_sp500_indicators()