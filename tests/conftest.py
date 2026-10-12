import sys
from pathlib import Path
import pytest

# Add project root to sys.path first
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
from services.db import init_db, seed_db_if_empty

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    init_db()
    seed_db_if_empty()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
