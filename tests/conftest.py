import pytest
from app.db.init_db import init_db


@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
    """Initializes the database schema and seeds initial data before running any tests."""
    init_db()
