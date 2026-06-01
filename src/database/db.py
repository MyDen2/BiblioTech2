import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

ENV_PATH = BASE_DIR / "config" / ".env"

load_dotenv(dotenv_path=ENV_PATH)


DB_HOST = os.getenv(
    "POSTGRES_PUBLIC_HOST",
    "localhost"
)

DB_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

DB_NAME = os.getenv(
    "POSTGRES_DB"
)

DB_USER = os.getenv(
    "POSTGRES_USER"
)

DB_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD"
)


def get_connection():

    if not all([
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
    ]):
        raise ValueError(
            "Missing PostgreSQL credentials"
        )

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )