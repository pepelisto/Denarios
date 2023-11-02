from bots.A_A.functions.Anastasia import Anastasia
import time
import datetime

def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        minutes_to_next_interval = (5 - current_time.minute % 5) % 5
        next_start_time = current_time.replace(second=1) + datetime.timedelta(minutes=minutes_to_next_interval)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time}")
        time.sleep(remaining_time)
        Anastasia(timeframe=240).traeder()
        time.sleep(60)


run_scheduled_pattern()
