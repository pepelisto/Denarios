import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Cargar tus datos, asegúrate de tener columnas relevantes como 'Close', 'High', 'Low', 'RSI', 'Stoch', 'MACD', etc.
path = "samples/2023_4h/"
csv_file_path = f"{path}WAVESUSDT_simulation_with_indicators.csv"
df = pd.read_csv(csv_file_path)

# Omitir las últimas 200 filas y revertir el DataFrame
df = df.iloc[:-200].iloc[::-1].reset_index(drop=True)

# Crear características del periodo anterior
df['Close_Prev'] = df['Close'].shift(1)
df['High_Prev'] = df['High'].shift(1)
df['Low_Prev'] = df['Low'].shift(1)
df['RSI_Prev'] = df['RSI'].shift(1)
df['Stoch_Prev'] = df['St k'].shift(1)
df['MACD_Prev'] = df['MACD'].shift(1)

# Eliminar filas con valores nulos resultantes de la creación de características
df = df.dropna()

# Definir tu modelo y características de entrada (X) y objetivo (y)
X = df[['Close_Prev', 'High_Prev', 'Low_Prev', 'RSI_Prev', 'Stoch_Prev', 'MACD_Prev']]
y = df['Close']

# Dividir los datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Inicializar y entrenar el modelo de regresión
model = LinearRegression()
model.fit(X_train, y_train)

# Realizar predicciones en el conjunto de prueba
predictions = model.predict(X_test)

# Calcular métricas de rendimiento (MAE, MSE, RMSE)
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)

# Imprimir métricas de rendimiento
print(f'MAE: {mae}')
print(f'MSE: {mse}')
print(f'RMSE: {rmse}')