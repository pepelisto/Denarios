import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Cargar tus datos, asegúrate de tener columnas relevantes como 'Close', 'Stoch', 'RSI', 'MACD', etc.
path = "samples/2023_4h/"
csv_file_path = f"{path}WAVESUSDT_simulation_with_indicators.csv"
df = pd.read_csv(csv_file_path)

# Omitir las últimas 200 filas y revertir el DataFrame
df = df.iloc[:-200].iloc[::-1].reset_index(drop=True)

# Crear nueva columna 'NextReversion' basada en el umbral deseado
threshold = 0.01  # ajusta este valor según tus criterios
df['NextReversion'] = (df['Open'] - df['Close'].shift(-1)) > threshold
df['NextReversion'] = df['NextReversion'].astype(int)

# Crear la columna 'Class' como la etiqueta de clase
df['Class'] = (df['Open'] - df['Close'].shift(-1)) > threshold
df['Class'] = df['Class'].astype(int)

# Separar características (X) y etiquetas de clase (y)
X = df[['RSI', 'Stoch', 'MACD', 'PriceVariation']]
y = df['Class']

# Dividir datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear y entrenar el modelo (utiliza tu modelo específico aquí)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Realizar predicciones en el conjunto de prueba
predictions = model.predict(X_test)

# Calcular métricas de rendimiento
accuracy = accuracy_score(y_test, predictions)
classification_report_result = classification_report(y_test, predictions)

# Imprimir métricas
print(f'Accuracy: {accuracy}')
print(f'Classification Report:\n{classification_report_result}')