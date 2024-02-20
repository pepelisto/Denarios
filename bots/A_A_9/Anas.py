from bots.A_A_9.functions.Anastasia import Anastasia
import time
import datetime
from bots.A_A_9.functions.email_not import send_email
from django.db import connections
from psycopg2 import OperationalError

def reconnect_database():
    default_db = connections['default']
    try:
       default_db.close()
    except Exception as e:
        print(f"Exception while closing the database connection: {e}")
    default_db.connect()

def run_scheduled_pattern():
    while True:
        current_time = datetime.datetime.now()
        minutes_to_next_interval = (5 - current_time.minute % 5) % 5
        next_start_time = current_time.replace(second=1) + datetime.timedelta(minutes=minutes_to_next_interval)
        remaining_time = (next_start_time - current_time).total_seconds()
        remaining_time = max(0, remaining_time)
        print(f"Waiting for {remaining_time / 60} minutes until {next_start_time}")
        time.sleep(remaining_time)
        retries = 0
        max_retries = 10
        while True:
            try:
                Anastasia(timeframe=240).traeder()
                time.sleep(60)
                break
            except Exception as e:
                # Send email notification
                if ('SSL SYSCALL error: EOF detected' or 'connection already closed') in str(e):
                    time.sleep(20)
                    retries += 1
                    print(f"Error: {e}")
                    if retries == max_retries:
                        error_message = f"Error on Anastasia: {e}, se intento 10 veces reconectar pero error persiste"
                        send_email("Anastasia Error", error_message)
                        print(f"Error: {e}")
                        raise
                    elif retries == 1:
                        error_message = f"Error on Anastasia: {e}, falla, se intentara la primera reconeccion "
                        send_email("Anastasia Error", error_message)
                        print(f"Error: {e}")
                    try:
                        reconnect_database()
                    except OperationalError as op_err:
                        print(f"Database reconnection failed Anastasia: {op_err}")
                        error_message = f"Error on Anastasia: {e}, error en intento de reconeccion de database"
                        send_email("Anastasia Error", error_message)
                        raise
                else:
                    error_message = f"Error on Anastasia (563) process killed: {e}"
                    send_email("Anastasia Error no identificado", error_message)
                    print(f"Error: {e}")
                    raise


run_scheduled_pattern()
