from bots.notUsed.A_A.functions.Agripina import Agripina
import time
import datetime


def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        next_start_time = current_time.replace(minute=00, second=30, microsecond=0) + datetime.timedelta(hours=1)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time}")
        time.sleep(remaining_time)
        Agripina(timeframe=60).traeder()
        print("Executing your task.")

run_scheduled_pattern()

