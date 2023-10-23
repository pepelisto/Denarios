from django.conf import settings
import django
from datetime import datetime, timedelta
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Sum, Q
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

data = 30
data_sim = 30

star_date_historic = datetime(2022, 12, 1)
end_date_historic = star_date_historic + timedelta(days=data)
star_date = end_date_historic
end_date = star_date + timedelta(days=data_sim)

PNLacumulado = 0
POSTITIONS = 0

for k in range(1, 15):
    result = Closed_position_sim.objects.values(
         'symbol',
         'simulation',
    ).filter(Q(close_date__range=(star_date_historic, end_date_historic)) &
             (Q(simulation=6009))).filter(tp_sl_ratio=3, sl_limit=0.04, sl_low_limit=0.015).\
        annotate(pnl_total=Sum('profit')).filter(pnl_total__gt=20).order_by('pnl_total').values_list(
        'symbol_id', flat=True
    )
    sim = Closed_position_sim.objects.values(
         'symbol',
         'simulation',
    ).filter(
            symbol_id__in=result,
            close_date__range=(star_date, end_date),
            simulation=6009
    ).annotate(
            pnl_total=Sum('profit'),
            positions=Count('id'),
    ).order_by('pnl_total')

    pnl_mes = sum(sim.values_list('pnl_total', flat=True))
    position = sum(sim.values_list('positions', flat=True))

    POSTITIONS += position
    PNLacumulado += pnl_mes
    print('mes ' + str(star_date) + ' PNL  ' + str(pnl_mes))

    star_date_historic = end_date - timedelta(days=data)
    end_date_historic = end_date
    star_date = end_date_historic
    end_date = star_date + timedelta(days=data_sim)


print(' PNL total acumulado  ' + str(PNLacumulado))
print(' Positions  ' + str(POSTITIONS))
print(' pnl avg  ' + str(PNLacumulado / POSTITIONS))
