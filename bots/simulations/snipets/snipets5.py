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
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
# settings.configure()
# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)

django.setup()
from app.models import *

star_date = datetime(2020, 1, 1)
end_date = datetime(2020, 12, 30)

result = Closed_position_sim.objects.values(
          #   'symbol__symbol',
          #'type',#, 'tp_sl_ratio', 'sl_limit' 'rsi_open', 'stoch_open',
      'simulation',
          # 'sim_info',
      'tp_sl_ratio',
      'sl_limit',#
      'sl_low_limit',
      'ratr',

              # 'rsi_open'
        # 'rsi_open', 'stoch_open',
     # 'simulation',
  ).filter(close_date__range=(star_date, end_date),
           # symbol__symbol='BTCUSDT',
            simulation__startswith=437,
             # tp_sl_ratio=4,
           # sl_limit=0.02,
           # sl_low_limit=0.01,
           #   ratr=0.05,
         # type='SELL',
         ).annotate(
    positions=Count('id'),
    pnl_total=Sum('profit'),
    max_pnl=Max('profit'),
    min_pnl=Min('profit'),
    pos_pnl_=Count(Case(When(profit__gt=0, then=1))),
    neg_pnl=Count(Case(When(profit__lt=0, then=1))),
    pnl_av=Avg('profit'),
    total_fee=Sum('fee'),
    avg_duration=ExpressionWrapper(
        Avg(
            (F('close_date') - F('open_date')) / 60000000,
            output_field=IntegerField()
        ),
        output_field=IntegerField()
    ),
    avg_duration_positive_profit = ExpressionWrapper(
        Avg(
            Case(
                When(profit__gt=0, then=(F('close_date') - F('open_date')) / 60000000),
                output_field=IntegerField()
            )
        ),
        output_field=IntegerField()
    ),
    avg_duration_negative_profit = ExpressionWrapper(
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

