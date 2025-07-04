from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, StdDev, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When
from datetime import datetime
from dateutil.relativedelta import relativedelta

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

periodos = 10
current_date = datetime(2023, 1, 1)
end_date_window = current_date + relativedelta(months=1)
total = 0

for i in range(1, 10):
    result = Closed_position_sim.objects.values(
         #'symbol__symbol', 'type'#
          'simulation',
         'tp_sl_ratio', 'sl_limit', 'sl_low_limit'
    ).filter(simulation=15, close_date__range=(current_date, end_date_window)).annotate(
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
        avg_roe=Avg('roe'),
        max_roe=Max('roe'),
        min_roe=Min('roe'),
        rsi_count=Count('id', filter=models.Q(close_method='RSI'))
    ).order_by('pnl_total')

    current_date = current_date + relativedelta(months=1)
    end_date_window = end_date_window + relativedelta(months=1)


    # Now the result will contain the statistics calculated for each combination
    for entry in result:
        print(entry)
    #     total += entry.pnl_total
    # print(total)
