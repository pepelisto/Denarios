from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, FloatField, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *


result = Closed_position_sim.objects.values(
    'symbol__symbol', 'type',
).annotate(
    pnl_total=Sum('profit'),
    positions=Count('id'),
    TP=Count(Case(When(profit__gt=0, then=1))),
    SL=Count(Case(When(profit__lt=0, then=1))),
    pnl_average=Avg('profit'),
    total_fee=Sum('fee'),
    avg_duration=ExpressionWrapper(
        Avg(
            (F('close_date') - F('open_date')) / 60000000,
            output_field=IntegerField()
        ),
        output_field=IntegerField()
    ),
    tp_esperado = ExpressionWrapper(
        Avg(
            (F('tp_price') / F('entry_price')) - 1,
            output_field=FloatField()
        ),
        output_field=FloatField()
    ),
    # avg_roe=Avg('roe'),
    # max_roe=Max('roe'),
    # min_roe=Min('roe'),
    # rsi_count=Count('id', filter=models.Q(close_method='RSI'))
).order_by('pnl_total')

# Now the result will contain the statistics calculated for each combination
for entry in result:
    print(entry)

