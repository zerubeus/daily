import time

import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings
from app.exceptions.custom_exceptions import DatabaseConnectionError


def get_db():
    retries = settings.RETRIES
    delay = settings.DELAY
    for _ in range(retries):
        try:
            conn = psycopg2.connect(
                dbname=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                cursor_factory=RealDictCursor,
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"Database connection failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise DatabaseConnectionError(
        "Failed to connect to the database after multiple attempts"
    )


def close_db_connection(conn):
    if conn:
        conn.close()
