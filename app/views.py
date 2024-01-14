from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, FloatField, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When, StdDev
from .models import *
from datetime import datetime, timedelta

@login_required

# def analisis(request, year=None, month=None, trimestre=None, semestre=None):
#     # Check if start_date and end_date are not provided in the URL
#     if not year and not month:
#         # Set default date range for the first semester of 2023
#         year = '2023'
#         month = '1'
#         start_date = '2023-01-01'
#         end_date = '2023-01-31'
#     else:
#         # Parse the start_date and end_date as datetime objects
#         start_date = datetime.strptime(start_date, '%Y-%m-%d')
#         end_date = datetime.strptime(end_date, '%Y-%m-%d')
#
#     # Use start_date and end_date in your query
#     result = Closed_position_sim.objects.values(
#         'symbol__symbol', 'type',
#         ).filter(
#             close_date__range=(start_date, end_date)
#         ).annotate(
#             pnl_total=Sum('profit'),
#             positions=Count('id'),
#             TP=Count(Case(When(profit__gt=0, then=1))),
#             SL=Count(Case(When(profit__lt=0, then=1))),
#             pnl_average=Avg('profit'),
#             total_fee=Sum('fee'),
#             avg_duration=ExpressionWrapper(
#                 Avg(
#                     (F('close_date') - F('open_date')) / 60000000,
#                     output_field=IntegerField()
#                 ),
#                 output_field=IntegerField()
#             ),
#             tp_esperado=ExpressionWrapper(
#                 Avg(
#                     (F('tp_price') / F('entry_price')) - 1,
#                     output_field=FloatField()
#                 ),
#                 output_field=FloatField()
#             ),
#         ).order_by('pnl_total')
#
#     return render(request, 'analisis.html', {'lista':result})

def analisis(request, year=None, month=None, symbol=None):
    # Determine the date range based on the URL pattern
    if month:
        # Monthly analysis
        start_date = datetime(int(year), int(month), 1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    else:
        if year:
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year), 12, 31)
        else:
            start_date = datetime(2023, 7, 1)
            end_date = datetime(2023, 12, 31)

    result = Closed_position_sim.objects.values(
        # 'symbol__symbol',
        'simulation', 'tp_sl_ratio', 'sl_low_limit', 'sl_limit', 'ratr',
         'type' # 'rsi_open',# 'stoch_open'
    ).filter(
          close_date__range=(start_date, end_date),
          tp_sl_ratio=1.5,
          sl_low_limit=0.01, sl_limit=0.1,
          simulation=443500000,
          # tp_sl_ratio=4,
          ratr=0.0075,
          # symbol__symbol='SOLUSDT',

    ).annotate(
        pnl_total=Sum('profit'),
        positions=Count('id'),
        TP=Count(Case(When(profit__gt=0, then=1))),
        # TPrsi=Count(Case(When(close_method='TPrsi', then=1))),
        # SLrsi=Count(Case(When(close_method='SLrsi', then=1))),
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
        max_pnl=Max('profit'),
        min_pnl=Min('profit'),
        avg_pnl_tp=Avg(Case(When(close_method='TP', then='profit'), output_field=FloatField())),
        avg_pnl_sl=Avg(Case(When(close_method='SL', then='profit'), output_field=FloatField())),
    ).order_by('-pnl_total')
    # If a symbol is specified, filter the results for that symbol
    if symbol:
        result = result.filter(symbol__symbol=symbol)
    # In your view or context data
    month_choices = [
        ('1', 'Jan'),
        ('2', 'Feb'),
        ('3', 'Mar'),
        ('4', 'Apr'),
        ('5', 'May'),
        ('6', 'Jun'),
        ('7', 'Jul'),
        ('8', 'Aug'),
        ('9', 'Sep'),
        ('10', 'Oct'),
        ('11', 'Nov'),
        ('12', 'Dec'),
    ]
    return render(request, 'analisis.html', {'lista': result, 'year': year, 'month': month, 'symbol': symbol,
                                             'month_choices':month_choices})

