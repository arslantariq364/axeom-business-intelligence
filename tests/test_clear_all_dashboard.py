"""Destructive clear-all regression tests. NEVER run against any real database."""
import io
import os
import pytest
from app import app
from services.db import init_db, get_db, seed_db_if_empty, is_dataset_cleared
from services.data_management import CLEARABLE_TABLES, execute_reset


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("AXEOM_FORCE_SQLITE", "1")
    monkeypatch.setenv("AXEOM_DB_PATH", str(tmp_path / "isolated-clear-test.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("OWNER_PIN", "unit-test-owner-pin-secure")
    monkeypatch.setenv("SECRET_KEY", "unit-test-long-secret-for-clear-dashboard-2026")
    monkeypatch.setattr("services.auth.OWNER_PIN", "unit-test-owner-pin-secure")
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as client:
        yield client


def upload(client, filename, data):
    return client.post("/api/upload", data={
        "file": (io.BytesIO(data.encode()), filename)
    }, content_type="multipart/form-data")


def test_clear_all_requires_auth_and_correct_phrase_and_fresh_preview(api):
    assert upload(api, "newinvoice.csv",
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-9001,Alpha Studio,alpha@example.com,2026-09-01,2026-09-15,125,unpaid,test\n").status_code == 200
    preview = api.get("/api/manage/reset/preview").json["preview"]
    assert preview["reset_available"] is True
    assert preview["total_records"] > 0
    payload = {"confirmation_phrase": "DELETE ALL BUSINESS DATA",
               "expected_total_records": preview["total_records"]}
    assert api.post("/api/manage/reset", json=payload).status_code == 403

    auth = {"X-Owner-Auth": "unit-test-owner-pin-secure"}
    assert api.post("/api/manage/reset", json={**payload, "confirmation_phrase": "RESET AXEOM DATA"},
                    headers=auth).status_code == 400
    assert api.post("/api/manage/reset", json={**payload, "expected_total_records": preview["total_records"]-1},
                    headers=auth).status_code == 409
    assert api.get("/api/state").json["metrics"]["client_count"] == 1
    assert api.get("/api/state").json["metrics"]["overdue_total"] == 125


def test_clear_all_removes_every_business_row_and_persists_across_restarts(api):
    inv = ("invoice_no,bill_to,email,issued,due,amount,status,memo\n"
           "INV-9002,Acme Media,acme@example.com,2026-09-01,2026-09-15,125,unpaid,shoot\n")
    lead = ("lead_id,created,name,business,email,phone,source,first_reply,status\n"
            "L9001,2026-09-15,Amber,Acme Media,amber@example.com,,Referral,,New\n")
    board = ("video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\n"
             "V9001,Acme Media,Promo,Amy,In Progress,,0,1.0,,\n")
    msg = "[2026-09-20 10:15] EMAIL from amber@example.com: Please change logo on V9001.\n"
    assert upload(api, "newinvoice.csv", inv).status_code == 200
    assert upload(api, "newlead.csv", lead).status_code == 200
    assert upload(api, "newboard.csv", board).status_code == 200
    assert upload(api, "messages_new.txt", msg).status_code == 200
    assert api.get("/api/state").json["metrics"]["client_count"] == 1
    assert api.get("/api/state").json["metrics"]["lost_requests_count"] == 1

    # Exercise classifications and owner choice without leaking to real Neon.
    assert api.post("/api/decisions", json={
        "action_id": "act-new", "status": "in_progress", "owner_notes": "Test"
    }).status_code == 200

    preflight = api.get("/api/manage/reset/preview").json["preview"]
    assert preflight["total_records"] > 0
    res = api.post("/api/manage/reset", headers={"X-Owner-Auth": "unit-test-owner-pin-secure"},
                   json={"confirmation_phrase": "DELETE ALL BUSINESS DATA",
                         "expected_total_records": preflight["total_records"]})
    assert res.status_code == 200, res.json
    assert res.json["cleared"] is True
    assert res.json["deleted_records"] == preflight["total_records"]
    assert all(v == 0 for v in res.json["table_counts_after"].values())

    conn = get_db()
    for table in CLEARABLE_TABLES:
        assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0, table
    conn.close()
    assert is_dataset_cleared() is True

    # Simulate the ordinary non-Vercel startup path: it MUST NOT reseed Pack 01.
    seed_db_if_empty()
    init_db(force=True)
    seed_db_if_empty()
    state = api.get("/api/state")
    assert state.status_code == 200, state.data
    data = state.json
    assert data["workspace_cleared"] is True
    assert data["metrics"]["client_count"] == 0
    assert data["metrics"]["total_leads_count"] == 0
    assert data["metrics"]["lost_requests_count"] == 0
    assert data["metrics"]["overdue_total"] == 0
    assert data["metrics"]["we_owe_total"] == 0
    assert data["metrics"]["never_billed_total"] == 0
    assert data["clients"] == []
    assert data["third_party_payers"] == []
    assert data["money"]["overdue"] == []
    assert data["requests"]["lost_requests"] == []
    assert data["evidence_register"] == []
    assert data["today"]["monday_top_3"] == []
    assert data["today"]["hero_action"]["client"] == ""
    assert data["decisions"] == {}
    exported = api.get("/api/export-answers").json
    assert exported["client_count"] == 0
    assert exported["clients"] == []
    assert exported["payers_who_are_not_clients"] == []
    assert exported["lost_requests"] == []
    report = api.get("/api/reports/business-report").json
    assert report["executive_summary"]["active_clients_count"] == 0
    assert report["1_active_clients"] == []
    assert report["10_recommended_next_actions"] == []

    # Upload again after clearing: start from 1 client, not 29 originals.
    assert upload(api, "freshinvoice.csv", inv.replace("INV-9002", "INV-9003")).status_code == 200
    state = api.get("/api/state").json
    assert state["metrics"]["client_count"] == 1
    assert state["clients"][0]["canonical_name"] == "Acme Media"
    assert state["metrics"]["overdue_total"] == 125
    assert state["metrics"]["we_owe_total"] == 0
    assert len(state["requests"]["lost_requests"]) == 0


def test_reset_remains_disabled_without_secure_environment(api, monkeypatch):
    monkeypatch.delenv("OWNER_PIN", raising=False)
    assert api.get("/api/manage/reset/preview").json["preview"]["reset_available"] is False
    with app.test_client() as client:
        result = client.post("/api/manage/reset", headers={"X-Owner-Auth": "unit-test-owner-pin-secure"},
                             json={"confirmation_phrase": "DELETE ALL BUSINESS DATA", "expected_total_records": 0})
        assert result.status_code == 409
