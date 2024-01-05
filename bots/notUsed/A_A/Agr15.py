from bots.notUsed.A_A.functions.Agripina import Agripina
import time
import datetime


def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        minutes_to_next_interval = (15 - current_time.minute % 15) % 15
        next_start_time = current_time + datetime.timedelta(minutes=minutes_to_next_interval)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time}")
        time.sleep(remaining_time)
        Agripina(timeframe=15).traeder()
        time.sleep(60)

run_scheduled_pattern()

