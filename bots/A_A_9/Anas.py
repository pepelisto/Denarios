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
        i = 0
        while True:
            try:
                Anastasia(timeframe=240).traeder()
                time.sleep(60)
                break
            except Exception as e:
                # Send email notification
                if 'SSL SYSCALL error: EOF detected' in str(e):
                    time.sleep(150)
                    i += 1
                    print(f"Error: {e}")
                    if i == 10:
                        error_message = f"Error on Anastasia: {e}, se intento 10 veces reconectar pero error persiste"
                        send_email("Anastasia Error", error_message)
                        print(f"Error: {e}")
                        raise
                    elif i == 1:
                        error_message = f"Error on Anastasia: {e} primer intento de reconeccion, si no llegan el email de 10 falla es pq funciono"
                        send_email("Anastasia Error", error_message)
                else:
                    error_message = f"Error on Anastasia: {e}"
                    send_email("Anastasia Error", error_message)
                    print(f"Error: {e}")
                    raise


run_scheduled_pattern()
