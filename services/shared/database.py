import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor


def create_database_connection():
    database_url = os.environ["DATABASE_URL"]
    retries = 10
    delay_seconds = 3
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        except psycopg2.OperationalError as exc:
            last_error = exc
            if attempt == retries:
                raise
            time.sleep(delay_seconds)

    raise last_error


def run_database_command(command, parameters=None, fetch_one=False, fetch_all=False):
    connection = create_database_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(command, parameters or ())
                if fetch_one:
                    return cursor.fetchone()
                if fetch_all:
                    return cursor.fetchall()
                return None
    finally:
        connection.close()
