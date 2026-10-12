"""
Comprehensive Integration & Regression Test Suite for Axeom Data Management & Reporting.

Covers:
- Owner authorization (session and header-based X-Owner-Auth)
- Record viewing, searching, and pagination across all tables
- Record editing and audit trail logging
- Record archiving and restoration
- Consequence / impact analysis pre-flight calculations
- Financial preservation invariant during archiving/soft-deletion
- Unauthorized deletion protection (401/403)
- Upload history and reversal safeguards
- System reset protections (401/403 without auth, 400 without exact confirmation phrase)
- Mode B Live Executive Business Report vs Mode A challenge answers snapshot immutability
"""

import json
import pytest
from app import app
from services.auth import OWNER_PIN

def test_owner_auth_endpoints(client):
    # 1. Initially unauthorized
    res = client.get('/api/auth/owner-status')
    assert res.status_code == 200
    assert res.get_json()["is_authorized"] is False

    # 2. Attempt login with invalid PIN
    res = client.post('/api/auth/owner-session', json={"owner_pin": "wrong-pin-123"})
    assert res.status_code == 401
    assert res.get_json()["is_authorized"] is False

    # 3. Valid PIN login
    res = client.post('/api/auth/owner-session', json={"owner_pin": OWNER_PIN})
    assert res.status_code == 200
    assert res.get_json()["is_authorized"] is True

    # 4. Status reflects authorized
    res = client.get('/api/auth/owner-status')
    assert res.status_code == 200
    assert res.get_json()["is_authorized"] is True

    # 5. Logout
    res = client.post('/api/auth/owner-logout')
    assert res.status_code == 200
    assert res.get_json()["is_authorized"] is False

def test_record_listing_and_filtering(client):
    # 1. Clients listing
    res = client.get('/api/manage/records?table=clients&limit=50')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "records" in data
    assert len(data["records"]) >= 29
    assert data["table"] == "clients"
    assert data["total_count"] >= 29

    # 2. Search filtering
    res = client.get('/api/manage/records?table=clients&search=Apex')
    assert res.status_code == 200
    records = res.get_json()["records"]
    assert len(records) >= 1
    assert any("Apex" in r["canonical_name"] for r in records)

    # 3. Other core tables
    for tbl in ["invoices", "payments", "bookings", "production_board", "leads", "messages"]:
        r = client.get(f'/api/manage/records?table={tbl}&limit=5')
        assert r.status_code == 200
        assert r.get_json()["status"] == "success"

def test_record_edit_and_audit_logging(client):
    # Login as owner
    client.post('/api/auth/owner-session', json={"owner_pin": OWNER_PIN})

    # 1. Fetch record C01 before edit
    res_orig = client.get('/api/manage/records/clients/C01')
    assert res_orig.status_code == 200
    orig_record = res_orig.get_json()["record"]
    orig_notes = orig_record.get("notes") or ""

    # 2. Update notes
    new_notes = f"{orig_notes} [QA Verified]"
    res_edit = client.put('/api/manage/records/clients/C01', json={
        "updated_fields": {"notes": new_notes}
    })
    assert res_edit.status_code == 200
    assert res_edit.get_json()["status"] == "success"
    assert res_edit.get_json()["record"]["notes"] == new_notes

    # 3. Check audit log
    res_audit = client.get('/api/manage/audit-logs?limit=5')
    assert res_audit.status_code == 200
    logs = res_audit.get_json()["audit_logs"]
    assert len(logs) > 0
    latest = logs[0]
    assert latest["action_type"] == "edit"
    assert latest["target_table"] == "clients"
    assert latest["record_id"] == "C01"

    # Revert notes back
    client.put('/api/manage/records/clients/C01', json={
        "updated_fields": {"notes": orig_notes}
    })

def test_record_archive_and_restore_financial_invariants(client):
    # Login as owner
    client.post('/api/auth/owner-session', json={"owner_pin": OWNER_PIN})

    # Baseline active clients
    state_before = client.get('/api/state').get_json()
    base_overdue = state_before["metrics"]["overdue_total"]

    # Archive client C29
    res_arch = client.post('/api/manage/records/clients/C29/archive')
    assert res_arch.status_code == 200
    assert res_arch.get_json()["status"] == "success"

    # Verify C29 is archived
    res_c29 = client.get('/api/manage/records/clients/C29')
    assert res_c29.get_json()["record"]["is_archived"] == 1

    # CRITICAL INVARIANT: Historical invoices and payments remain intact in the financial ledger
    state_after = client.get('/api/state').get_json()
    assert state_after["metrics"]["overdue_total"] == base_overdue

    # Restore client C29
    res_rest = client.post('/api/manage/records/clients/C29/restore')
    assert res_rest.status_code == 200
    assert res_rest.get_json()["status"] == "success"

    res_c29_rest = client.get('/api/manage/records/clients/C29')
    assert res_c29_rest.get_json()["record"]["is_archived"] == 0

def test_impact_analysis_endpoint(client):
    res = client.get('/api/manage/records/clients/C01/impact')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "impact" in data
    impact = data["impact"]
    assert "relationships" in impact
    assert "consequences_summary" in impact
    assert "historical invoices" in impact["consequences_summary"]

def test_soft_delete_requires_authorization(client):
    # 1. Unauthenticated DELETE must be rejected with 401 or 403
    res_unauth = client.delete('/api/manage/records/leads/L001')
    assert res_unauth.status_code in [401, 403]

    # 2. Authenticated via header X-Owner-Auth succeeds
    res_auth_header = client.delete('/api/manage/records/leads/L001', headers={
        "X-Owner-Auth": OWNER_PIN
    })
    assert res_auth_header.status_code == 200
    assert res_auth_header.get_json()["status"] == "success"

    # Verify L001 is marked deleted
    res_l001 = client.get('/api/manage/records/leads/L001')
    assert res_l001.status_code == 200
    assert res_l001.get_json()["record"]["deleted_at"] is not None

    # Restore L001 with auth header
    res_restore = client.post('/api/manage/records/leads/L001/restore', headers={
        "X-Owner-Auth": OWNER_PIN
    })
    assert res_restore.status_code == 200
    assert res_restore.get_json()["record"]["deleted_at"] is None

def test_upload_dataset_history_and_reversal(client):
    # 1. Uploads listing
    res = client.get('/api/manage/uploads')
    assert res.status_code == 200
    uploads = res.get_json()["uploads"]
    assert isinstance(uploads, list)

    if len(uploads) > 0:
        up_id = uploads[0]["id"]
        # 2. Impact preview
        res_imp = client.get(f'/api/manage/uploads/{up_id}/impact')
        assert res_imp.status_code == 200
        imp_data = res_imp.get_json()
        assert "impact_summary" in imp_data or "active_records_remaining" in imp_data

        # 3. Unauthenticated revert attempt fails
        res_rev_unauth = client.post(f'/api/manage/uploads/{up_id}/revert')
        assert res_rev_unauth.status_code in [401, 403]

def test_reset_data_protections(client):
    # 1. Reset preview is readable
    res_prev = client.get('/api/manage/reset/preview')
    assert res_prev.status_code == 200
    data = res_prev.get_json()
    assert "preview" in data
    assert "table_counts" in data["preview"]
    assert "clients" in data["preview"]["table_counts"]
    assert "warning" in data["preview"]

    # 2. Reset without auth fails
    res_no_auth = client.post('/api/manage/reset', json={"phrase": "RESET AXEOM DATA"})
    assert res_no_auth.status_code in [401, 403]

    # 3. Reset with auth but wrong confirmation phrase fails
    client.post('/api/auth/owner-session', json={"owner_pin": OWNER_PIN})
    res_bad_phrase = client.post('/api/manage/reset', json={"phrase": "WRONG PHRASE"})
    assert res_bad_phrase.status_code == 400
    assert "confirmation phrase" in res_bad_phrase.get_json()["message"]

def test_mode_b_business_report_generation_vs_mode_a(client):
    # 1. Mode B JSON report
    res_json = client.get('/api/reports/business-report?format=json')
    assert res_json.status_code == 200
    report = res_json.get_json()
    assert report["metadata"]["report_title"] == "Axeom Studio — Executive Business & Operations Report"
    assert report["metadata"]["report_mode"] == "MODE_B_CURRENT_BUSINESS_REPORT"
    assert "executive_summary" in report
    assert report["executive_summary"]["active_clients_count"] >= 29

    # 2. Mode B HTML report
    res_html = client.get('/api/reports/business-report?format=html')
    assert res_html.status_code == 200
    html_content = res_html.get_data(as_text=True)
    assert "<!DOCTYPE html>" in html_content
    assert "Executive Business &amp; Operations Report" in html_content or "Executive Business & Operations Report" in html_content
    assert "window.print()" in html_content

    # 3. Mode A snapshot immutability
    with open("submission/answers.json", "r", encoding="utf-8") as f:
        mode_a = json.load(f)
    assert mode_a["client_count"] == 29
    assert len(mode_a["clients"]) == 29
    assert mode_a["overdue_total"] == 9250.00
    assert len(mode_a["never_replied_leads"]) == 22
    assert len(mode_a["lost_requests"]) == 33
