from bots.A_A_9.functions.Agripina import Agripina
from bots.A_A_9.functions.email_not import send_email
import time
import datetime
from pytz import utc
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
        retries = 0
        max_retries = 10
        while True:
            try:
                print("Executing your task.")
                Agripina(timeframe=240).traeder()
                break
            except Exception as e:
                # Send email notification
                if 'SSL SYSCALL error: EOF detected' in str(e):
                    time.sleep(5)
                    retries += 1
                    print(f"Error: {e}")
                    if retries == max_retries:
                        error_message = f"Error on Agripina: {e}, se intento 10 veces reconectar pero error persiste"
                        send_email("Anastasia Error", error_message)
                        print(f"Error: {e}")
                        raise
                    elif retries == 1:
                        error_message = f"Error on Agripina: {e} primer intento de reconeccion, si no llegan el email de 10 falla es pq funciono"
                        send_email("Anastasia Error", error_message)
                    try:
                        reconnect_database()
                        error_message = f"funciono la reconeccion Agripina: 2256"
                        send_email("Agripina funciona la wea", error_message)
                    except OperationalError as op_err:
                        print(f"Database reconnection failed Agripina: {op_err}")
                        error_message = f"Error on Agripina: {e}, error en intento de reconeccion de database"
                        send_email("Agripina Error", error_message)
                        raise
                else:
                    error_message = f"Error on Agripina: {e}"
                    send_email("Agripina Error", error_message)
                    print(f"Error: {e}")
                    raise

run_scheduled_pattern()

