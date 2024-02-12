from django.conf import settings
import django
from datetime import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Count, Sum, Case, When, Q, F, Max


# settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

star_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
pnl = 0
for i in range(0, 42):
    result = Closed_position_sim.objects.values(
          'symbol__symbol',# 'type',#, 'tp_sl_ratio', 'sl_limit' 'rsi_open', 'stoch_open',
          'simulation',
          'tp_sl_ratio', 'sl_limit', 'sl_low_limit',
          # 'ratr',
          'simulation',
    ).filter(close_date__range=(star_date, end_date)).filter(symbol_id=i).filter(
        simulation=450199963, rsi_open=6, sl_limit=0.1).annotate(
        positions=Count('id'),
        pnl_total=Sum('profit'),
        positive_pnl_count=Count(Case(When(profit__gt=0, then=1))),
        negative_pnl_count=Count(Case(When(profit__lt=0, then=1))),
        pnl_average=Avg('profit'),
        total_fee=Sum('fee'),
    ).filter(pnl_total__gt=-25).order_by('symbol', '-pnl_total')[0:1]
    # ).filter(pnl_total__gt=0).order_by('symbol', '-pnl_total')[0:1]
    # Now the result will contain the statistics calculated for each combin
    for entry in result:
        print(entry)
        pnl += entry['pnl_total']
        # Optimum_parameter(
        #     symbol_id=entry['symbol'],
        #     timeframe=240,
        #     tp_sl_ratio=entry['tp_sl_ratio'],
        #     sl_limit=0.1,
        #     sl_low_limit=0.01,
        #     open_rsi=6,
        #     pnl=round(entry['pnl_total'], 2),
        #     simulation=entry['simulation'],
        #     pnl_av=entry['pnl_average']
        # ).save()

print(" total PNL con bola de cristal : " + str(pnl))
