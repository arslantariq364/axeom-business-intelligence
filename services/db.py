"""
Database abstraction layer for Axeom Studio Operations & Owner OS.
Seamlessly supports Neon PostgreSQL (via DATABASE_URL and Psycopg 3)
with automatic fallback to local SQLite for offline development and testing.
"""

import os
import json
import datetime
from pathlib import Path

# Optional PostgreSQL driver (Psycopg 3)
try:
    import psycopg
    from psycopg.rows import dict_row
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False

import sqlite3

DB_PATH = os.environ.get("AXEOM_DB_PATH", "axeom.db")
DATA_DIR = Path("submission/original_data") if Path("submission/original_data").exists() else Path("data")


def get_database_url():
    """Returns DATABASE_URL from environment or local .env file."""
    if os.environ.get("AXEOM_FORCE_SQLITE") == "1":
        return None
    url = os.environ.get("DATABASE_URL")
    if url == "" or url == "sqlite":
        return None
    if url is None and os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATABASE_URL="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and not val.startswith("#"):
                            return val
        except Exception:
            pass
    return url


def is_postgres():
    """Returns True if DATABASE_URL is configured for PostgreSQL."""
    url = get_database_url()
    return bool(url and (url.startswith("postgresql://") or url.startswith("postgres://")))


def normalize_database_url(url: str) -> str:
    """Ensures PostgreSQL URL uses postgresql:// scheme and required SSL for Neon."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if "sslmode=" not in url and "localhost" not in url and "127.0.0.1" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


def qmark_to_pyformat(sql: str) -> str:
    """Translates SQLite '?' placeholders to PostgreSQL '%s' outside string literals."""
    tokens = []
    in_single_quote = False
    in_double_quote = False
    i = 0
    while i < len(sql):
        c = sql[i]
        if c == "'" and not in_double_quote:
            if i + 1 < len(sql) and sql[i+1] == "'":
                tokens.append("''")
                i += 2
                continue
            in_single_quote = not in_single_quote
            tokens.append(c)
        elif c == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            tokens.append(c)
        elif c == '?' and not in_single_quote and not in_double_quote:
            tokens.append('%s')
        else:
            tokens.append(c)
        i += 1
    return "".join(tokens)


class PostgresRow(dict):
    """
    Dual-access row dictionary matching sqlite3.Row behavior:
    supports column name lookup (row['amount']) and index lookup (row[0]).
    """
    def __init__(self, data_dict, tuple_values=None):
        super().__init__(data_dict)
        self._tuple = tuple_values if tuple_values is not None else tuple(data_dict.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tuple[key]
        return super().__getitem__(key)


class PostgresCursorWrapper:
    """Cursor wrapper that translates '?' placeholders and PRAGMAs to PostgreSQL."""
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        clean_query = query.strip()
        upper_query = clean_query.upper()

        # Ignore SQLite-specific commands that are no-ops in PostgreSQL
        if upper_query.startswith("PRAGMA"):
            return self
        if upper_query == "BEGIN TRANSACTION":
            return self

        pg_query = qmark_to_pyformat(clean_query)
        if params is not None:
            self._cursor.execute(pg_query, params)
        else:
            self._cursor.execute(pg_query)
        return self

    def executemany(self, query, seq_of_params):
        pg_query = qmark_to_pyformat(query)
        self._cursor.executemany(pg_query, seq_of_params)
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return PostgresRow(row, tuple(row.values()))

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [PostgresRow(r, tuple(r.values())) for r in rows]

    def fetchmany(self, size=None):
        rows = self._cursor.fetchmany(size)
        return [PostgresRow(r, tuple(r.values())) for r in rows]

    def close(self):
        self._cursor.close()

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    @property
    def lastrowid(self):
        return getattr(self, "_lastrowid", None)


class PostgresConnectionWrapper:
    """Connection wrapper ensuring transaction and cursor compatibility."""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def execute(self, query, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()


def get_db():
    """
    Returns active database connection:
    - Neon PostgreSQL connection if DATABASE_URL is set
    - SQLite connection if DATABASE_URL is unset
    """
    database_url = get_database_url()
    if database_url:
        if not PSYCOPG_AVAILABLE:
            raise RuntimeError("psycopg is required when DATABASE_URL is configured. Run: pip install 'psycopg[binary]'")
        dsn = normalize_database_url(database_url)
        raw_conn = psycopg.connect(dsn, row_factory=dict_row)
        return PostgresConnectionWrapper(raw_conn)

    # SQLite Local Connection
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


_DB_INITIALIZED = False

def init_db(force=False):
    """Idempotently initializes database tables and runs versioned migrations."""
    global _DB_INITIALIZED
    if is_postgres():
        if _DB_INITIALIZED and not force:
            return
        _init_db_postgres()
        _DB_INITIALIZED = True
    else:
        _init_db_sqlite()


def _init_db_postgres():
    conn = get_db()
    cur = conn.cursor()

    # 1. Dataset Revisions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dataset_revisions (
        revision_id SERIAL PRIMARY KEY,
        created_at VARCHAR(64) NOT NULL,
        source_filename VARCHAR(255),
        source_file_hash VARCHAR(64),
        summary_json TEXT
    );
    """)

    # 2. File Uploads Audit
    cur.execute("""
    CREATE TABLE IF NOT EXISTS file_uploads (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        file_role VARCHAR(64) NOT NULL,
        sha256_hash VARCHAR(64) UNIQUE,
        row_count INTEGER DEFAULT 0,
        added_count INTEGER DEFAULT 0,
        updated_count INTEGER DEFAULT 0,
        skipped_count INTEGER DEFAULT 0,
        rejected_count INTEGER DEFAULT 0,
        status VARCHAR(32) NOT NULL,
        details TEXT,
        uploaded_at VARCHAR(64) NOT NULL
    );
    """)

    # Durable non-business lifecycle marker. Not removed by empty-workspace reset.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key VARCHAR(64) PRIMARY KEY,
        value TEXT
    );
    """)

    # 3. Canonical Clients & Payers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id VARCHAR(64) PRIMARY KEY,
        canonical_name VARCHAR(255) NOT NULL,
        primary_contact VARCHAR(255),
        emails TEXT,
        phones TEXT,
        payer_aliases TEXT,
        status VARCHAR(64),
        notes TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS third_party_payers (
        name VARCHAR(255) PRIMARY KEY,
        pays_for TEXT NOT NULL,
        aliases TEXT,
        emails TEXT,
        phones TEXT,
        evidence TEXT
    );
    """)

    # 4. Bookings
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id VARCHAR(64) PRIMARY KEY,
        booking_date VARCHAR(64),
        client_name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        service VARCHAR(255),
        status VARCHAR(64),
        price NUMERIC(12, 2) DEFAULT 0.0,
        source_file VARCHAR(255)
    );
    """)

    # 5. Invoices
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_no VARCHAR(64) PRIMARY KEY,
        bill_to VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        issued VARCHAR(64),
        due VARCHAR(64),
        amount NUMERIC(12, 2) NOT NULL,
        status VARCHAR(64),
        memo TEXT,
        source_file VARCHAR(255)
    );
    """)

    # 6. Payments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id VARCHAR(64) PRIMARY KEY,
        payment_date VARCHAR(64),
        payer VARCHAR(255) NOT NULL,
        payer_email VARCHAR(255),
        amount NUMERIC(12, 2) NOT NULL,
        method VARCHAR(64),
        reference VARCHAR(255),
        source_file VARCHAR(255)
    );
    """)

    # 7. Production Board
    cur.execute("""
    CREATE TABLE IF NOT EXISTS production_board (
        video_id VARCHAR(64) PRIMARY KEY,
        client VARCHAR(255) NOT NULL,
        title VARCHAR(255),
        editor VARCHAR(255),
        stage VARCHAR(64),
        notes_on_board TEXT,
        revisions INTEGER DEFAULT 0,
        editor_hours NUMERIC(8, 2) DEFAULT 0.0,
        client_approved_on VARCHAR(64),
        shoot_booking VARCHAR(64),
        source_file VARCHAR(255)
    );
    """)

    # 8. Leads
    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        lead_id VARCHAR(64) PRIMARY KEY,
        created VARCHAR(64),
        name VARCHAR(255) NOT NULL,
        business VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(64),
        source VARCHAR(64),
        first_reply VARCHAR(64),
        status VARCHAR(64),
        source_file VARCHAR(255)
    );
    """)

    # 9. Messages
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        msg_hash VARCHAR(64) UNIQUE,
        line_no INTEGER,
        msg_datetime VARCHAR(64),
        channel VARCHAR(64),
        direction VARCHAR(64),
        entity VARCHAR(255),
        body TEXT,
        source_file VARCHAR(255)
    );
    """)

    # 10. Costs & Team
    cur.execute("""
    CREATE TABLE IF NOT EXISTS costs (
        id SERIAL PRIMARY KEY,
        item VARCHAR(255),
        cost VARCHAR(64),
        note TEXT,
        source_file VARCHAR(255)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS team (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        role VARCHAR(255),
        joined VARCHAR(64),
        pay VARCHAR(64),
        source_file VARCHAR(255)
    );
    """)

    # 11. Owner Decisions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS owner_decisions (
        action_id VARCHAR(64) PRIMARY KEY,
        decision_type VARCHAR(64) NOT NULL,
        status VARCHAR(64) NOT NULL,
        owner_notes TEXT,
        updated_at VARCHAR(64) NOT NULL
    );
    """)

    # 12. Typesafe AI (Jev) Caching & Classifications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jev_cache (
        cache_key VARCHAR(255) PRIMARY KEY,
        model_version VARCHAR(64) NOT NULL,
        prompt_hash VARCHAR(64) NOT NULL,
        response_json TEXT NOT NULL,
        created_at VARCHAR(64) NOT NULL,
        result_source VARCHAR(64) DEFAULT 'deterministic_fallback',
        provider_model VARCHAR(64) DEFAULT 'none',
        app_question_version VARCHAR(64) DEFAULT 'axeom-intent-v2.0',
        input_hash VARCHAR(64) DEFAULT ''
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS message_classifications (
        id SERIAL PRIMARY KEY,
        msg_id INTEGER,
        msg_hash VARCHAR(64),
        predicted_intent VARCHAR(64) NOT NULL,
        confidence NUMERIC(6, 4) DEFAULT 0.0,
        provider VARCHAR(64) NOT NULL,
        provider_model VARCHAR(64) DEFAULT 'none',
        multi_intent INTEGER DEFAULT 0,
        actionable_billing INTEGER DEFAULT 0,
        classified_at VARCHAR(64) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id SERIAL PRIMARY KEY,
        timestamp VARCHAR(64) NOT NULL,
        action_type VARCHAR(64) NOT NULL,
        target_table VARCHAR(64) NOT NULL,
        record_id VARCHAR(255),
        details TEXT,
        performed_by VARCHAR(64) DEFAULT 'owner'
    );
    """)

    # Check dataset revisions count
    cur.execute("SELECT COUNT(*) FROM dataset_revisions")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO dataset_revisions (created_at, source_filename, source_file_hash, summary_json)
        VALUES (?, ?, ?, ?)
        """, (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_init_pg",
            "initial_genesis_hash",
            json.dumps({"description": "Initial PostgreSQL schema migration"})
        ))

    run_migrations(conn)

    conn.commit()
    conn.close()


def _init_db_sqlite():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dataset_revisions (
        revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        source_filename TEXT,
        source_file_hash TEXT,
        summary_json TEXT
    )
    """)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS owner_decisions (
        action_id TEXT PRIMARY KEY,
        decision_type TEXT NOT NULL,
        status TEXT NOT NULL,
        owner_notes TEXT,
        updated_at TEXT NOT NULL
    )
    """)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action_type TEXT NOT NULL,
        target_table TEXT NOT NULL,
        record_id TEXT,
        details TEXT,
        performed_by TEXT DEFAULT 'owner'
    )
    """)

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
    """Runs column migrations safely depending on active database dialect."""
    cur = conn.cursor()
    tables_to_migrate = ["clients", "leads", "invoices", "payments", "bookings", "messages", "production_board"]

    if is_postgres():
        for t in tables_to_migrate:
            try:
                cur.execute(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS is_archived INTEGER DEFAULT 0")
                cur.execute(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS deleted_at VARCHAR(64)")
            except Exception:
                pass
        try:
            cur.execute("ALTER TABLE file_uploads ADD COLUMN IF NOT EXISTS is_reverted INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE file_uploads ADD COLUMN IF NOT EXISTS reverted_at VARCHAR(64)")
        except Exception:
            pass
        return

    # SQLite migrations
    cur.execute("PRAGMA table_info(file_uploads)")
    existing_cols = {r[1] for r in cur.fetchall()}
    for col in ["added_count", "updated_count", "skipped_count", "rejected_count", "is_reverted"]:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE file_uploads ADD COLUMN {col} INTEGER DEFAULT 0")
    if "reverted_at" not in existing_cols:
        cur.execute("ALTER TABLE file_uploads ADD COLUMN reverted_at TEXT")

    cur.execute("PRAGMA table_info(messages)")
    existing_msg_cols = {r[1] for r in cur.fetchall()}
    if "msg_hash" not in existing_msg_cols:
        cur.execute("ALTER TABLE messages ADD COLUMN msg_hash TEXT")

    for t in tables_to_migrate:
        cur.execute(f"PRAGMA table_info({t})")
        cols = {r[1] for r in cur.fetchall()}
        if "is_archived" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN is_archived INTEGER DEFAULT 0")
        if "deleted_at" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN deleted_at TEXT")


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


def is_dataset_cleared():
    """Persistent empty-workspace marker: prevents implicit challenge-data re-seeding."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM app_settings WHERE key = ?", ("dataset_cleared",))
        row = cur.fetchone()
        return bool(row and row["value"] == "1")
    except Exception:
        # During first-time initialization app_settings may not exist yet.
        return False
    finally:
        conn.close()


def seed_db_if_empty():
    """
    Seeds database from DATA_DIR directory using the exact same unified ingest pipeline.
    Ensures identical validation and provenance tracking across SQLite and PostgreSQL.
    """
    init_db()
    if is_dataset_cleared():
        return  # A consciously cleared database must stay empty across restarts.
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM invoices")
    count = cur.fetchone()[0]
    conn.close()

    if count > 0:
        _seed_canonical_clients_if_empty()
        return

    from services.ingest import ingest_file_path

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
            INSERT INTO clients (id, canonical_name, primary_contact, emails, phones, payer_aliases, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                canonical_name = excluded.canonical_name,
                primary_contact = excluded.primary_contact,
                emails = excluded.emails,
                phones = excluded.phones,
                payer_aliases = excluded.payer_aliases,
                status = excluded.status,
                notes = excluded.notes
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
            INSERT INTO third_party_payers (name, pays_for, aliases, emails, phones, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                pays_for = excluded.pays_for,
                aliases = excluded.aliases,
                emails = excluded.emails,
                phones = excluded.phones,
                evidence = excluded.evidence
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
