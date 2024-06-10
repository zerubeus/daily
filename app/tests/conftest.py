import os

import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.db.connection import get_db
from app.db.init_db import create_tables
from app.main import app

os.environ["DB_NAME"] = "dailymotion_test"
os.environ["DB_USER"] = "user"
os.environ["DB_PASSWORD"] = "password"
os.environ["DB_HOST"] = "db_test"
os.environ["DB_PORT"] = "5432"
os.environ["REDIS_HOST"] = "redis"
os.environ["REDIS_PORT"] = "6379"


@pytest.fixture(scope="session")
def test_db():
    conn = get_db()
    create_tables()
    yield conn
    conn.close()


@pytest.fixture(scope="function", autouse=True)
def clean_db(test_db):
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM activation_codes; DELETE FROM users;")
    test_db.commit()
    cursor.close()
    yield
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM activation_codes; DELETE FROM users;")
    test_db.commit()
    cursor.close()


@pytest.fixture
def redis_client():
    client = Redis(
        host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=0
    )
    client.flushdb()
    yield client
    client.flushdb()


@pytest.fixture
def client():
    return TestClient(app)
