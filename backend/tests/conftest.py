import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

import backend.app.database.models
from backend.app.core.config import Settings
from backend.app.database.base import Base
from backend.app.database.session import get_db
from backend.app.main import app

# Fixture is a function that will be run before each test function to set up the test environment. 
# It can also be used to tear down the test environment after the test function has run. 
# Fixtures can be used to create a test database, create a test client, and override dependencies.

# Fixture for creating a test database engine
@pytest.fixture(scope="session")
def test_engine():
    test_settings = Settings(_env_file=".env.test")  # type: ignore

    database_url = test_settings.DATABASE_URL
    database_name = make_url(test_settings.DATABASE_URL).database

    if database_name != "private_ai_test":
        raise ValueError(
            f"Test database name must be 'private_ai_test', but got '{database_name}'"
        )

    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# Fixture for creating a database session for tests
@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# Fixture for creating a test client with dependency overrides
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()