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
    ExpressionWrapper, F, Sum, IntegerField, FloatField, Case, When, StdDev

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
# settings.configure()
# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)

django.setup()
from app.models import *

star_date = datetime(2020, 1, 1)
end_date = datetime(2025, 12, 31)
# Calculamos la diferencia en meses
months = (end_date.year - star_date.year) * 12 + end_date.month - star_date.month


result = Closed_position_sim.objects.values(
            # 'symbol__symbol',
            'type',#,
        'tp_sl_ratio',
        # 'sl_limit' ,
        'rsi_open',
        'simulation',
        # 'stoch_open',

          # 'sim_info',
  ).filter(close_date__range=(star_date, end_date),
           # symbol__symbol='BTCUSDT',
           # simulation=5151,
           # sl_limit=0.1,# sl_low_limit=0.01,# ratr=0.05,# type='SELL',
           #  rsi_open=6,
           # tp_sl_ratio=2,
          ).exclude(simulation=450527222)\
    .annotate(
    positions=Count('id'),
    pnl_total=Round(Sum('profit'), 2),
    stddev_pnl=Round(StdDev('profit'), 2),
    sharpe_ratio=ExpressionWrapper(
        Round((((Sum('profit')/months)*12)/Avg('quantity')) / StdDev('profit'), 2),
        output_field=FloatField()),
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
    avg_dur_pos_prof = ExpressionWrapper(
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
).order_by('pnl_total')

# Now the result will contain the statistics calculated for each combination
for entry in result:
    print(entry)

