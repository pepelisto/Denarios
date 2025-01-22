import matplotlib.pyplot as plt


def plot_close_trajectories(df, symbol_close_col, external_close_col, title="Trajectoria de Close"):
    """
    Genera un gráfico que muestra la trayectoria del Close del símbolo y del externo.

    :param df: DataFrame que contiene los datos.
    :param symbol_close_col: Nombre de la columna del Close del símbolo.
    :param external_close_col: Nombre de la columna del Close del externo.
    :param title: Título del gráfico (opcional).
    """
    plt.figure(figsize=(12, 6))

    # Graficar las trayectorias
    plt.plot(df["timestamp"], df[symbol_close_col], label="Close Symbol", color="blue", linewidth=2)
    plt.plot(df["timestamp"], df[external_close_col], label="Close External", color="orange", linestyle="--",
             linewidth=2)

    # Configurar etiquetas y leyenda
    plt.xlabel("Fecha")
    plt.ylabel("Precio Close")
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    # Mostrar el gráfico
    plt.show()


def plot_return_trajectories(df, symbol_close_col, external_close_col, symbol_name, external_name="SP500",
                             title="Rentabilidad Acumulada"):
    """
    Genera un gráfico que muestra la rentabilidad acumulada de invertir 100 USD en el símbolo y el externo.

    :param df: DataFrame que contiene los datos.
    :param symbol_close_col: Nombre de la columna del Close del símbolo.
    :param external_close_col: Nombre de la columna del Close del externo.
    :param symbol_name: Nombre del símbolo (e.g., "BTCUSDT").
    :param external_name: Nombre del externo (por defecto, "SP500").
    :param title: Título del gráfico (opcional).
    """
    df = df.iloc[::-1].reset_index(drop=True)
    # Calcular rentabilidad acumulada
    df["Symbol_Return"] = (df[symbol_close_col] / df[symbol_close_col].iloc[0]) * 100
    df["External_Return"] = (df[external_close_col] / df[external_close_col].iloc[0]) * 100
    df = df.iloc[::-1].reset_index(drop=True)
    plt.figure(figsize=(12, 6))

    # Graficar rentabilidad acumulada
    plt.plot(df["timestamp"], df["Symbol_Return"], label=f"Rentabilidad {symbol_name}", color="blue", linewidth=2)
    plt.plot(df["timestamp"], df["External_Return"], label=f"Rentabilidad {external_name}", color="orange",
             linestyle="--", linewidth=2)

    # Configurar etiquetas y leyenda
    plt.xlabel("Fecha")
    plt.ylabel("Rentabilidad (%)")
    plt.title(f"{title}: {symbol_name} vs {external_name}")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    # Mostrar el gráfico
    plt.show()