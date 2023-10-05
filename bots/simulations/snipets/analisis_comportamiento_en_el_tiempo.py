from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from django.db.models import Avg, Max, Min, FloatField, Count, ExpressionWrapper, F, Sum, IntegerField, Case, When
from datetime import datetime, timedelta

settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()
from app.models import *


# Define the start and end dates
start_date = datetime(2022, 6, 7)
end_date = datetime(2023, 9, 8)

# Define the time window (in days) for analysis
time_lapse = 7  # You can change this value to adjust the window

symbols = Symbol.objects.filter(find_in_api=True)

for s in symbols:
    symbol = s.symbol

    # Initialize a list to store weekly pnl data
    pnl_data = []

    # Calculate the initial end date for the first window
    current_date = start_date
    end_date_window = current_date + timedelta(days=time_lapse)

    while end_date_window <= end_date:
        # Query the database for pnl data within the current window
        window_pnl = (
            Closed_position_sim.objects.values(
            'symbol__symbol', 'type', 'simulation', 'tp_sl_ratio', 'sl_limit',
            ).filter(close_date__range=(current_date, end_date_window), symbol__symbol=symbol, type='SELL',
                     simulation=1, tp_sl_ratio=3, sl_limit=0.02).annotate(
                    window_pnl_total=Sum('profit'),
                    window_positions=Count('id'),
                    window_TP=Count(Case(When(profit__gt=0, then=1))),
                    window_SL=Count(Case(When(profit__lt=0, then=1))),
                    window_pnl_average=Avg('profit'),
                )
            )

        # Append the window pnl data to the list
        # Store the combination information and pnl data in a dictionary
        combination_info = {
            'symbol': symbol,  # Change to the actual symbol value
            'type': 'SELL',  # Change to the actual type value
        }
        print(window_pnl)
        # Append the combination information and pnl data to the list
        # pnl_data.append({'combination': combination_info, 'pnl_data': window_pnl})

        # Move to the next time window
        current_date = end_date_window
        end_date_window = current_date + timedelta(days=time_lapse)

    # print(pnl_data)
    # # Iterate through pnl_data and print each combination and pnl statistics
    # for data in pnl_data:
    #     combination = data['combination']
    #     pnl_stats = data['pnl_data']
    #
    #     if pnl_stats:
    #         pnl_stats = pnl_stats[0]  # Assuming there's only one record per combination
    #
    #         print("Combination:", combination)
    #         print("PnL Statistics:")
    #         print("Total PnL:", pnl_stats['window_pnl_total'])
    #         print("Total Positions:", pnl_stats['window_positions'])
    #         print("Total TP:", pnl_stats['window_TP'])
    #         print("Total SL:", pnl_stats['window_SL'])
    #         print("Average PnL:", pnl_stats['window_pnl_average'])
    #         print("=" * 40)  # Separator line
    #     else:
    #         print("Combination:", combination)
    #         print("No data for this combination in the specified time window.")
    #         print("=" * 40)  # Separator line
    #
    # # # ... (rest of the code)
