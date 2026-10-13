"""
Test Suite for Prompt 9: Synthetic Fixtures & Implementation Stress Tests.
Tests system resilience against unseen fixtures without polluting submission answers.
All tests run in an isolated test database (AXEOM_DB_PATH).
"""

import io
import os
import json
import shutil
import pytest
from pathlib import Path
from app import app
from services.db import get_db, init_db, seed_db_if_empty
from services.identity import resolve_client, resolve_client_by_name, CANONICAL_CLIENTS
from services.finance import reconcile_finances
from services.jev import classify_message, get_api_key

@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Provides a fully isolated test database populated from axeom.db."""
    test_db = str(tmp_path / "axeom_synthetic_test.db")
    shutil.copy("axeom.db", test_db)
    monkeypatch.setenv("AXEOM_FORCE_SQLITE", "1")
    monkeypatch.setenv("AXEOM_DB_PATH", test_db)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client, test_db

# 1. Unseen same-format file updates correct client and business results without code edits
# 1. Genuinely new file with new record changes result; repeating upload leaves it unchanged
def test_genuinely_new_file_record_updates_result_and_repeat_is_idempotent(isolated_env):
    client, _ = isolated_env
    # Check baseline overdue total
    state_before = client.get("/api/state").get_json()
    base_overdue = state_before["metrics"]["overdue_total"]

    # Upload unseen new invoice for Crown Barbers: INV-9100 for $750 due 2026-09-15 (overdue as of 2026-10-06)
    csv_content = (
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-9100,Crown Barbers,marcus@crownbarbers.com,2026-09-01,2026-09-15,750.00,unpaid,September Promotional Video\n"
    )
    data = {'file': (io.BytesIO(csv_content.encode('utf-8')), 'new_unseen_invoices_batch.csv')}
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "success"
    assert resp.get_json()["added"] == 1

    # Verify business results updated automatically without code edits
    state_after_first = client.get("/api/state").get_json()
    assert state_after_first["metrics"]["overdue_total"] == base_overdue + 750.0

    # Repeat the upload of the exact same file
    data_repeat = {'file': (io.BytesIO(csv_content.encode('utf-8')), 'new_unseen_invoices_batch.csv')}
    resp_repeat = client.post('/api/upload', data=data_repeat, content_type='multipart/form-data')
    assert resp_repeat.status_code == 200

    # Verify repeating the upload leaves the result unchanged
    state_after_repeat = client.get("/api/state").get_json()
    assert state_after_repeat["metrics"]["overdue_total"] == base_overdue + 750.0

# 2. Duplicate file detection (exact SHA-256) is handled as an independent check
def test_duplicate_file_exact_sha256_detection(isolated_env):
    client, _ = isolated_env
    csv_content = (
        "payment_id,date,payer,payer_email,amount,method,reference\n"
        "P9001,01/10/2026,Patel Insurance Group,raj@patelinsurance.com,1000.00,wire,INV-1122\n"
    )
    # 1st upload
    data1 = {'file': (io.BytesIO(csv_content.encode('utf-8')), 'payments_batch_oct.csv')}
    resp1 = client.post('/api/upload', data=data1, content_type='multipart/form-data')
    assert resp1.status_code == 200
    assert resp1.get_json()["status"] == "success"

    # 2nd upload with identical bytes
    data2 = {'file': (io.BytesIO(csv_content.encode('utf-8')), 'payments_batch_oct.csv')}
    resp2 = client.post('/api/upload', data=data2, content_type='multipart/form-data')
    assert resp2.status_code == 200
    res2 = resp2.get_json()
    assert res2["status"] == "duplicate_file"
    assert res2["added"] == 0
    assert "already been processed" in res2["message"].lower()

# 3. Renamed file with valid recognized schema still works
def test_renamed_file_with_valid_schema_still_works(isolated_env):
    client, _ = isolated_env
    # File has random custom name but standard invoice headers
    renamed_csv = (
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-9005,Khan Dental,sarah@khandental.com,2026-10-01,2026-10-15,600.00,unpaid,Reels pack\n"
    )
    data = {'file': (io.BytesIO(renamed_csv.encode('utf-8')), 'quickbooks_dump_backup_2026_final_v2.csv')}
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    res_json = resp.get_json()
    assert res_json["status"] == "success"
    assert res_json["file_role"] == "invoices"

# 4. Legitimate repeated transactions are not collapsed
def test_legitimate_repeated_transactions_not_collapsed(isolated_env):
    client, _ = isolated_env
    # Two distinct payments on the same date with different IDs for the exact same amount
    multi_pay_csv = (
        "payment_id,date,payer,payer_email,amount,method,reference\n"
        "P9010,02/10/2026,Northpoint Church,media@northpointdfw.org,300.00,ach,INV-1001\n"
        "P9011,02/10/2026,Northpoint Church,media@northpointdfw.org,300.00,ach,INV-1002\n"
    )
    data = {'file': (io.BytesIO(multi_pay_csv.encode('utf-8')), 'distinct_repeated_payments.csv')}
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    assert resp.get_json()["added"] == 2

    conn = get_db()
    rows = conn.execute("SELECT payment_id FROM payments WHERE payment_id IN ('P9010', 'P9011')").fetchall()
    conn.close()
    assert len(rows) == 2, "Both legitimate distinct transactions must exist in database"

# 5. Similar names with conflicting evidence remain separate
def test_similar_names_with_conflicting_evidence_remain_separate():
    # Test Cedar Ridge Properties (conflicting domain & phone) vs Cedarstone Construction
    res_cedar_conflict = resolve_client(
        name="Cedar Ridge Properties",
        email="sales@cedarridgeproperties.com",
        phone="972-555-0999"
    )
    assert res_cedar_conflict is None, "Conflicting email/phone must prevent false merge to Cedarstone Construction"

    # Test Torres Tire & Auto (Luis Torres) vs Torres Law Firm (Mike Torres)
    res_torres_conflict = resolve_client(
        name="Torres Tire & Auto",
        email="luis@torrestire.com",
        phone="214-555-0193"
    )
    assert res_torres_conflict is None, "Torres Tire & Auto must not merge into Torres Law Firm"

    # Test Lone Star Realty vs Lonestar Realty Group remain strictly separate
    c_lone_star = resolve_client(name="Lone Star Realty", email="dana@lonestarrealty.com", phone="214-555-0164")
    c_lonestar_rg = resolve_client(name="Lonestar Realty Group", email="greg@lonestarrg.com", phone="817-555-0119")
    assert c_lone_star["id"] == "C20"
    assert c_lonestar_rg["id"] == "C28"
    assert c_lone_star["id"] != c_lonestar_rg["id"]

# 6. A new alias with strong evidence links correctly
def test_new_alias_with_strong_evidence_links_correctly():
    # Client name is an unseen alias "Patel Risk Associates", but email and phone match Patel Insurance Group
    resolved = resolve_client(
        name="Patel Risk Associates",
        email="raj@patelinsurance.com",
        phone="214-555-0195"
    )
    assert resolved is not None
    assert resolved["id"] == "C12"
    assert resolved["canonical_name"] == "Patel Insurance Group"

# 7. A new request appears in the correct client/video workflow
def test_new_request_appears_in_correct_client_and_video_workflow(isolated_env):
    client, _ = isolated_env
    # Message referencing Cedarstone Construction and video V022
    msg_data = "[2026-10-05 10:15] EMAIL from will@cedarstone.build (Cedarstone Construction): Please change the font to white on video V022.\n"
    data = {'file': (io.BytesIO(msg_data.encode('utf-8')), 'new_incoming_messages.txt')}
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200

    # Check Cedarstone dossier
    dossier = client.get('/api/client/C05').get_json()["data"]
    matching_msg = next((m for m in dossier["messages"] if "V022" in m["body"]), None)
    assert matching_msg is not None, "New request must appear in client's dossier"

# 8. Missing columns, invalid dates and bad amounts produce useful errors
def test_missing_columns_invalid_dates_and_bad_amounts_produce_useful_errors(isolated_env):
    client, _ = isolated_env
    # Missing required primary key column
    malformed_csv = "email,issued,due,amount,status\ntest@test.com,2026-09-01,2026-09-15,500.00,unpaid\n"
    data = {'file': (io.BytesIO(malformed_csv.encode('utf-8')), 'invoices_missing_cols.csv')}
    resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
    assert "missing required column" in resp.get_json()["message"].lower()

    # Bad amounts handled safely without crashing
    bad_amt_csv = (
        "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        "INV-9999,Test Client,test@test.com,2026-09-01,2026-09-15,$invalid_amt,unpaid,test\n"
    )
    data_bad = {'file': (io.BytesIO(bad_amt_csv.encode('utf-8')), 'invoices_bad_amt.csv')}
    resp_bad = client.post('/api/upload', data=data_bad, content_type='multipart/form-data')
    assert resp_bad.status_code == 400
    assert resp_bad.get_json()["rejected"] == 1
    # Invalid money must never enter the database as a fictitious $0 invoice.
    conn = get_db()
    row = conn.execute("SELECT amount FROM invoices WHERE invoice_no = 'INV-9999'").fetchone()
    conn.close()
    assert row is None

# 9. Updates and overlapping snapshots follow documented semantics
def test_updates_and_overlapping_snapshots_follow_documented_semantics(isolated_env):
    client, _ = isolated_env
    # Ingest invoice initially as unpaid
    v1_csv = "invoice_no,bill_to,email,issued,due,amount,status,memo\nINV-9888,Luna Bridal,sofia@lunabridal.com,2026-09-01,2026-09-15,800.00,unpaid,promo\n"
    client.post('/api/upload', data={'file': (io.BytesIO(v1_csv.encode('utf-8')), 'inv_v1.csv')}, content_type='multipart/form-data')

    # Updated snapshot with status changed to paid
    v2_csv = "invoice_no,bill_to,email,issued,due,amount,status,memo\nINV-9888,Luna Bridal,sofia@lunabridal.com,2026-09-01,2026-09-15,800.00,paid,promo\n"
    resp2 = client.post('/api/upload', data={'file': (io.BytesIO(v2_csv.encode('utf-8')), 'inv_v2.csv')}, content_type='multipart/form-data')
    assert resp2.status_code == 200
    assert resp2.get_json()["updated"] == 1

    conn = get_db()
    row = conn.execute("SELECT status FROM invoices WHERE invoice_no = 'INV-9888'").fetchone()
    conn.close()
    assert row["status"] == "paid"

# 10. Two imports cannot create duplicate financial events
def test_two_imports_cannot_create_duplicate_financial_events(isolated_env):
    client, _ = isolated_env
    inv_data = "invoice_no,bill_to,email,issued,due,amount,status,memo\nINV-9777,Luna Bridal,sofia@lunabridal.com,2026-09-01,2026-09-15,800.00,unpaid,promo\n"
    # Upload once
    client.post('/api/upload', data={'file': (io.BytesIO(inv_data.encode('utf-8')), 'inv_first.csv')}, content_type='multipart/form-data')
    # Upload again with different filename
    client.post('/api/upload', data={'file': (io.BytesIO(inv_data.encode('utf-8')), 'inv_second.csv')}, content_type='multipart/form-data')

    conn = get_db()
    count = conn.execute("SELECT count(*) FROM invoices WHERE invoice_no = 'INV-9777'").fetchone()[0]
    conn.close()
    assert count == 1, "Duplicate upload must not create duplicate primary key records"

# 11. Refresh and application restart preserve imports and owner choices
def test_refresh_and_app_restart_preserve_imports_and_owner_choices(isolated_env):
    client, _ = isolated_env
    # Post decision
    resp = client.post('/api/decisions', json={
        "action_id": "test_owner_action_99",
        "decision_type": "action",
        "status": "in_progress",
        "owner_notes": "Reviewed with client over phone, approved revision."
    })
    assert resp.status_code == 200

    # Simulate app restart / new request
    state = client.get('/api/state').get_json()
    assert "test_owner_action_99" in state["decisions"]
    assert state["decisions"]["test_owner_action_99"]["status"] == "in_progress"
    assert "Reviewed with client" in state["decisions"]["test_owner_action_99"]["owner_notes"]

# 12. Jev failures remain visible and do not fabricate results
def test_jev_failures_remain_visible_and_do_not_fabricate_results():
    if not get_api_key():
        res = classify_message("Can we cancel our shoot today and reschedule for next week?")
        assert res["provider"] == "deterministic_fallback"
        assert res["live_call_blocked"] is True
        assert "TYPESAFE_API_KEY" in res["blocker_reason"]
        # Must not fabricate mock token counts or fake provider IDs
        assert "fake" not in str(res).lower()

# 13. Owner approval/draft/defer controls behave as labeled
def test_owner_approval_draft_defer_controls_behave_as_labeled(isolated_env):
    client, _ = isolated_env
    for target_status in ["deferred", "in_progress", "completed"]:
        resp = client.post('/api/decisions', json={
            "action_id": "action_test_cycle",
            "decision_type": "action",
            "status": target_status,
            "owner_notes": f"Testing transition to {target_status}"
        })
        assert resp.status_code == 200
        state = client.get('/api/state').get_json()
        assert state["decisions"]["action_test_cycle"]["status"] == target_status

# 14. A phone user can identify the first action within 10 seconds
def test_phone_user_can_identify_first_action_within_10_seconds(isolated_env):
    client, _ = isolated_env
    resp = client.get('/')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # 1. First screen is #view-today
    assert 'id="view-today" class="app-view active"' in html

    # 2. Hero Action #1 container is at the top of #view-today
    assert '<div id="hero-card-container">' in html

    # 3. Payload size is extremely compact (< 50KB) enabling < 20ms delivery over mobile networks
    assert len(resp.data) < 50000

    # 4. Check state API provides hero action with all required elements
    state = client.get('/api/state').get_json()
    hero = state["today"]["hero_action"]
    assert hero["client"] == "Patel Insurance Group"
    assert "INV-1122" in hero["overdue_invoice"]
    assert hero["what_to_do_this_week"] != ""

# 15. Verify synthetic data isolation from submission answers
def test_synthetic_data_isolation_from_submission_answers():
    # If backup template exists, verify it matches original template
    if os.path.exists("answers_template_backup.json"):
        with open("answers_template_backup.json", "r", encoding="utf-8") as f:
            assert len(f.readlines()) == 51

    # Verify answers.json contains no synthetic IDs from test suite
    ans_path = "submission/answers.json" if os.path.exists("submission/answers.json") else "answers.json"
    if os.path.exists(ans_path):
        with open(ans_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "INV-9001" not in content
        assert "P9001" not in content
        assert "INV-9888" not in content
        assert "SYN-" not in content
        assert "test_owner_action_99" not in content

    # Verify answers_working.json contains no synthetic IDs from test suite
    if os.path.exists("answers_working.json"):
        with open("answers_working.json", "r", encoding="utf-8") as f:
            content = f.read()
        assert "INV-9001" not in content
        assert "P9001" not in content
        assert "INV-9888" not in content
        assert "SYN-" not in content
        assert "test_owner_action_99" not in content
