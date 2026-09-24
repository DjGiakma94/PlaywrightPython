import os

import pytest
import psycopg
from psycopg import OperationalError
from psycopg.rows import dict_row


@pytest.fixture(scope="session")
def db_connection():
    database_url = os.getenv("DATABASE_POOLER_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        pytest.fail(
            "Set DATABASE_POOLER_URL or DATABASE_URL in the project .env file.",
            pytrace=False,
        )

    try:
        connection = psycopg.connect(database_url, row_factory=dict_row)
        connection.autocommit = True
    except OperationalError as error:
        pytest.fail(
            "Database connection failed. Prefer Supabase Session pooler "
            "connection string in DATABASE_POOLER_URL.",
            pytrace=False,
        )

    yield connection

    connection.close()