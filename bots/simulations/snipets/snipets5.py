from django.conf import settings
import django
from datetime import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

star_date = datetime(2023, 1, 1)
end_date = datetime(2023, 9, 30)

result = Closed_position_sim.objects.values(
     # 'symbol__symbol',
     # 'type',#, 'tp_sl_ratio', 'sl_limit' 'rsi_open', 'stoch_open',
     'simulation',
     'tp_sl_ratio', 'sl_limit', 'sl_low_limit',
      # 'rsi_open',# 'stoch_open',
     # 'simulation',
).filter(close_date__range=(star_date, end_date),
         # simulation=15,
         #  tp_sl_ratio=3, sl_limit=0.04, sl_low_limit=0.015,
         # type='SELL',
         ).annotate(
    positions=Count('id'),
    pnl_total=Sum('profit'),
    positive_pnl_count=Count(Case(When(profit__gt=0, then=1))),
    negative_pnl_count=Count(Case(When(profit__lt=0, then=1))),
    pnl_average=Avg('profit'),
    total_fee=Sum('fee'),
    avg_duration=ExpressionWrapper(
        Avg(
            (F('close_date') - F('open_date')) / 60000000,
            output_field=IntegerField()
        ),
        output_field=IntegerField()
    ),
).order_by('pnl_total')

# Now the result will contain the statistics calculated for each combination
for entry in result:
    print(entry)

