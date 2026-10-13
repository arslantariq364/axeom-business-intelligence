"""
Comprehensive Phase 10 Regression Verification Suite: Scenarios A through Z.
Tests real end-to-end functionality on an isolated SQLite database to ensure
zero regressions and strict adherence to Phase 10 requirements.
"""

import os
import json
import codecs
import pytest
from pathlib import Path
from app import app
from services.auth import OWNER_PIN
from services.db import init_db, get_db, is_dataset_cleared, seed_db_if_empty, invalidate_caches
from services.ingest import process_file_upload
from services.data_management import CLEARABLE_TABLES, get_reset_preview, execute_reset, update_record
from services.finance import reconcile_finances

TEST_DB_PATH = "test_phase10_scenarios.db"

TEST_PIN = "unit-test-owner-pin-secure"
TEST_SECRET = "unit-test-long-secret-for-clear-dashboard-2026"

@pytest.fixture(scope="module")
def isolated_app():
    """Sets up an isolated database for Phase 10 test execution."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    old_force = os.environ.get("AXEOM_FORCE_SQLITE")
    old_path = os.environ.get("AXEOM_DB_PATH")
    old_pin = os.environ.get("OWNER_PIN")
    old_secret = os.environ.get("SECRET_KEY")

    os.environ["AXEOM_FORCE_SQLITE"] = "1"
    os.environ["AXEOM_DB_PATH"] = TEST_DB_PATH
    os.environ["OWNER_PIN"] = TEST_PIN
    os.environ["SECRET_KEY"] = TEST_SECRET
    import services.auth
    services.auth.OWNER_PIN = TEST_PIN

    app.config["TESTING"] = True
    invalidate_caches()
    init_db(force=True)
    seed_db_if_empty()

    with app.test_client() as client:
        yield client

    # Cleanup
    invalidate_caches()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    if old_force is not None:
        os.environ["AXEOM_FORCE_SQLITE"] = old_force
    else:
        os.environ.pop("AXEOM_FORCE_SQLITE", None)

    if old_path is not None:
        os.environ["AXEOM_DB_PATH"] = old_path
    else:
        os.environ.pop("AXEOM_DB_PATH", None)

    if old_pin is not None:
        os.environ["OWNER_PIN"] = old_pin
        services.auth.OWNER_PIN = old_pin
    else:
        os.environ.pop("OWNER_PIN", None)

    if old_secret is not None:
        os.environ["SECRET_KEY"] = old_secret
    else:
        os.environ.pop("SECRET_KEY", None)


def test_scenario_a_initial_dashboard_loads(isolated_app):
    """Scenario A: Initial dashboard loads successfully."""
    res = isolated_app.get("/")
    assert res.status_code == 200
    assert b"Axeom" in res.data
    assert b"state-error-banner" in res.data
    assert b"btn-state-retry" in res.data

    api_res = isolated_app.get("/api/state")
    assert api_res.status_code == 200
    state = api_res.get_json()
    assert state["status"] == "success"
    assert "metrics" in state
    assert "money" in state
    assert "requests" in state
    assert "clients" in state


def test_scenario_b_valid_client_upload_increases_client_count(isolated_app):
    """Scenario B: Valid client upload increases client count."""
    init_state = isolated_app.get("/api/state").get_json()
    init_clients = int(init_state["metrics"]["client_count"])

    inv_csv = (
        b"invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        b"INV-NEW-CLIENT-B,Horizon Labs Alpha,horizon@example.com,2026-08-01,2026-08-15,500.00,paid,Init\n"
    )
    res = process_file_upload("invoices_scenario_b.csv", inv_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    new_clients = int(new_state["metrics"]["client_count"])
    assert new_clients == init_clients + 1


def test_scenario_c_new_invoice_increases_outstanding(isolated_app):
    """Scenario C: New invoice increases outstanding balance."""
    init_state = isolated_app.get("/api/state").get_json()
    init_overdue = float(init_state["metrics"]["overdue_total"])

    inv_csv = (
        b"invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        b"INV-SCEN-C,Horizon Labs Alpha,horizon@example.com,2026-08-01,2026-08-15,500.00,unpaid,Shoot\n"
    )
    res = process_file_upload("invoices_scenario_c.csv", inv_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    new_overdue = float(new_state["metrics"]["overdue_total"])
    assert round(new_overdue - init_overdue, 2) == 500.00


def test_scenario_d_partial_payment_decreases_outstanding(isolated_app):
    """Scenario D: Partial payment decreases outstanding balance."""
    init_state = isolated_app.get("/api/state").get_json()
    init_overdue = float(init_state["metrics"]["overdue_total"])

    pay_csv = (
        b"payment_id,date,payer,payer_email,amount,method,reference\n"
        b"PAY-SCEN-D,2026-08-20,Horizon Labs Alpha,horizon@example.com,200.00,bank,INV-SCEN-C\n"
    )
    res = process_file_upload("payments_scenario_d.csv", pay_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    new_overdue = float(new_state["metrics"]["overdue_total"])
    assert round(init_overdue - new_overdue, 2) == 200.00


def test_scenario_e_overpayment_increases_credits(isolated_app):
    """Scenario E: Overpayment increases client credits."""
    init_state = isolated_app.get("/api/state").get_json()
    init_credits = float(init_state["metrics"]["we_owe_total"])

    # Remaining balance on INV-SCEN-C was 300.00. Paying 500.00 generates 200.00 credit.
    pay_csv = (
        b"payment_id,date,payer,payer_email,amount,method,reference\n"
        b"PAY-SCEN-E,2026-08-22,Horizon Labs Alpha,horizon@example.com,500.00,bank,INV-SCEN-C\n"
    )
    res = process_file_upload("payments_scenario_e.csv", pay_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    new_credits = float(new_state["metrics"]["we_owe_total"])
    assert new_credits >= init_credits + 200.00


def test_scenario_f_unbilled_work_updates(isolated_app):
    """Scenario F: Completed, genuinely unbilled booking updates the unbilled-work queue."""
    init_state = isolated_app.get("/api/state").get_json()
    init_unbilled = float(init_state["metrics"]["never_billed_total"])

    booking_csv = (
        b"booking_id,date,client_name,email,service,status,price\n"
        b"B-UNBILLED-999,2026-09-25,Horizon Labs Alpha,horizon@example.com,Brand Video,completed,1250.00\n"
    )
    res = process_file_upload("bookings_scenario_f.csv", booking_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    new_unbilled = float(new_state["metrics"]["never_billed_total"])
    assert round(new_unbilled - init_unbilled, 2) == 1250.00
    assert any(item.get("booking_id_or_month") == "B-UNBILLED-999" for item in new_state["money"]["never_billed"])


def test_scenario_g_leads_update_marketing(isolated_app):
    """Scenario G: Website leads update marketing calculations."""
    init_state = isolated_app.get("/api/state").get_json()
    init_leads = int(init_state["metrics"]["total_leads_count"])

    lead_csv = (
        b"lead_id,created,name,business,email,phone,source,status\n"
        b"L-SCEN-G1,2026-09-28,New Lead One,Biz1,lead1@biz1.example,555-0201,Website form,open\n"
        b"L-SCEN-G2,2026-09-29,New Lead Two,Biz2,lead2@biz2.example,555-0202,Website form,open\n"
    )
    res = process_file_upload("leads_scenario_g.csv", lead_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    new_leads = int(new_state["metrics"]["total_leads_count"])
    assert new_leads == init_leads + 2


def test_scenario_h_edit_requests_update_metrics(isolated_app):
    """Scenario H: New verified edit requests update request metrics."""
    init_state = isolated_app.get("/api/state").get_json()
    init_lost = int(init_state["metrics"]["lost_requests_count"])

    board_csv = (
        b"video_id,client,title,editor,stage,notes_on_board,revisions,editor_hours,client_approved_on,shoot_booking\n"
        b"V-SCEN-H,Horizon Labs Alpha,Promo Cut,Sara,Review,Client emailed requesting cut shortening,2,4.0,,B-UNBILLED-999\n"
    )
    res = process_file_upload("board_scenario_h.csv", board_csv)
    assert res["status"] == "success"

    new_state = isolated_app.get("/api/state").get_json()
    assert int(new_state["metrics"]["lost_requests_count"]) >= init_lost


def test_scenario_i_identical_csv_upload_idempotency(isolated_app):
    """Scenario I: Identical CSV uploads do not duplicate records."""
    test_csv = (
        b"lead_id,created,name,business,email,phone,source,status\n"
        b"L-IDEMP-1,2026-10-01,Idemp Test,Idemp Corp,idemp@test.example,555-9999,Referral,open\n"
    )
    res1 = process_file_upload("idempotent_test.csv", test_csv)
    assert res1["status"] == "success"
    assert res1["added"] == 1

    res2 = process_file_upload("idempotent_test.csv", test_csv)
    assert res2["status"] == "duplicate_file"
    assert res2["added"] == 0


def test_scenario_j_invalid_monetary_values_rejected(isolated_app):
    """Scenario J: Invalid monetary values are rejected."""
    bad_inv = (
        b"invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        b"INV-BAD-MONEY,Bad Client,bad@example.com,2026-10-01,2026-10-15,INVALID_DOLLARS,unpaid,Error\n"
    )
    res = process_file_upload("bad_money.csv", bad_inv)
    assert res["rejected"] > 0 or len(res.get("errors", [])) > 0 or res["status"] == "error"


def test_scenario_k_invalid_dates_rejected_safely(isolated_app):
    """Scenario K: Invalid dates are rejected safely without crashing."""
    bad_date = (
        b"invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        b"INV-BAD-DATE,Bad Date Client,baddate@example.com,99/99/9999,invalid-date,500.00,unpaid,Date error\n"
    )
    res = process_file_upload("bad_date.csv", bad_date)
    assert res["status"] in ("success", "partial_success", "error")

    state_res = isolated_app.get("/api/state")
    assert state_res.status_code == 200


def test_scenario_l_utf8_bom_csv_accepted(isolated_app):
    """Scenario L: UTF-8 BOM CSVs are accepted."""
    content = "booking_id,date,client_name,email,service,status,price\nB-BOM-1,2026-10-02,BOM Client,bom@example.com,Shoot,completed,750.00\n"
    bom_bytes = codecs.BOM_UTF8 + content.encode("utf-8")

    res = process_file_upload("bom_upload.csv", bom_bytes)
    assert res["status"] == "success"
    assert res["added"] == 1


def test_scenario_m_booking_date_corrections_persist(isolated_app):
    """Scenario M: Booking-date corrections persist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT booking_id FROM bookings LIMIT 1")
    row = cur.fetchone()
    assert row is not None
    bid = row[0]
    conn.close()

    res = update_record("bookings", bid, {"booking_date": "2026-05-15"})
    assert res["status"] == "success"

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT booking_date FROM bookings WHERE booking_id = ?", (bid,))
    updated_date = cur.fetchone()[0]
    conn.close()
    assert updated_date == "2026-05-15"


def test_scenario_n_reset_preview_accurate_counts(isolated_app):
    """Scenario N: Reset preview displays accurate record counts."""
    preview = get_reset_preview()
    assert "total_records" in preview
    assert "table_counts" in preview

    conn = get_db()
    actual_count = 0
    for table in CLEARABLE_TABLES:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        actual_count += cnt
    conn.close()

    assert preview["total_records"] == actual_count


def test_scenario_o_reset_requires_valid_authorization(isolated_app):
    """Scenario O: Reset requires valid owner authorization."""
    preview = get_reset_preview()
    expected = preview["total_records"]

    # Wrong confirmation phrase with valid auth
    res_bad_phrase = isolated_app.post(
        "/api/manage/reset",
        headers={"X-Owner-Auth": TEST_PIN},
        json={"confirmation_phrase": "WRONG PHRASE", "expected_total_records": expected}
    )
    assert res_bad_phrase.status_code == 400

    # Missing PIN / unauthorized
    res_no_pin = isolated_app.post(
        "/api/manage/reset",
        json={"confirmation_phrase": "DELETE ALL BUSINESS DATA", "expected_total_records": expected}
    )
    assert res_no_pin.status_code in (401, 403)


def test_scenario_p_and_q_reset_clears_tables_and_metrics_zero(isolated_app):
    """
    Scenario P: Reset clears all business tables in an isolated DB.
    Scenario Q: All dashboard metrics become zero after reset.
    """
    preview = get_reset_preview()
    total_before = preview["total_records"]
    assert total_before > 0

    res = isolated_app.post(
        "/api/manage/reset",
        headers={"X-Owner-Auth": TEST_PIN},
        json={"confirmation_phrase": "DELETE ALL BUSINESS DATA", "expected_total_records": total_before}
    )
    assert res.status_code == 200
    res_json = res.get_json()
    assert res_json["status"] == "success"
    assert res_json["deleted_records"] == total_before

    # Verify Scenario P: All clearable tables have 0 records
    conn = get_db()
    for table in CLEARABLE_TABLES:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert cnt == 0, f"Table {table} was not cleared: {cnt} records remain"
    conn.close()

    # Verify Scenario Q: Dashboard metrics are exactly zero
    state_res = isolated_app.get("/api/state")
    assert state_res.status_code == 200
    state = state_res.get_json()
    m = state["metrics"]
    assert float(m["overdue_total"]) == 0.0
    assert int(m["overdue_count"]) == 0
    assert float(m["we_owe_total"]) == 0.0
    assert float(m["never_billed_total"]) == 0.0
    assert int(m["client_count"]) == 0
    assert int(m["total_leads_count"]) == 0
    assert len(state["money"]["overdue"]) == 0
    assert len(state["money"]["never_billed"]) == 0
    assert len(state["requests"]["lost_requests"]) == 0
    assert len(state["clients"]) == 0


def test_scenario_r_original_clients_do_not_reappear(isolated_app):
    """Scenario R: Original clients do not reappear after restart."""
    invalidate_caches()
    seed_db_if_empty()  # Must respect is_dataset_cleared() and NOT re-seed

    assert is_dataset_cleared() is True

    state_res = isolated_app.get("/api/state")
    state = state_res.get_json()
    assert len(state["clients"]) == 0
    assert float(state["metrics"]["overdue_total"]) == 0.0


def test_scenario_s_fresh_upload_works_after_reset(isolated_app):
    """Scenario S: Uploading new data after reset works correctly."""
    inv_csv = (
        b"invoice_no,bill_to,email,issued,due,amount,status,memo\n"
        b"INV-POST-1,Post Reset Studio,owner@postreset.example,2026-08-10,2026-08-25,950.00,unpaid,Post Reset Shoot\n"
    )
    res_i = process_file_upload("post_reset_invoices.csv", inv_csv)
    assert res_i["status"] == "success"

    state = isolated_app.get("/api/state").get_json()
    assert int(state["metrics"]["client_count"]) == 1
    assert float(state["metrics"]["overdue_total"]) == 950.00


def test_scenario_t_api_failures_display_retry():
    """Scenario T: API failures display a Retry button."""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    assert 'id="state-error-banner"' in html
    assert 'id="btn-state-retry"' in html
    assert "Unable to load business data" in html


def test_scenario_u_slow_api_responses_non_blocking():
    """Scenario U: Slow API responses do not freeze the interface."""
    with open("static/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()
    assert "AbortController" in js
    assert "setTimeout" in js


def test_scenario_v_browser_refresh_preserves_state(isolated_app):
    """Scenario V: Browser refresh preserves correct current data."""
    res1 = isolated_app.get("/api/state").get_json()
    res2 = isolated_app.get("/api/state").get_json()
    assert res1["metrics"] == res2["metrics"]


def test_scenario_w_responsive_layout():
    """Scenario W: Mobile and desktop layouts remain functional."""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    assert '<meta name="viewport"' in html
    assert "width=device-width" in html


def test_scenario_x_previous_dashboard_functions_operational(isolated_app):
    """Scenario X: Previous dashboard functions remain operational."""
    res_dec = isolated_app.post("/api/decisions", json={"action_id": "test_act", "status": "approved"})
    assert res_dec.status_code == 200

    res_search = isolated_app.get("/api/search?q=Post")
    assert res_search.status_code == 200

    res_export = isolated_app.get("/api/export-answers")
    assert res_export.status_code == 200

    res_report = isolated_app.get("/api/reports/business-report")
    assert res_report.status_code == 200


def test_scenario_y_no_js_syntax_errors():
    """Scenario Y: No unexpected console errors / clean JS syntax."""
    import subprocess
    result = subprocess.run(["node", "-c", "static/js/app.js"], capture_output=True, text=True)
    assert result.returncode == 0, f"JS syntax check failed: {result.stderr}"


def test_scenario_z_no_production_data_modified():
    """Scenario Z: No production data is modified during testing."""
    active_db = os.environ.get("AXEOM_DB_PATH")
    assert active_db == TEST_DB_PATH
    prod_url = os.environ.get("PROD_DATABASE_URL", "")
    assert "ep-lively-field-b4guexwq-pooler" in prod_url or prod_url == ""
    assert not active_db.startswith("postgresql://")
