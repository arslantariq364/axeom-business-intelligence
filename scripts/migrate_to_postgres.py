"""
Automated, idempotent database migration script from SQLite to Neon PostgreSQL.
Transfers all tables, canonical clients, business records, and audit logs,
updates PostgreSQL auto-increment sequences, and performs complete financial verification.
"""

import os
import sys
import sqlite3
import datetime
from pathlib import Path

# Add project root to path
WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))

from services.db import get_db, init_db, is_postgres, normalize_database_url, get_database_url
import psycopg
from psycopg.rows import dict_row

TABLES_TO_MIGRATE = [
    {
        "table": "dataset_revisions",
        "pk": "revision_id",
        "sequence_col": "revision_id",
        "cols": ["revision_id", "created_at", "source_filename", "source_file_hash", "summary_json"]
    },
    {
        "table": "file_uploads",
        "pk": "sha256_hash",
        "sequence_col": "id",
        "cols": ["id", "filename", "file_role", "sha256_hash", "row_count", "added_count", "updated_count", "skipped_count", "rejected_count", "status", "details", "uploaded_at"]
    },
    {
        "table": "clients",
        "pk": "id",
        "sequence_col": None,
        "cols": ["id", "canonical_name", "primary_contact", "emails", "phones", "payer_aliases", "status", "notes"]
    },
    {
        "table": "third_party_payers",
        "pk": "name",
        "sequence_col": None,
        "cols": ["name", "pays_for", "aliases", "emails", "phones", "evidence"]
    },
    {
        "table": "bookings",
        "pk": "booking_id",
        "sequence_col": None,
        "cols": ["booking_id", "booking_date", "client_name", "email", "service", "status", "price", "source_file"]
    },
    {
        "table": "invoices",
        "pk": "invoice_no",
        "sequence_col": None,
        "cols": ["invoice_no", "bill_to", "email", "issued", "due", "amount", "status", "memo", "source_file"]
    },
    {
        "table": "payments",
        "pk": "payment_id",
        "sequence_col": None,
        "cols": ["payment_id", "payment_date", "payer", "payer_email", "amount", "method", "reference", "source_file"]
    },
    {
        "table": "production_board",
        "pk": "video_id",
        "sequence_col": None,
        "cols": ["video_id", "client", "title", "editor", "stage", "notes_on_board", "revisions", "editor_hours", "client_approved_on", "shoot_booking", "source_file"]
    },
    {
        "table": "leads",
        "pk": "lead_id",
        "sequence_col": None,
        "cols": ["lead_id", "created", "name", "business", "email", "phone", "source", "first_reply", "status", "source_file"]
    },
    {
        "table": "messages",
        "pk": "msg_hash",
        "sequence_col": "id",
        "cols": ["id", "msg_hash", "line_no", "msg_datetime", "channel", "direction", "entity", "body", "source_file"]
    },
    {
        "table": "costs",
        "pk": "id",
        "sequence_col": "id",
        "cols": ["id", "item", "cost", "note", "source_file"]
    },
    {
        "table": "team",
        "pk": "id",
        "sequence_col": "id",
        "cols": ["id", "name", "role", "joined", "pay", "source_file"]
    },
    {
        "table": "owner_decisions",
        "pk": "action_id",
        "sequence_col": None,
        "cols": ["action_id", "decision_type", "status", "owner_notes", "updated_at"]
    },
    {
        "table": "jev_cache",
        "pk": "cache_key",
        "sequence_col": None,
        "cols": ["cache_key", "model_version", "prompt_hash", "response_json", "created_at", "result_source", "provider_model", "app_question_version", "input_hash"]
    },
    {
        "table": "message_classifications",
        "pk": "id",
        "sequence_col": "id",
        "cols": ["id", "msg_id", "msg_hash", "predicted_intent", "confidence", "provider", "provider_model", "multi_intent", "actionable_billing", "classified_at"]
    }
]


def run_migration(sqlite_path="axeom_pre_migration_backup.db", database_url=None):
    if database_url is None:
        database_url = get_database_url()
    if not database_url:
        print("❌ Error: DATABASE_URL must be provided or set in environment.")
        return False

    if not os.path.exists(sqlite_path):
        # Fall back to axeom.db if backup path does not exist
        if os.path.exists("axeom.db"):
            sqlite_path = "axeom.db"
        else:
            print(f"❌ Error: SQLite source database not found at '{sqlite_path}'.")
            return False

    print(f"\n========================================================")
    print(f"Axeom Neon PostgreSQL Migration & Data Verification")
    print(f"Source SQLite: {sqlite_path}")
    print(f"Target Neon DB: {database_url.split('@')[-1] if '@' in database_url else 'PostgreSQL'}")
    print(f"========================================================\n")

    # 1. Connect SQLite
    s_conn = sqlite3.connect(sqlite_path)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    # 2. Connect PostgreSQL & Initialize Schema
    dsn = normalize_database_url(database_url)
    pg_conn = psycopg.connect(dsn, row_factory=dict_row)
    
    # Initialize target schema
    os.environ["DATABASE_URL"] = database_url
    init_db()
    pg_cur = pg_conn.cursor()

    total_records_migrated = 0

    for item in TABLES_TO_MIGRATE:
        t_name = item["table"]
        pk_col = item["pk"]
        cols = item["cols"]
        seq_col = item["sequence_col"]

        # Check if table exists in SQLite
        s_cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t_name}'")
        if not s_cur.fetchone():
            print(f"  ⚠️ Skipping '{t_name}' (not present in SQLite source)")
            continue

        s_cur.execute(f"SELECT * FROM {t_name}")
        rows = s_cur.fetchall()

        if not rows:
            print(f"  ℹ️ Table '{t_name}': 0 rows in source")
            continue

        col_names = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))
        
        # Build ON CONFLICT clause for idempotency
        update_set = ", ".join([f"{c} = EXCLUDED.{c}" for c in cols if c != pk_col])
        if update_set:
            conflict_clause = f"ON CONFLICT ({pk_col}) DO UPDATE SET {update_set}"
        else:
            conflict_clause = f"ON CONFLICT ({pk_col}) DO NOTHING"

        insert_sql = f"""
        INSERT INTO {t_name} ({col_names})
        VALUES ({placeholders})
        {conflict_clause}
        """

        migrated_for_table = 0
        for r in rows:
            vals = []
            for c in cols:
                v = r[c] if c in r.keys() else None
                vals.append(v)
            pg_cur.execute(insert_sql, vals)
            migrated_for_table += 1

        pg_conn.commit()
        total_records_migrated += migrated_for_table
        print(f"  ✅ Migrated '{t_name}': {migrated_for_table} rows")

        # Update sequence for tables with SERIAL primary keys
        if seq_col:
            try:
                pg_cur.execute(f"""
                SELECT setval(pg_get_serial_sequence('{t_name}', '{seq_col}'), COALESCE((SELECT MAX({seq_col}) FROM {t_name}), 1));
                """)
                pg_conn.commit()
            except Exception as e:
                pass

    s_conn.close()
    pg_conn.close()

    print(f"\n🎉 Total rows successfully migrated to PostgreSQL: {total_records_migrated}")

    # 3. Independent Verification of Financial Invariants
    print("\n--------------------------------------------------------")
    print("Running Independent Financial & Business Data Audit on Neon...")
    print("--------------------------------------------------------")
    
    from services.finance import reconcile_finances
    from services.requests import get_requests_and_leads
    from services.identity import CANONICAL_CLIENTS

    fin = reconcile_finances()
    req = get_requests_and_leads()

    client_count = len(CANONICAL_CLIENTS)
    overdue_total = fin["overdue_total"]
    overdue_count = len(fin["overdue"])
    we_owe_total = fin["we_owe_total"]
    we_owe_count = len(fin["we_owe"])
    never_billed_total = fin["never_billed_total"]
    never_billed_count = len(fin["never_billed"])
    discrepancies_count = len(fin["discrepancies"])
    lost_requests_count = req["lost_requests_count"]
    unreplied_leads_count = req["unreplied_leads_count"]

    print(f"  1. Unique Clients:               {client_count} (Expected: 29)")
    print(f"  2. Overdue Invoices:             {overdue_count} totaling ${overdue_total:,.2f} (Expected: 9 totaling $9,250.00)")
    print(f"  3. We Owe Liabilities:           {we_owe_count} totaling ${we_owe_total:,.2f} (Expected: 2 totaling $2,400.00)")
    print(f"  4. Never Billed Work:            {never_billed_count} totaling ${never_billed_total:,.2f} (Expected: 3 totaling $2,950.00)")
    print(f"  5. Billing Tool Discrepancies:   {discrepancies_count} (Expected: 6)")
    print(f"  6. Lost Requests:                {lost_requests_count} (Expected: 33)")
    print(f"  7. Unanswered Leads:             {unreplied_leads_count} (Expected: 22)")

    assert client_count == 29, f"Client count mismatch: {client_count} != 29"
    assert overdue_total == 9250.0, f"Overdue total mismatch: {overdue_total} != 9250.0"
    assert we_owe_total == 2400.0, f"We owe total mismatch: {we_owe_total} != 2400.0"
    assert never_billed_total == 2950.0, f"Never billed mismatch: {never_billed_total} != 2950.0"
    assert discrepancies_count == 6, f"Discrepancies mismatch: {discrepancies_count} != 6"
    assert lost_requests_count == 33, f"Lost requests mismatch: {lost_requests_count} != 33"
    assert unreplied_leads_count == 22, f"Unreplied leads mismatch: {unreplied_leads_count} != 22"

    print("\n✅ Neon PostgreSQL Database Migration & Financial Audit PASSED 100%!")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate Axeom data from SQLite to Neon PostgreSQL")
    parser.add_argument("--sqlite-path", default="axeom_pre_migration_backup.db", help="Path to source SQLite database")
    parser.add_argument("--database-url", default=None, help="Target PostgreSQL connection string (defaults to DATABASE_URL)")
    args = parser.parse_args()

    run_migration(sqlite_path=args.sqlite_path, database_url=args.database_url)
