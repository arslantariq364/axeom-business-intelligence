"""
Database layer for Axeom Studio Operations & Owner OS.
Manages SQLite connections, schema initialization, migrations, and revisions.
"""

import sqlite3
import os
import json
import datetime
from pathlib import Path

DB_PATH = os.environ.get("AXEOM_DB_PATH", "axeom.db")
DATA_DIR = Path("data")

def get_db():
    db_path = os.environ.get("AXEOM_DB_PATH", "axeom.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def clean_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(s)
    except ValueError:
        return default

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # 1. Dataset Revisions Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dataset_revisions (
        revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        source_filename TEXT,
        source_file_hash TEXT,
        summary_json TEXT
    )
    """)

    # 2. File Uploads Audit Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS file_uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_role TEXT NOT NULL,
        sha256_hash TEXT UNIQUE,
        row_count INTEGER DEFAULT 0,
        added_count INTEGER DEFAULT 0,
        updated_count INTEGER DEFAULT 0,
        skipped_count INTEGER DEFAULT 0,
        rejected_count INTEGER DEFAULT 0,
        status TEXT NOT NULL,
        details TEXT,
        uploaded_at TEXT NOT NULL
    )
    """)

    # 3. Canonical Clients & Payers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id TEXT PRIMARY KEY,
        canonical_name TEXT NOT NULL,
        primary_contact TEXT,
        emails TEXT,
        phones TEXT,
        payer_aliases TEXT,
        status TEXT,
        notes TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS third_party_payers (
        name TEXT PRIMARY KEY,
        pays_for TEXT NOT NULL,
        aliases TEXT,
        emails TEXT,
        phones TEXT,
        evidence TEXT
    )
    """)

    # 4. Bookings
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        booking_date TEXT,
        client_name TEXT NOT NULL,
        email TEXT,
        service TEXT,
        status TEXT,
        price REAL DEFAULT 0.0,
        source_file TEXT
    )
    """)

    # 5. Invoices
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_no TEXT PRIMARY KEY,
        bill_to TEXT NOT NULL,
        email TEXT,
        issued TEXT,
        due TEXT,
        amount REAL NOT NULL,
        status TEXT,
        memo TEXT,
        source_file TEXT
    )
    """)

    # 6. Payments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        payment_date TEXT,
        payer TEXT NOT NULL,
        payer_email TEXT,
        amount REAL NOT NULL,
        method TEXT,
        reference TEXT,
        source_file TEXT
    )
    """)

    # 7. Production Board
    cur.execute("""
    CREATE TABLE IF NOT EXISTS production_board (
        video_id TEXT PRIMARY KEY,
        client TEXT NOT NULL,
        title TEXT,
        editor TEXT,
        stage TEXT,
        notes_on_board TEXT,
        revisions INTEGER DEFAULT 0,
        editor_hours REAL DEFAULT 0.0,
        client_approved_on TEXT,
        shoot_booking TEXT,
        source_file TEXT
    )
    """)

    # 8. Leads
    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        lead_id TEXT PRIMARY KEY,
        created TEXT,
        name TEXT NOT NULL,
        business TEXT,
        email TEXT,
        phone TEXT,
        source TEXT,
        first_reply TEXT,
        status TEXT,
        source_file TEXT
    )
    """)

    # 9. Messages
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg_hash TEXT UNIQUE,
        line_no INTEGER,
        msg_datetime TEXT,
        channel TEXT,
        direction TEXT,
        entity TEXT,
        body TEXT,
        source_file TEXT
    )
    """)

    # 10. Costs & Team
    cur.execute("""
    CREATE TABLE IF NOT EXISTS costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        cost TEXT,
        note TEXT,
        source_file TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        joined TEXT,
        pay TEXT,
        source_file TEXT
    )
    """)

    # 11. Owner Decisions (Durable Persistence)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS owner_decisions (
        action_id TEXT PRIMARY KEY,
        decision_type TEXT NOT NULL,
        status TEXT NOT NULL, -- pending, in_progress, completed, deferred
        owner_notes TEXT,
        updated_at TEXT NOT NULL
    )
    """)

    # 12. Typesafe AI (Jev) Caching & Classifications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jev_cache (
        cache_key TEXT PRIMARY KEY,
        model_version TEXT NOT NULL,
        prompt_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        result_source TEXT DEFAULT 'deterministic_fallback',
        provider_model TEXT DEFAULT 'none',
        app_question_version TEXT DEFAULT 'axeom-intent-v2.0',
        input_hash TEXT DEFAULT ''
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS message_classifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg_id INTEGER,
        msg_hash TEXT,
        predicted_intent TEXT NOT NULL,
        confidence REAL DEFAULT 0.0,
        provider TEXT NOT NULL,
        provider_model TEXT DEFAULT 'none',
        multi_intent INTEGER DEFAULT 0,
        actionable_billing INTEGER DEFAULT 0,
        classified_at TEXT NOT NULL
    )
    """)

    # Ensure initial revision row exists if empty
    cur.execute("SELECT COUNT(*) FROM dataset_revisions")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO dataset_revisions (created_at, source_filename, source_file_hash, summary_json)
        VALUES (?, ?, ?, ?)
        """, (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_init",
            "initial_genesis_hash",
            json.dumps({"description": "Initial system schema migration"})
        ))

    run_migrations(conn)

    conn.commit()
    conn.close()

def run_migrations(conn):
    cur = conn.cursor()
    # Check file_uploads columns
    cur.execute("PRAGMA table_info(file_uploads)")
    existing_cols = {r[1] for r in cur.fetchall()}
    for col in ["added_count", "updated_count", "skipped_count", "rejected_count"]:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE file_uploads ADD COLUMN {col} INTEGER DEFAULT 0")

    # Check messages columns
    cur.execute("PRAGMA table_info(messages)")
    existing_msg_cols = {r[1] for r in cur.fetchall()}
    if "msg_hash" not in existing_msg_cols:
        cur.execute("ALTER TABLE messages ADD COLUMN msg_hash TEXT")

def get_current_revision():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT revision_id, created_at, source_filename FROM dataset_revisions ORDER BY revision_id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return {"revision_id": row["revision_id"], "created_at": row["created_at"], "source": row["source_filename"]}
    return {"revision_id": 1, "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "source": "system"}

def get_recent_uploads(limit=10):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, filename, file_role, row_count, added_count, updated_count, skipped_count, rejected_count, status, details, uploaded_at FROM file_uploads ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def seed_db_if_empty():
    """
    Seeds database from data/ directory using the exact same unified ingest pipeline.
    Ensures identical validation and provenance tracking.
    """
    init_db()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM invoices")
    count = cur.fetchone()[0]
    conn.close()

    if count > 0:
        # Populate canonical clients directory if needed
        _seed_canonical_clients_if_empty()
        return

    # Import via shared ingestion service
    from services.ingest import ingest_file_path

    # Ingest in logical sequence
    seed_files = [
        "bookings.csv",
        "invoices.csv",
        "payments.csv",
        "production_board.csv",
        "leads.csv",
        "messages.txt",
        "costs.csv",
        "team.csv"
    ]

    for fname in seed_files:
        fpath = DATA_DIR / fname
        if fpath.exists():
            ingest_file_path(fpath)

    _seed_canonical_clients_if_empty()

def _seed_canonical_clients_if_empty():
    from services.identity import CANONICAL_CLIENTS, THIRD_PARTY_PAYERS
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM clients")
    if cur.fetchone()[0] == 0:
        for c in CANONICAL_CLIENTS:
            cur.execute("""
            INSERT OR REPLACE INTO clients (id, canonical_name, primary_contact, emails, phones, payer_aliases, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c['id'],
                c['canonical_name'],
                c.get('primary_contact', ''),
                json.dumps(c.get('emails', [])),
                json.dumps(c.get('phones', [])),
                json.dumps(c.get('payer_aliases', [])),
                c.get('status', 'active'),
                c.get('notes', '')
            ))

    cur.execute("SELECT COUNT(*) FROM third_party_payers")
    if cur.fetchone()[0] == 0:
        for p in THIRD_PARTY_PAYERS:
            cur.execute("""
            INSERT OR REPLACE INTO third_party_payers (name, pays_for, aliases, emails, phones, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                p['name'],
                json.dumps(p.get('pays_for', [])),
                json.dumps(p.get('aliases', [])),
                json.dumps(p.get('emails', [])),
                json.dumps(p.get('phones', [])),
                p.get('evidence', '')
            ))

    conn.commit()
    conn.close()
