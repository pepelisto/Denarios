from bots.notUsed.A_A_invertido.functions.Anastasia import Anastasia
import time
import datetime


def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        next_start_time = current_time + datetime.timedelta(seconds=120)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        time.sleep(remaining_time)
        Anastasia(timeframe=15).traeder()


# traeder()
run_scheduled_pattern()
