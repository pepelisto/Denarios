import pandas as pd

def merge_external_data(main_df_path, external_df_path, external_columns, merge_column="timestamp", date_column="Date", prefix="external", market_close_hour=20):
    """
    Combina el DataFrame principal con otro DataFrame externo basado en el último valor disponible.

    :param main_df_path: Ruta del archivo CSV del DataFrame principal.
    :param external_df_path: Ruta del archivo CSV del DataFrame externo (por ejemplo, SP500).
    :param external_columns: Lista de columnas relevantes del DataFrame externo.
    :param merge_column: Columna de referencia en el DataFrame principal (por defecto, 'timestamp').
    :param date_column: Columna de referencia en el DataFrame externo (por defecto, 'Date').
    :param prefix: Prefijo para las columnas del DataFrame externo (por defecto, 'external').
    :return: DataFrame combinado.
    """
    # Leer DataFrames
    main_df = pd.read_csv(main_df_path, parse_dates=[merge_column])
    external_df = pd.read_csv(external_df_path, parse_dates=[date_column])

    # Filtrar columnas relevantes del DataFrame externo
    external_df = external_df[[date_column] + external_columns]

    # Renombrar las columnas del DataFrame externo con el prefijo
    rename_mapping = {col: f"{col}_{prefix}" for col in external_columns if col != date_column}
    external_df.rename(columns=rename_mapping, inplace=True)

    # Desplazar los datos del DataFrame externo para obtener siempre el día anterior
    external_df = external_df.sort_values(by=date_column)
    external_df[date_column] = external_df[date_column] + pd.Timedelta(days=1)

    # Establecer índices temporales
    main_df.set_index(merge_column, inplace=True)
    external_df.set_index(date_column, inplace=True)

    # Sincronizar usando el último cierre disponible
    merged_df = pd.merge_asof(
        main_df.sort_index(),
        external_df.sort_index(),
        left_index=True,
        right_index=True,
        direction="backward"
    )

    # Restablecer el índice y devolver el DataFrame combinado
    merged_df.reset_index(inplace=True)

    # Obtener el orden actual de las columnas
    columns = list(merged_df.columns)

    # Intercambiar las posiciones de la columna 1 y 2
    columns[0], columns[1] = columns[1], columns[0]

    # Reorganizar las columnas en el DataFrame
    merged_df = merged_df[columns]

    # Ordenar el DataFrame de la fecha más reciente a la más antigua
    merged_df = merged_df.iloc[::-1].reset_index(drop=True)

    return merged_df