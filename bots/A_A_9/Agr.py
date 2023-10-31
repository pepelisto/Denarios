from bots.A_A.functions.Agripina import Agripina
import time
import datetime
from pytz import utc


def run_scheduled_pattern():
    while True:
        current_time_utc = datetime.datetime.utcnow().replace(tzinfo=utc)
        current_hour_utc = current_time_utc.hour

        # Calculate the next execution time based on the specific UTC times
        if current_hour_utc < 0:
            next_start_time_utc = current_time_utc.replace(hour=0, minute=0, second=30, microsecond=0)
        elif current_hour_utc < 4:
            next_start_time_utc = current_time_utc.replace(hour=4, minute=0, second=30, microsecond=0)
        elif current_hour_utc < 8:
            next_start_time_utc = current_time_utc.replace(hour=8, minute=0, second=30, microsecond=0)
        elif current_hour_utc < 12:
            next_start_time_utc = current_time_utc.replace(hour=12, minute=0, second=30, microsecond=0)
        elif current_hour_utc < 16:
            next_start_time_utc = current_time_utc.replace(hour=16, minute=0, second=30, microsecond=0)
        elif current_hour_utc < 20:
            next_start_time_utc = current_time_utc.replace(hour=20, minute=0, second=30, microsecond=0)
        else:
            # If it's already past 20 UTC, set the next start time for the next day at 0 UTC
            next_start_time_utc = (current_time_utc + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=30, microsecond=0)

        remaining_time = (next_start_time_utc - current_time_utc).total_seconds()
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time_utc}")
        time.sleep(remaining_time)
        Agripina(timeframe=240).traeder()
        print("Executing your task.")

run_scheduled_pattern()

