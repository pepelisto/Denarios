import yfinance as yf
import pandas as pd
import os

def download_sp500_daily_csv(
    symbol="^GSPC",  # "^GSPC" = índice S&P 500 en Yahoo Finance
    period="5y",     # Últimos 3 años
    output_path="data/sp500_1d.csv"
):
    """
    Descarga datos diarios del S&P 500 (o el símbolo que indiques)
    desde Yahoo Finance para el período especificado
    y los guarda en un archivo CSV.
    """

    # Crear la carpeta de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Descargar datos diarios
    df = yf.download(symbol, period=period, interval="1d")

    # Asegurar que el índice sea de tipo DateTime
    df.index = pd.to_datetime(df.index)


    # Limpieza del DataFrame
    # 1. Quitar el MultiIndex dejando solo las columnas relevantes
    df.columns.name = None  # Eliminar el nombre de las columnas ("Ticker")
    df.reset_index(inplace=True)  # Mover el índice (Date) a una columna normal

    # 2. Renombrar las columnas
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]

    # 3. Convertir "Date" al formato datetime, si no lo está
    df["Date"] = pd.to_datetime(df["Date"])


    print(df)
    # Guardar el DataFrame en CSV
    df.to_csv(output_path, index=False)
    print(f"Archivo guardado en: {output_path}")

if __name__ == "__main__":
    # Ejemplo de uso
    download_sp500_daily_csv()