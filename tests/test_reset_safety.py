"""Regression checks: do not accidentally erase Neon/SQLite without verified restore."""
from app import app
from services.db import init_db, get_db


def test_reset_protects_original_rows_when_baseline_snapshot_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("AXEOM_FORCE_SQLITE", "1")
    monkeypatch.setenv("AXEOM_DB_PATH", str(tmp_path / "reset-safety.db"))
    init_db()
    conn = get_db()
    conn.execute(
        "INSERT INTO invoices (invoice_no,bill_to,issued,due,amount,status) "
        "VALUES (?,?,?,?,?,?)",
        ("INV-KEEP", "Real Client", "2026-09-01", "2026-09-15", 500, "unpaid")
    )
    conn.commit()
    conn.close()
    app.config["TESTING"] = True
    with app.test_client() as client:
        preview = client.get("/api/manage/reset/preview")
        assert preview.status_code == 200
        p = preview.get_json()["preview"]
        assert p["reset_available"] is False
        assert p["has_recoverable_backup"] is False
        assert p["table_counts"]["invoices"] == 1
        assert p["total_records"] == sum(p["table_counts"].values())
        assert p["total_records"] >= 1
        with client.session_transaction() as sess:
            sess["owner_authorized"] = True
        forbidden = client.post("/api/manage/reset", json={"phrase": "WRONG"})
        assert forbidden.status_code == 400
        blocked = client.post("/api/manage/reset", json={"phrase": "DELETE ALL BUSINESS DATA"})
        assert blocked.status_code == 409
        assert blocked.get_json()["status"] == "error"
        conn = get_db()
        assert conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 1
        conn.close()
