"""
Surgical production restoration and integrity verification for Neon branch 'main'.
Restores INV-1001 to authentic Northpoint Church values and removes test contamination.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv(".env")
PROD_URL = os.environ.get("PROD_DATABASE_URL")

def main():
    print(f"Connecting to Neon Production Branch (main): {PROD_URL[:45]}...")
    conn = psycopg.connect(PROD_URL, row_factory=dict_row)
    cur = conn.cursor()

    # 1. Inspect INV-1001 before
    cur.execute("SELECT * FROM invoices WHERE invoice_no = 'INV-1001'")
    inv_1001_before = cur.fetchone()
    print(f"INV-1001 before: {dict(inv_1001_before)}")

    # 2. Restore INV-1001 to authentic Pack 01 baseline
    cur.execute("""
    UPDATE invoices
    SET bill_to = 'Northpoint Church',
        email = 'media@northpointdfw.org',
        issued = '2026-08-01',
        due = '2026-08-15',
        amount = 300.0,
        status = 'paid',
        memo = 'August Retainer - 4 Videos',
        source_file = 'invoices.csv',
        deleted_at = NULL,
        is_archived = 0
    WHERE invoice_no = 'INV-1001'
    """)
    print("Updated INV-1001 to Northpoint Church ($300.00, paid).")

    # 3. Remove synthetic test invoices
    cur.execute("DELETE FROM invoices WHERE invoice_no IN ('INV-2001', 'INV-9100')")
    print(f"Deleted {cur.rowcount} synthetic test invoices.")

    # 4. Remove synthetic file uploads
    cur.execute("DELETE FROM file_uploads WHERE filename LIKE 'alpha%' OR filename LIKE 'test%'")
    print(f"Deleted {cur.rowcount} synthetic file upload records.")

    # 5. Remove synthetic test messages
    cur.execute("DELETE FROM messages WHERE source_file LIKE 'new_test_messages_%.txt'")
    print(f"Deleted {cur.rowcount} synthetic test message records.")

    # 6. Remove synthetic decisions
    cur.execute("DELETE FROM owner_decisions WHERE action_id = 'test_action_01'")
    print(f"Deleted {cur.rowcount} synthetic owner decisions.")

    conn.commit()

    # 7. Verification: Run Finance Reconciliation on Production
    print("\nVerifying Invariants on Production DB:")
    cur.execute("SELECT COUNT(*) FROM clients WHERE deleted_at IS NULL")
    clients_cnt = cur.fetchone()['count']
    print(f"Active Clients: {clients_cnt} (Expected: 29)")

    # Overdue count and sum
    cur.execute("""
    SELECT COUNT(*) as count, COALESCE(SUM(amount), 0.0) as total
    FROM invoices
    WHERE status != 'paid' AND due <= '2026-10-06' AND deleted_at IS NULL
    """)
    overdue = cur.fetchone()
    print(f"Overdue Invoices: {overdue['count']} totaling ${float(overdue['total']):,.2f}")

    # INV-1001 after
    cur.execute("SELECT * FROM invoices WHERE invoice_no = 'INV-1001'")
    inv_1001_after = cur.fetchone()
    print(f"INV-1001 after: {dict(inv_1001_after)}")

    conn.close()

if __name__ == "__main__":
    main()
