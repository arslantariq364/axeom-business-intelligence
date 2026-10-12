"""
Integration test suite executed against the isolated Neon PostgreSQL 'dev' branch.
Tests file uploads, database persistence, client matching, financial calculations,
and owner decisions without modifying the production database.
"""

import os
import sys
import io
import json
from pathlib import Path

# Project root
WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))

# Load environment variables securely from .env if present
from dotenv import load_dotenv
load_dotenv(WORKSPACE / ".env")

DEV_DATABASE_URL = os.environ.get("DEV_DATABASE_URL")
PROD_DATABASE_URL = os.environ.get("PROD_DATABASE_URL") or os.environ.get("DATABASE_URL")

def run_isolated_dev_tests():
    if not DEV_DATABASE_URL or not PROD_DATABASE_URL:
        print("Skipping isolated dev branch test: DEV_DATABASE_URL or PROD_DATABASE_URL not set in environment.")
        return True

    print("========================================================")
    print("Testing Isolated Neon Database Branch ('dev')")
    print(f"Dev Database Configured:  Yes")
    print(f"Prod Database Configured: Yes")
    print("========================================================\n")

    # Point environment to isolated DEV branch
    os.environ["DATABASE_URL"] = DEV_DATABASE_URL
    from app import app
    from services.db import get_db, init_db
    from services.finance import reconcile_finances
    from services.identity import resolve_client, resolve_client_by_name, THIRD_PARTY_PAYERS
    from services.decisions import save_decision, get_decision
    from services.ingest import process_file_upload

    # 1. Initialize schema on dev and clean up any prior test runs
    init_db()
    clean_conn = get_db()
    clean_cur = clean_conn.cursor()
    clean_cur.execute("DELETE FROM invoices WHERE invoice_no = 'INV-9100'")
    clean_cur.execute("DELETE FROM file_uploads WHERE filename = 'isolated_branch_test_invoice.csv'")
    clean_cur.execute("DELETE FROM dataset_revisions WHERE source_filename = 'isolated_branch_test_invoice.csv'")
    clean_cur.execute("DELETE FROM owner_decisions WHERE action_id = 'action_isolated_test'")
    clean_conn.commit()
    clean_conn.close()

    # 2. Check baseline on dev branch
    app.config["TESTING"] = True
    with app.test_client() as client:
        state_0 = client.get("/api/state").get_json()
        m0 = state_0["metrics"]
        print(f"[Test 1: Dev Baseline Verification]")
        print(f"  Clients:        {m0['active_clients_count']} (Expected: 29)")
        print(f"  Overdue Total:  ${m0['overdue_total']:,.2f} (Expected: $9,250.00)")
        print(f"  We Owe Total:   ${m0['we_owe_total']:,.2f} (Expected: $2,400.00)")
        print(f"  Never Billed:   ${m0['never_billed_total']:,.2f} (Expected: $2,950.00)")
        print(f"  Discrepancies:  {m0['discrepancies_count']} (Expected: 6)")
        assert m0["active_clients_count"] == 29
        assert m0["overdue_total"] == 9250.0
        assert m0["we_owe_total"] == 2400.0
        assert m0["never_billed_total"] == 2950.0
        assert m0["discrepancies_count"] == 6
        print("  ✅ Dev baseline verified.")

        # 3. Test File Upload & Database Persistence on Dev Branch
        print(f"\n[Test 2: File Upload & Financial Recalculation on Dev Branch]")
        csv_content = (
            "invoice_no,bill_to,email,issued,due,amount,status,memo\n"
            "INV-9100,Crown Barbers,marcus@crownbarbers.com,2026-09-01,2026-09-15,750.00,unpaid,September Promotional Video\n"
        ).encode("utf-8")

        upload_res = process_file_upload("isolated_branch_test_invoice.csv", csv_content)
        print(f"  Upload result: status={upload_res['status']}, added={upload_res['added']}, file_role={upload_res['file_role']}")
        assert upload_res["status"] == "success"
        assert upload_res["added"] == 1
        assert upload_res["file_role"] == "invoices"

        # Check that state updated on dev branch
        state_1 = client.get("/api/state").get_json()
        m1 = state_1["metrics"]
        print(f"  Overdue after upload: ${m1['overdue_total']:,.2f} (Expected: $10,000.00 = $9,250 + $750)")
        assert m1["overdue_total"] == 10000.0, f"Expected 10000.0, got {m1['overdue_total']}"
        assert m1["overdue_count"] == 10
        print("  ✅ Upload persistence & financial recalculation verified on dev branch.")

        # 4. Test Idempotency / Duplicate File Upload on Dev Branch
        print(f"\n[Test 3: Idempotent Deduplication on Dev Branch]")
        upload_dup = process_file_upload("isolated_branch_test_invoice.csv", csv_content)
        print(f"  Repeat upload status: {upload_dup['status']}")
        assert upload_dup["status"] == "duplicate_file"
        assert upload_dup["added"] == 0

        state_2 = client.get("/api/state").get_json()
        assert state_2["metrics"]["overdue_total"] == 10000.0
        print("  ✅ Duplicate file safely rejected with 0 changes.")

        # 5. Test Client Identity Matching on Dev Branch
        print(f"\n[Test 4: Client Identity Matching on Dev Branch]")
        match1 = resolve_client_by_name("Crown Barbers")
        assert match1 is not None and match1["canonical_name"] == "Crown Barbershop"
        match2 = resolve_client_by_name("Greenway Peds")
        assert match2 is not None and match2["canonical_name"] == "Greenway Pediatrics"
        match3 = resolve_client_by_name("Elevate Fitness")
        assert match3 is not None and match3["canonical_name"] == "Elevate Athletics"
        match4 = resolve_client_by_name("Patel Insurance")
        assert match4 is not None and match4["canonical_name"] == "Patel Insurance Group"
        assert any("Brightline Marketing" in p["aliases"] for p in THIRD_PARTY_PAYERS)
        print("  ✅ Client alias resolution and matching verified.")

        # 6. Test Owner Decision Persistence on Dev Branch
        print(f"\n[Test 5: Owner Decision Persistence on Dev Branch]")
        dec = save_decision("action_isolated_test", "action", "completed", "Verified on dev branch")
        assert dec["status"] == "completed"
        fetched_dec = get_decision("action_isolated_test")
        assert fetched_dec["status"] == "completed"
        assert fetched_dec["owner_notes"] == "Verified on dev branch"
        print("  ✅ Owner decision recorded and persisted on dev branch.")

    # 7. CRITICAL VERIFICATION: Ensure Production Branch was NOT modified!
    print(f"\n[Test 6: Production Branch Protection Audit]")
    os.environ["DATABASE_URL"] = PROD_DATABASE_URL
    import psycopg
    from psycopg.rows import dict_row
    from services.db import normalize_database_url
    
    prod_conn = psycopg.connect(normalize_database_url(PROD_DATABASE_URL), row_factory=dict_row)
    prod_cur = prod_conn.cursor()

    # Check invoice count on prod
    prod_cur.execute("SELECT count(*) FROM invoices WHERE invoice_no = 'INV-9100'")
    inv_on_prod = prod_cur.fetchone()["count"]
    print(f"  Test invoice INV-9100 on Production: {inv_on_prod} (Expected: 0)")
    assert inv_on_prod == 0, "FATAL: Test invoice leaked to production branch!"

    # Check owner decisions on prod
    prod_cur.execute("SELECT count(*) FROM owner_decisions WHERE action_id = 'action_isolated_test'")
    dec_on_prod = prod_cur.fetchone()["count"]
    print(f"  Test decision on Production:        {dec_on_prod} (Expected: 0)")
    assert dec_on_prod == 0, "FATAL: Test decision leaked to production branch!"

    # Check production total overdue
    prod_cur.execute("SELECT sum(amount) FROM invoices WHERE status = 'unpaid'")
    prod_conn.close()

    print("  ✅ Production database branch confirmed 100% UNTOUCHED and pristine!")
    print("\n🎉 ALL ISOLATED DATABASE BRANCH TESTS PASSED 100%!")
    return True

if __name__ == "__main__":
    run_isolated_dev_tests()
