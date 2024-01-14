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
   #      simulation=4435600000,
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
)

# Imprimir los valores antes de la creación del DataFrame
print("Valores antes de crear el DataFrame:")
for entry in result:
    print(entry)


# Now the result will contain the statistics calculated for each combination

# Crear un DataFrame a partir de los resultados obtenidos
data = {
    'Fecha': [entry['close_date'] for entry in result],
    'Retorno diario': [entry['pnl_total'] for entry in result],
}

df_result = pd.DataFrame(data)
df_result['Fecha'] = pd.to_datetime(df_result['Fecha'])

# Sumar los valores de 'Retorno diario' para fechas duplicadas
df_result['Retorno acumulado'] = df_result['Retorno diario'].cumsum()

# Graficar los resultados
fig, ax = plt.subplots(figsize=(16, 9))
ax.plot(df_result['Fecha'], df_result['Retorno acumulado'], label='Rentabilidad acumulada', color='blue', linewidth=3)
ax.legend(loc='upper left')

# Configurar los ticks y etiquetas del eje x
months = mdates.MonthLocator()
months_fmt = mdates.DateFormatter('%Y-%m')

# Utilizamos DateLocator y DateFormatter para establecer la escala de las fechas
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(months_fmt)

plt.xticks(rotation=90, size=12)
plt.title('Evolución de la Rentabilidad Acumulada Mes a Mes', size=24)
plt.show()