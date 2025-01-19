"""
 PPPP   EEEEE  PPPP   EEEEE   L      I   SSSSS  TTTTT   OOO
 P   P  E      P   P  E       L      I  S         T    O   O
 PPPP   EEEE   PPPP   EEEE    L      I   SSS      T    O   O
 P      E      P      E       L      I       S    T    O   O
 P      EEEEE  P      EEEEE   LLLLL  I  SSSSS     T     OOO
 """


# from django.conf import settings
import django
from datetime import datetime

from django.db.models.functions import Round

from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count,\
    ExpressionWrapper, F, Sum, IntegerField, FloatField, Case, When
import pandas as pd
import django
from django.db.models.functions import Round
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from django.db.models.functions import TruncDate

django.setup()
from app.models import *

star_date = datetime(2020, 1, 1)
end_date = datetime(2023, 12, 30)

result = Closed_position_sim.objects.values(
    'close_date',  # Truncar la fecha a días
    'simulation',
).filter(close_date__range=(star_date, end_date),
         simulation=441560000,
).annotate(
    positions=Count('id'),
    pnl_total=Round(Sum('profit'), 2),
    max_pnl=Max('profit'),
    min_pnl=Min('profit'),
    pos_pnl_=Count(Case(When(profit__gt=0, then=1))),
    neg_pnl=Count(Case(When(profit__lt=0, then=1))),
    pnl_av=Round(Avg('profit'), 2),
    pnl_avg_std=Round(ExpressionWrapper(
        (Avg(F('profit')) / (Avg(F('quantity')) / 100)),
        output_field=FloatField()
    ), 2),
    avg_q=Round(Avg('quantity'), 2),
    fee=Round(Sum('fee'), 2),
    avg_duration=ExpressionWrapper(
        Avg(
            (F('close_date') - F('open_date')) / 60000000,
            output_field=IntegerField()
        ),
        output_field=IntegerField()
    ),
    avg_dur_pos_prof=ExpressionWrapper(
        Avg(
            Case(
                When(profit__gt=0, then=(F('close_date') - F('open_date')) / 60000000),
                output_field=IntegerField()
            )
        ),
        output_field=IntegerField()
    ),
    avg_dur_neg_prof=ExpressionWrapper(
        Avg(
            Case(
                When(profit__lt=0, then=(F('close_date') - F('open_date')) / 60000000),
                output_field=IntegerField()
            )
        ),
        output_field=IntegerField()
    )
).order_by('fecha_truncada')

# Imprimir los valores antes de la creación del DataFrame
print("Valores antes de crear el DataFrame:")
for entry in result:
    print(entry)

# Crear un DataFrame a partir de los resultados obtenidos
data = {
    'Fecha': [entry['close_date'] for entry in result],
    'Retorno acumulado': [entry['pnl_total'] for entry in result],
}

print("\nValores después de crear el DataFrame:")
print(pd.DataFrame(data))

df_result = pd.DataFrame(data)
df_result['Fecha'] = pd.to_datetime(df_result['Fecha'])

# Imprimir los valores después de la conversión de fechas
print("\nValores después de convertir a fechas:")
print(df_result)

# Sumar los valores de 'pnl_total' para fechas duplicadas
df_result = df_result.groupby('Fecha')['Retorno acumulado'].sum().reset_index()

# Imprimir los valores después de agrupar
print("\nValores después de agrupar:")
print(df_result)

# Agregar una fila al principio del dataframe con valor inicial 0
fila_inicial_df = pd.DataFrame({'Fecha': [star_date], 'Retorno acumulado': [0]})
df_result = pd.concat([fila_inicial_df, df_result], ignore_index=True)

# Imprimir los valores después de agregar la fila inicial
print("\nValores después de agregar la fila inicial:")
print(df_result)

# Calcular el retorno acumulado y ajustar a 100 como base
df_result['Retorno acumulado'] = (1 + df_result['Retorno acumulado']).cumprod() * 100

# Imprimir los valores finales antes de graficar
print("\nValores finales antes de graficar:")
print(df_result)

# Graficar los resultados
fig, ax = plt.subplots(figsize=(16, 9))
ax.step(df_result['Fecha'], df_result['Retorno acumulado'], label='Rentabilidad acumulada', color='blue', linewidth=3, where='post')
ax.legend(loc='upper left')

# Configurar los ticks y etiquetas del eje x
months = mdates.MonthLocator()
months_fmt = mdates.DateFormatter('%Y-%m')

# Asegurémonos de que las fechas estén correctamente representadas en el gráfico
ax.set_xlim(df_result['Fecha'].iloc[0], df_result['Fecha'].iloc[-1])

# Utilizamos DateLocator y DateFormatter para establecer la escala de las fechas
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(months_fmt)

plt.xticks(rotation=90, size=12)
plt.title('Evolución de la Rentabilidad Acumulada Mes a Mes', size=24)
plt.show()