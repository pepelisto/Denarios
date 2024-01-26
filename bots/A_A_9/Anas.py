from bots.A_A_9.functions.Anastasia import Anastasia
import time
import datetime
from bots.A_A_9.functions.email_not import send_email

def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        minutes_to_next_interval = (5 - current_time.minute % 5) % 5
        next_start_time = current_time.replace(second=1) + datetime.timedelta(minutes=minutes_to_next_interval)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time}")
        time.sleep(remaining_time)
        while True:
            try:
                Anastasia(timeframe=240).traeder()
                time.sleep(60)
                break
            except Exception as e:
                # Send email notification
                error_message = f"Error on Anastasia: {e}"
                send_email("Anastasia Error", error_message)
                print(f"Error: {e}")
                raise


run_scheduled_pattern()
