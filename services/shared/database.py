import os

import psycopg2
from psycopg2.extras import RealDictCursor


def create_database_connection():
    database_url = os.environ["DATABASE_URL"]
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


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
