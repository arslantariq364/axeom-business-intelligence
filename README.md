# Axeom Studio Operations & Owner OS

A lightweight, mobile-first operations and financial OS built for **Axeom Studio** owner Zaid. Built with a verified Python backend, durable SQLite persistence, and a high-contrast Scandinavian modern visual language adapted from **Conneq CRM** (light sage canvas, off-white cards, dark charcoal typography, and bright lime accent).

* **Challenge Pack ID**: `"01"`
* **Fixed Reference As-Of Date**: `2026-10-06`
* **Zero Discrepancy Invariant**: Both the web dashboard (`/api/state`) and `answers_working.json` consume the exact same underlying service calculations.

---

## 1. Quickstart & Local Run Commands (Ubuntu / Debian)

### Prerequisites
* Python 3.10+ (tested on Python 3.14.6)
* `sqlite3`
* `curl` (for health and API checks)

### Exact Terminal Commands

```bash
# 1. Clone or navigate to the project directory
cd "/home/arslan-tariq/Downloads/Axeom Challenge - Pack 01"

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
cp .env.example .env

# 5. Run automated test suite
python3 -m pytest tests/ -v

# 6. Start the local application server
python app.py
```

The application will start on **`http://127.0.0.1:5050`** (or the port defined in `PORT`).

---

## 2. Directory Structure & Module Responsibilities

```text
├── app.py                      # Flask REST router, API endpoints, upload handler
├── axeom.db                    # Durable SQLite database (WAL mode, foreign keys ON)
├── answers.json                # Original submission template (strictly preserved)
├── answers_working.json        # Recomputed working answers matching 100% invariant tests
├── requirements.txt            # Pinned dependencies with explanations
├── Procfile                    # Deployment entry point for Render / cloud hosting
├── .env.example                # Placeholder secrets documentation
├── .gitignore                  # Git exclusions for venv, caches, and secrets
│
├── data/                       # Authoritative raw challenge pack data (8 files, 1,112 rows)
│   ├── bookings.csv            # 175 client shoot bookings
│   ├── costs.csv               # Studio and contractor cost schedules
│   ├── invoices.csv            # 152 billing invoices
│   ├── leads.csv               # 99 inbound marketing inquiries
│   ├── messages.txt            # 208 multi-channel communications (WhatsApp, Email, etc.)
│   ├── payments.csv            # 131 bank transactions and cash receipts
│   ├── production_board.csv    # 333 video editing deliverables
│   └── team.csv                # Editor roster and hourly pay
│
├── services/                   # Modular business logic and analytical services
│   ├── db.py                   # SQLite schema, migrations, revisions, seeding
│   ├── ingest.py               # Unified idempotent file ingestion pipeline
│   ├── identity.py             # 29 canonical clients & third-party payer mapping
│   ├── finance.py              # Financial reconciliation ($9,250 overdue, $2,400 we owe, $2,950 unbilled)
│   ├── requests.py             # 33 lost edit requests & 22 unreplied leads detection
│   ├── analytics.py            # Churn risk (Patel Ins), marketing economics, top 3 actions
│   ├── decisions.py            # Durable owner decision persistence
│   ├── history.py              # Deep-dive client dossier service
│   ├── evidence.py             # Evidence provenance trails & real-time search
│   └── export.py               # Template-compliant answers.json generator
│
├── static/                     # Frontend assets
│   ├── css/conneq.css          # Conneq CRM design system (light sage & lime theme)
│   └── js/app.js               # Client controller (SPA navigation, modals, live search)
│
├── templates/                  # Frontend markup
│   └── index.html              # Mobile-first owner dashboard SPA
│
├── tests/                      # Automated test suite
│   ├── conftest.py             # Pytest configuration and sys.path setup
│   └── test_import.py          # 8-step import idempotency, validation & persistence tests
│
└── docs/                       # Specifications, audit logs, and master guide
    ├── master-guide.html       # Self-contained visual design guide & architecture
    ├── design-specification.md # UI/UX design tokens, typography, and responsive rules
    ├── data_inventory.md       # Cryptographic hashes and data quality audit
    ├── identity_review.md      # Canonical identity resolution proofs
    ├── evidence.md             # Mathematical reconciliations and calculations
    └── progress.md             # 72-hour milestone schedule and critical path
```

---

## 3. Dependency Explanation

All production dependencies are pinned in `requirements.txt`:

| Package | Pinned Version | Purpose & Architectural Rationale |
| :--- | :--- | :--- |
| **`Flask`** | `3.1.3` | Lightweight Python WSGI microframework. Fast startup (<100ms), zero dependency bloat, native JSON support. |
| **`Werkzeug`** | `3.1.6` | Underpins Flask for secure file upload parsing and HTTP routing. |
| **`requests`** | `2.34.2` | Clean HTTP library utilized for end-to-end integration and API verification. |
| **`pytest`** | `9.0.3` | Automated testing runner for database migrations, deduplication, and pipeline tests. |
| *(Optional)* **`gunicorn`** | `23.0.0` | Standard production WSGI server for UNIX/Linux containerized deployment. |

---

## 4. Ingestion Engine & Storage Foundation (`services/ingest.py`)

A single, unified pipeline handles both the initial pack seeding and ongoing "Add New Files" uploads:

1. **Automatic Schema Sniffing**: Inspects column headers to identify file role (`invoices`, `payments`, `bookings`, `production_board`, `leads`, `messages`, `costs`, `team`) regardless of file renaming.
2. **Defensive Validation**: Rejects files with duplicate column headers, missing required fields, or corrupt encodings (handles UTF-8, UTF-8-BOM, Latin-1).
3. **Idempotency & Deduplication**:
   * **File Level**: Calculates SHA-256 hash. If identical bytes were previously imported, returns an immediate cached summary (`skipped = N, added = 0`).
   * **Record Level**: Checks stable primary keys. Identical records are `skipped`; modified records are `updated`; new records are `added`.
   * **Transactions**: Never collapses legitimate identical transactions (e.g., identical payments of $900 with distinct payment IDs).
4. **Staged Database Transactions**: File imports execute within a database transaction (`BEGIN...COMMIT`). If any fatal validation error occurs, changes roll back cleanly, preventing database corruption.
5. **Dataset Revision Tracking**: Every data-mutating commit increments the global `revision_id` in `dataset_revisions`.

---

## 5. Deployment Feasibility

Axeom is intentionally engineered with a minimal footprint:
* **Memory Footprint**: < 45 MB RAM in idle; < 80 MB under full recomputation.
* **Storage Footprint**: < 1 MB SQLite database file.
* **No Database Cluster Required**: Runs on standard Linux filesystems or persistent volumes on Render, PythonAnywhere, Railway, or Fly.io.
* **Public URL Readiness**: Supports container port binding via `PORT` environment variable and `Procfile`.

---

## 6. Verification & Automated Testing

To run the complete automated test suite:
```bash
python3 -m pytest tests/ -v
```

All 8 integration tests verify:
* Content-based role detection on renamed files.
* Unified pipeline ingestion of all 8 original datasets.
* Duplicate file idempotency (0 duplicates inserted).
* In-place row updates on changed records.
* Database rollback on malformed input.
* Duplicate header detection and rejection.
* Non-collapsing of identical-value transactions.
* Persistence and dataset revision incrementing across restarts.
