from django.conf import settings
import django
from datetime import datetime
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

symbols = Symbol.objects.filter(find_in_api=True)
for s in symbols:
    symbol = s.symbol
    positives = 0
    pnl_suma = 0
    for i in [1,2,3,4,5,6,7,8,9,10,11]:
        star_date = datetime(2023, i, 2)
        end_date = datetime(2023, i+1, 1)
        result = Closed_position_sim.objects.values('simulation', 'symbol__symbol').filter(
            symbol__symbol=symbol,
            close_date__range=(star_date, end_date),
            simulation=4444,).\
            annotate(
                pnl_total=Sum('profit'),
            ).order_by('pnl_total')

        for entry in result:
            if entry['pnl_total'] > 0:
                positives += 1
            pnl_suma += entry['pnl_total']
    pnl_avg = pnl_suma / 9
    print(symbol + ' -tasa ' + str(positives) + ' -pnl suma ' + str(pnl_suma))
