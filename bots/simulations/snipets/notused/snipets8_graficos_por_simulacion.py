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
from matplotlib.backends.backend_agg import FigureCanvasAgg


django.setup()

from app.models import *
star_date = datetime(2024, 1, 1)
end_date = datetime(2024, 5, 31)
sim = 1
sl = 0.1
rsi = 6
stoch_open = 0.3
tp_sl_r = 2

result = Closed_position_sim.objects.values(
    # 'close_date',  # Truncar la fecha a días

    'sl_limit',
    'rsi_open',
    'simulation',
    'stoch_open',
    'tp_sl_ratio'
).filter(close_date__range=(star_date, end_date),
         simulation=sim,
         rsi_open=rsi,
         sl_limit=sl,
         stoch_open=stoch_open,
         tp_sl_ratio=tp_sl_r,
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

# Get unique simulation numbers
simulations = Closed_position_sim.objects.filter(simulation=sim, rsi_open=rsi, sl_limit=sl, stoch_open=stoch_open, tp_sl_ratio=tp_sl_r).filter(close_date__range=(star_date, end_date)).values_list('simulation', flat=True).distinct()

# Create a plot for each simulation number
fig, ax = plt.subplots(figsize=(16, 9))

for simulation in simulations:
    result = Closed_position_sim.objects.values(
        'close_date',
        'simulation',
        'sl_limit',
        'rsi_open',
        'stoch_open',
        'tp_sl_ratio',
    ).filter(close_date__range=(star_date, end_date),
             simulation=simulation,
             rsi_open=rsi,
             sl_limit=sl,
             stoch_open=stoch_open,
             tp_sl_ratio=tp_sl_r,
    ).annotate(
        pnl_total=Round(Sum('profit'), 2),
    )

    # Crear un DataFrame a partir de los resultados obtenidos
    data = {
        'Fecha': [entry['close_date'] for entry in result],
        f'Retorno acumulado - Sim {simulation}': [entry['pnl_total'] for entry in result],
    }

    df_result = pd.DataFrame(data)
    df_result['Fecha'] = pd.to_datetime(df_result['Fecha'])

    # Sumar los valores de 'Retorno diario' para fechas duplicadas
    df_result[f'Retorno acumulado - Sim {simulation}'] = df_result[f'Retorno acumulado - Sim {simulation}'].cumsum()

    # Plot the line for the current simulation
    ax.plot(df_result['Fecha'], df_result[f'Retorno acumulado - Sim {simulation}'], label=f'Sim {simulation}', linewidth=2)


# Configurar los ticks y etiquetas del eje x
months = mdates.MonthLocator()
months_fmt = mdates.DateFormatter('%Y-%m')

# Utilizamos DateLocator y DateFormatter para establecer la escala de las fechas
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(months_fmt)

# Añadir líneas verticales punteadas al final de cada año
for year in range(star_date.year, end_date.year):
    last_day_of_year = datetime(year, 12, 31)
    ax.vlines(last_day_of_year, ymin=0, ymax=ax.get_ylim()[1], colors='gray', linestyles='dashed', linewidth=1)

# Añadir líneas horizontales punteadas cada 1000 unidades en el eje y
for y in range(0, int(ax.get_ylim()[1]), 100):
    ax.hlines(y, xmin=star_date, xmax=end_date, colors='gray', linestyles='dashed', linewidth=1)


plt.xticks(rotation=90, size=12)
plt.legend(loc='upper left')
plt.title('Evolución de la Rentabilidad Acumulada Mes a Mes por Simulación', size=24)
plt.show()