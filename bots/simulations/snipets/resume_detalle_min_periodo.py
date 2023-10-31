from django.conf import settings
import django
from datetime import datetime, timedelta
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When, FloatField

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *

star_date = datetime(2022, 10, 1)
end_date = datetime(2023, 10, 30)

result = Closed_position_sim.objects.values(
      # 'symbol__symbol',
      # 'type',
    'simulation', 'tp_sl_ratio', 'sl_low_limit', 'sl_limit', 'ratr'
        ).filter(close_date__range=(star_date, end_date),
                  simulation=444408  #, tp_sl_ratio=3, sl_limit=0.04, sl_low_limit=0.015
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
            max_pnl=Max('profit'),
            min_pnl=Min('profit'),
            TP=Count(Case(When(profit__gt=0, then=1))),
            SL=Count(Case(When(profit__lt=0, then=1))),
            avg_pnl_tp=Avg(Case(When(close_method='TP', then='profit'), output_field=FloatField())),
            avg_pnl_sl=Avg(Case(When(close_method='SL', then='profit'), output_field=FloatField())),
        ).order_by('pnl_total')

# Iterate through the simulation results
for e in result:
    # Define the conditions to retrieve positions for the current simulation
    conditions = {
         # 'symbol__symbol': e['symbol__symbol'],
        # 'type': e['type'],
        'ratr': e['ratr'],
        'simulation': e['simulation'],
        'tp_sl_ratio': e['tp_sl_ratio'],
        'sl_low_limit': e['sl_low_limit'],
        'sl_limit': e['sl_limit'],
        # 'rsi_open': e['rsi_open'],
        # 'stoch_open': e['stoch_open'],
        'close_date__range': (star_date, end_date),
    }

    # Retrieve positions for the current simulation
    positions = Closed_position_sim.objects.filter(**conditions).order_by('close_date')

    # Initialize variables for calculations
    max_pnl_negatives = 0
    current_pnl_negatives = 0
    max_pnl_positives = 0
    current_pnl_positives = 0
    pnl_suma = 0
    max_pnl_period = 0
    min_pnl_period = 0
    pnl_week = 0
    weekly_positive_count = 0
    total_weeks = 0

    # Calculate values by iterating through positions
    for position in positions:
        pnl = position.profit
        close_date = position.close_date

        # Calculate max consecutive PNL negatives
        if pnl < 0:
            current_pnl_negatives += 1
            max_pnl_negatives = max(max_pnl_negatives, current_pnl_negatives)
            current_pnl_positives = 0
        else:
            current_pnl_negatives = 0

        # Calculate max consecutive PNL positives
        if pnl > 0:
            current_pnl_positives += 1
            max_pnl_positives = max(max_pnl_positives, current_pnl_positives)
            current_pnl_negatives = 0
        else:
            current_pnl_positives = 0

        # Calculate max and min PNL period
        pnl_suma += pnl
        max_pnl_period = max(pnl_suma, max_pnl_period)
        min_pnl_period = min(pnl_suma, min_pnl_period)

        # Calculate weekly positive count
        pnl_week += pnl
        if close_date.weekday() == 6:  # Assuming Sunday is the end of the week
            total_weeks += 1
            if pnl_week > 0:
                weekly_positive_count += 1
            pnl_week = 0


    # Calculate the weekly win rate
    weekly_win_rate = weekly_positive_count / total_weeks if total_weeks > 0 else 0

    # Update the 'e' dictionary with calculated values
    e['max_pnl_neg'] = max_pnl_negatives
    e['max_pnl_pos'] = max_pnl_positives
    e['max_pnl_period'] = max_pnl_period
    e['min_pnl_period'] = min_pnl_period
    e['weekly_win_rate'] = weekly_win_rate
    e['ROE'] = e['pnl_total'] / (e['positions'] * 5)

for entry in result:
    print(entry)