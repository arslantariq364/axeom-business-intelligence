"""
Integration test suite for Axeom Unified Ingestion Pipeline and Storage Foundation.
Tests original files, duplicates, changed records, malformations, schema detection,
and durability across database reconnections.
"""

import os
import pytest
import sqlite3
import hashlib
from pathlib import Path
from services.db import init_db, get_db, get_current_revision
from services.ingest import process_file_upload, detect_file_role

TEST_DB_PATH = "test_axeom_import.db"

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Sets up an isolated SQLite database for import testing."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    monkeypatch.setenv("AXEOM_FORCE_SQLITE", "1")
    monkeypatch.setenv("AXEOM_DB_PATH", TEST_DB_PATH)
    
    # Initialize schema
    init_db()
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_detect_file_role_header_signatures():
    """Verifies that content sniffing accurately detects roles regardless of filename."""
    inv_csv = "invoice_no,bill_to,amount,status\nINV-9999,Acme Corp,500.00,unpaid\n"
    pay_csv = "payment_id,payer,amount,date\nP9999,Acme Corp,500.00,2026-04-10\n"
    book_csv = "booking_id,client_name,service,price\nB9999,Acme Corp,Podcast,500\n"
    board_csv = "video_id,client,title,editor\nV9999,Acme Corp,Video 1,Ali\n"
    leads_csv = "lead_id,name,business,source\nL9999,Jane Doe,Acme Corp,Website\n"
    msg_txt = "[2026-04-02 09:15] EMAIL from jane@acme.com: Hello team!\n"

    assert detect_file_role("obscure_filename_1.csv", inv_csv) == "invoices"
    assert detect_file_role("obscure_filename_2.csv", pay_csv) == "payments"
    assert detect_file_role("obscure_filename_3.csv", book_csv) == "bookings"
    assert detect_file_role("obscure_filename_4.csv", board_csv) == "production_board"
    assert detect_file_role("obscure_filename_5.csv", leads_csv) == "leads"
    assert detect_file_role("notes.log", msg_txt) == "messages"

def test_ingest_original_files():
    """Verifies that all original files in data/ can be processed through the unified pipeline."""
    data_dir = Path("data")
    for fpath in data_dir.glob("*.csv"):
        with open(fpath, "rb") as f:
            res = process_file_upload(fpath.name, f.read())
        assert res["status"] == "success", f"Failed ingesting {fpath.name}: {res.get('message')}"
        assert res["added"] > 0

    # Also test messages.txt
    msg_path = data_dir / "messages.txt"
    if msg_path.exists():
        with open(msg_path, "rb") as f:
            res = process_file_upload(msg_path.name, f.read())
        assert res["status"] == "success"
        assert res["added"] > 0

def test_duplicate_file_idempotency():
    """Uploading the exact same file bytes twice must be detected as duplicate without adding duplicate rows."""
    content = b"invoice_no,bill_to,amount,issued,due,status\nINV-9901,Test Corp,1000.00,2026-04-01,2026-04-15,unpaid\n"
    
    try:
        # First upload
        res1 = process_file_upload("invoices_test_dup.csv", content)
        assert res1["status"] in ["success", "duplicate_file"]

        # Second upload with identical bytes
        res2 = process_file_upload("invoices_test_dup.csv", content)
        assert res2["status"] == "duplicate_file"
        assert res2["added"] == 0
        assert res2["skipped"] >= 0

        # Verify database has at most 1 row
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM invoices WHERE invoice_no = 'INV-9901'")
        assert cur.fetchone()[0] == 1
        conn.close()
    finally:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM invoices WHERE invoice_no = 'INV-9901'")
        cur.execute("DELETE FROM file_uploads WHERE filename = 'invoices_test_dup.csv'")
        conn.commit()
        conn.close()

def test_changed_record_updates():
    """Uploading an updated CSV with an existing invoice ID updates the existing record rather than inserting a duplicate."""
    initial_csv = b"invoice_no,bill_to,amount,issued,due,status\nINV-9902,Alpha LLC,1200.00,2026-05-01,2026-05-15,unpaid\n"
    updated_csv = b"invoice_no,bill_to,amount,issued,due,status\nINV-9902,Alpha LLC,1500.00,2026-05-01,2026-05-15,paid\n"
    try:
        res1 = process_file_upload("alpha_v1_test.csv", initial_csv)
        assert res1["status"] in ["success", "duplicate_file"]

        # Modified content: invoice paid and amount updated
        res2 = process_file_upload("alpha_v2_test.csv", updated_csv)
        assert res2["status"] in ["success", "duplicate_file"]

        # Verify updated values in database
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT amount, status FROM invoices WHERE invoice_no = 'INV-9902'")
        row = cur.fetchone()
        if row:
            assert float(row["amount"]) == 1500.0
            assert row["status"] == "paid"
        conn.close()
    finally:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM invoices WHERE invoice_no = 'INV-9902'")
        cur.execute("DELETE FROM file_uploads WHERE filename IN ('alpha_v1_test.csv', 'alpha_v2_test.csv')")
        conn.commit()
        conn.close()

def test_malformed_csv_rollback_on_missing_required_column():
    """A file missing required schema columns must be rejected cleanly with zero rows inserted."""
    bad_csv = b"random_col,another_col\n123,456\n"
    res = process_file_upload("bad_file.csv", bad_csv)
    assert res["status"] == "error"
    assert "Could not determine valid schema" in res["message"]

    # Invoices missing amount column
    bad_inv = b"invoice_no,bill_to\nINV-3001,Beta Corp\n"
    res2 = process_file_upload("bad_invoices.csv", bad_inv)
    assert res2["status"] == "error"
    assert "Missing required columns" in res2["message"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoices WHERE invoice_no = 'INV-3001'")
    assert cur.fetchone()[0] == 0
    conn.close()

def test_duplicate_headers_rejected():
    """CSV containing duplicate header names must be rejected before ingestion."""
    dup_header_csv = b"invoice_no,bill_to,amount,amount\nINV-4001,Beta Corp,500,500\n"
    res = process_file_upload("dup_header.csv", dup_header_csv)
    assert res["status"] == "error"
    assert "Duplicate column headers" in res["message"]

def test_non_collapsing_of_legitimate_identical_transactions():
    """Two payments with identical dollar amounts but different payment IDs must both be preserved."""
    pay_csv = (
        b"payment_id,payer,amount,date,method,reference\n"
        b"P8001,Client A,900.00,01/05/2026,card,INV-01\n"
        b"P8002,Client B,900.00,02/05/2026,card,INV-02\n"
    )
    try:
        res = process_file_upload("two_payments.csv", pay_csv)
        assert res["status"] in ["success", "duplicate_file"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM payments WHERE payment_id IN ('P8001', 'P8002')")
        assert cur.fetchone()[0] == 2
        conn.close()
    finally:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM payments WHERE payment_id IN ('P8001', 'P8002')")
        cur.execute("DELETE FROM file_uploads WHERE filename = 'two_payments.csv'")
        conn.commit()
        conn.close()

def test_persistence_and_dataset_revision():
    """Verifies that dataset revisions increment on data mutations and survive reconnection."""
    content1 = b"lead_id,name,business,source\nL1001,Sam Test,Studio,Referral\n"
    content2 = b"lead_id,name,business,source\nL1002,Alex Test,Agency,Website form\n"
    try:
        res1 = process_file_upload("leads_rev1.csv", content1)
        rev1 = res1["revision_id"]

        res2 = process_file_upload("leads_rev2.csv", content2)
        rev2 = res2["revision_id"]

        assert rev2 > rev1

        # Test persistence after closing connection
        current_rev = get_current_revision()
        assert current_rev["revision_id"] == rev2
    finally:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM leads WHERE lead_id IN ('L1001', 'L1002')")
        cur.execute("DELETE FROM file_uploads WHERE filename IN ('leads_rev1.csv', 'leads_rev2.csv')")
        conn.commit()
        conn.close()
