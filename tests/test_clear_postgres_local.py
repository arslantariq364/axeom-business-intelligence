import os
from urllib.parse import urlparse
import pytest

from services.db import get_database_url, get_db, is_dataset_cleared, seed_db_if_empty
from services.data_management import CLEARABLE_TABLES, get_reset_preview, execute_reset

pytestmark = pytest.mark.skipif(
    not os.getenv("AXEOM_POSTGRES_SMOKE"),
    reason="Requires local PostgreSQL container smoke test environment"
)


def test_local_postgres_clear_all(monkeypatch):
    host = urlparse(get_database_url() or "").hostname
    assert host in ("127.0.0.1", "localhost"), "Destructive CI tests only use local containers"
    monkeypatch.setenv("OWNER_PIN", "example-local-strong-password")
    monkeypatch.setenv("SECRET_KEY", "a-dedicated-local-example-secret-00000001")
    preview = get_reset_preview()
    assert preview["total_records"] > 0
    result = execute_reset(
        "DELETE ALL BUSINESS DATA",
        expected_total_records=preview["total_records"]
    )
    assert result["status"] == "success", result
    assert result["deleted_records"] == preview["total_records"]
    seed_db_if_empty()
    assert is_dataset_cleared()
    conn = get_db()
    try:
        for table in CLEARABLE_TABLES:
            assert conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0] == 0
    finally:
        conn.close()
