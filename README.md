# Axeom — Business Intelligence & Operations Dashboard

[![Python](https://img.shields.io/badge/Python-3.11%2B%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://palletsprojects.com/p/flask/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Serverless-00e699.svg)](https://neon.tech/)
[![Psycopg](https://img.shields.io/badge/Driver-Psycopg%203-blueviolet.svg)](https://www.psycopg.org/)
[![Tests](https://img.shields.io/badge/Tests-80%2F80%20Passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Deployment-Vercel%20Serverless-black.svg)](https://vercel.com/)

A modern, high-reliability Business Intelligence (BI) and Operations Operating System designed for media production studios, creative agencies, and high-touch service businesses. 

Axeom ingests fragmented operational records—invoices, bank deposits, production boards, inbound inquiries, and multi-channel client communications—and reconciles them into actionable financial clarity and owner-directed priority actions.

### 🌐 Official Project Deliverables
- **Live Production App**: [https://axeom-business-intelligence.vercel.app](https://axeom-business-intelligence.vercel.app)
- **Demonstration Video**: [Watch 5-Minute HD Walkthrough (Google Drive)](https://drive.google.com/file/d/10gawKb1ZWhdLixC-LrnjNLXrgM5K-m9D/view?usp=sharing)
- **Source Code Repository**: [https://github.com/arslantariq364/axeom-business-intelligence](https://github.com/arslantariq364/axeom-business-intelligence)
- **Pack ID**: `01` | **Candidate**: Arslan Tariq (`tsa6648@gmail.com`)

---

## 📸 Dashboard Overview

| Desktop Command Center | Responsive Mobile (390x844) |
| :---: | :---: |
| ![Desktop Dashboard](docs/assets/dashboard_overview.png) | ![Mobile Dashboard](docs/assets/mobile_dashboard.png) |

| Financial Reconciliation & Overdue Balances | Canonical Client Directory & Health |
| :---: | :---: |
| ![Money Reconciliation](docs/assets/money_reconciliation.png) | ![Client Directory](docs/assets/client_directory.png) |

---

## 1. Project Overview & Problem Statement

Growing media production studios frequently face operational blind spots caused by disconnected software tools:
- **Billing Tool Disconnects:** Automated accounting systems (e.g., QuickBooks, Stripe) report false payment statuses due to unallocated deposits or bank clearing lag.
- **Unbilled Production Work:** Shoots completed on the studio floor often sit unbilled for months because production boards are separated from invoicing.
- **Lost Client Requests:** Critical revision requests sent via ad-hoc Slack messages or email threads get lost in communication silos, leading to client friction and churn.
- **Unaddressed Inbound Leads:** Inquiries arrive through web forms or referral channels but go unanswered due to lack of a centralized tracking pipeline.
- **Identity Ambiguity:** Clients book under colloquial abbreviations, personal names, or pay through third-party agencies (e.g., marketing parent firms).

**Axeom solves this by acting as the Studio Owner's Operating System:** an automated, deterministic reconciliation engine that ingests raw operational files, resolves identities, audits finances, detects lost requests, and presents a curated **Monday Top 3** list of high-impact actions.

---

## 2. Key Features

- **Entity & Identity Resolution:** Maps noisy aliases, phone numbers, email domains, and third-party agency payers (e.g., agencies paying on behalf of distinct client accounts) to canonical business profiles without accidental entity collapsing.
- **Deterministic Financial Reconciliation:** 
  - Overdue debt tracking with exact aging calculations.
  - Studio liabilities ("We Owe") tracking cancellation refunds and customer overpayment credits.
  - Detection of unbilled bookings with missing invoices.
  - Direct identification of accounting software discrepancies against actual transaction logs.
- **Lost Request & Communication Audit:** Scans cross-channel message dumps (Email, Slack, SMS) to flag edit requests that never made it onto active production boards.
- **Inbound Lead Tracking:** Automatically measures lead response latency and flags inquiries that have gone unanswered.
- **Owner Action Protocol (Safety-First):** Recommends pre-composed communication scripts (phone call scripts, email drafts) and enables the studio owner to Approve, Reject, or Defer with custom notes. **Never sends automated customer messages or executes financial mutations without explicit human approval.**
- **Mobile-First UX (The Axeom 10-Second Test):** Specifically engineered so a studio owner opening the dashboard on a smartphone can identify their most urgent priority, review the backing evidence, and access an action script within 10 seconds.
- **Robust Ingestion Engine:** Accepts CSV and plain text dumps with automatic schema detection, SHA-256 duplicate file idempotency, header validation, atomic transactional staging, and rollback safety.

---

## 3. Technology Stack

- **Backend:** Python 3.11+ / 3.14, Flask 3.1 (WSGI application)
- **Database Architecture:** Neon Serverless PostgreSQL (production) with dual-engine fallback to SQLite3 (offline development & isolated testing)
- **Database Driver:** Psycopg 3 (`psycopg[binary]>=3.2.0`, `psycopg-pool`)
- **Frontend Architecture:** Vanilla HTML5, Modern CSS3 Custom Properties (Design System tokens, glassmorphism, responsive dock navigation), Vanilla ES6 JavaScript
- **Testing & Quality Assurance:** Pytest (Unit & Integration), Playwright / Chrome Automation (End-to-End browser verification)
- **Production Hosting:** Vercel Serverless Functions (`@vercel/python` runtime)

---

## 4. System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["User Interface & Devices"]
        Mobile["Mobile Browser\n(390x844 Viewport)"]
        Desktop["Desktop Browser\n(1366x768+ Viewport)"]
    end

    subgraph HostingLayer["Vercel Serverless Edge"]
        VercelRoute["Vercel Routing & Rewrites\n(vercel.json)"]
        WSGI["Serverless WSGI Handler\n(api/index.py)"]
        Flask["Flask Application Core\n(app.py)"]
    end

    subgraph ServiceLayer["Business Logic & Intelligence Engines"]
        Ingest["Ingestion & Validation Engine\n(services/ingest.py)"]
        Identity["Entity Resolution Service\n(services/identity.py)"]
        Finance["Financial Reconciliation Engine\n(services/finance.py)"]
        Requests["Requests & Leads Auditor\n(services/requests.py)"]
        Analytics["Priority & Retention Analytics\n(services/analytics.py)"]
        Decisions["Owner Decisions Persistence\n(services/decisions.py)"]
        JevNLP["Intent Classifier & Fallback\n(services/jev.py)"]
    end

    subgraph StorageLayer["Data & Persistence Tier"]
        NeonPG[("Neon Serverless PostgreSQL\n(DATABASE_URL via Psycopg 3)")]
        SQLiteFallback[("Local SQLite Database\n(axeom.db - Offline Dev)")]
    end

    Mobile --> VercelRoute
    Desktop --> VercelRoute
    VercelRoute --> WSGI
    WSGI --> Flask

    Flask --> Ingest
    Flask --> Identity
    Flask --> Finance
    Flask --> Requests
    Flask --> Analytics
    Flask --> Decisions
    Flask --> JevNLP

    Ingest --> NeonPG
    Finance --> NeonPG
    Decisions --> NeonPG
    Requests --> NeonPG
    Identity --> NeonPG
    JevNLP --> NeonPG

    NeonPG -.->|Local Dev Fallback| SQLiteFallback
```

---

## 5. How the System Works

1. **Data Ingestion (`POST /api/upload`):**
   - Files uploaded via the browser or API are received in-memory (up to 16MB).
   - The file's SHA-256 hash is computed. If an identical file was previously ingested, processing returns immediately with a duplicate acknowledgement without corrupting records.
   - Headers and data types are validated against supported schemas (`bookings`, `invoices`, `payments`, `production_board`, `leads`, `messages`, `costs`, `team`).
2. **Entity Resolution:**
   - Client records are cross-referenced across bookings and invoices using canonical identity records and alias registries.
   - Third-party agency payers (e.g. billing agencies paying for multiple clinics) are recognized as distinct payers rather than conflated with the underlying service client.
3. **Deterministic Financial Audit:**
   - Overdue invoices are reconciled against actual bank payment records.
   - Partial payments are matched and subtracted from outstanding balances.
   - Client overpayments and shoot cancellation credits are audited as liabilities ("We Owe").
   - Completed bookings lacking corresponding invoices are flagged as unbilled revenue.
4. **Owner Priority Dashboard:**
   - Retention risks and delinquent balances are scored.
   - The highest priority item is elevated to the **Hero Action Card** on the owner's dashboard with backing evidence links and customizable phone/email scripts.
   - Owner decisions (Approve, Reject, Defer) are durably recorded in the database and persist across reboots.

---

## 6. Local Installation & Setup

### Prerequisites
- Python 3.11+ (Python 3.14 tested and supported)
- Google Chrome (optional, for running browser E2E tests)
- Git

### Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arslan-tariq/axeom-business-intelligence.git
   cd axeom-business-intelligence
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the local application:**
   ```bash
   python3 app.py
   ```
   Open `http://127.0.0.1:5000` (or `PORT=5050 python3 app.py`) in your browser.

---

## 7. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `DATABASE_URL` | No (Production) | *Unset (uses SQLite)* | PostgreSQL connection string (Neon pooled endpoint recommended). |
| `AXEOM_DB_PATH` | No | `axeom.db` | File path for local SQLite database fallback. |
| `PORT` | No | `5000` | Port for local Flask web server. |
| `TYPESAFE_API_KEY`| No | *Unset* | Optional API key for live Jev System One NLP classification. |
| `LIVE_LINK` | No | *Unset* | Public URL override for dashboard export routines. |

---

## 8. Database Migration to Neon PostgreSQL

To migrate your local SQLite database to Neon PostgreSQL:

1. Obtain your Neon database connection string from the [Neon Console](https://console.neon.tech).
2. Set `DATABASE_URL` in your environment:
   ```bash
   export DATABASE_URL="postgresql://neondb_owner:password@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
   ```
3. Run the automated migration and audit script:
   ```bash
   python3 scripts/migrate_to_postgres.py
   ```
   The migration script will:
   - Create all tables and indexes idempotently.
   - Transfer all records with conflict handling.
   - Synchronize all PostgreSQL `SERIAL` sequences.
   - Run an independent financial invariant audit directly against Neon.

---

## 9. Running Tests

The test suite covers unit tests, service reconciliation, file upload idempotency, responsive layouts, and browser end-to-end interactions.

```bash
# Run all Python unit and integration tests (60 tests)
python3 -m pytest tests/ -v

# Run browser automated verification (Playwright / Chrome)
node tests/qa_browser_e2e.js

# Run browser real file upload end-to-end suite (16 tests)
node tests/qa_real_upload_e2e.js
```

---

## 10. Deployment (Vercel & Neon)

Axeom is configured out-of-the-box for zero-configuration serverless deployment on Vercel:

1. **Push your repository to GitHub.**
2. **Import the repository into Vercel:**
   - Framework Preset: **Other** (Root directory: `.`)
   - Build Command: *(Leave blank)*
   - Output Directory: *(Leave blank)*
3. **Configure Environment Variables in Vercel:**
   - `DATABASE_URL`: Your Neon pooled connection string.
4. **Deploy!**
   Vercel will detect `api/index.py` and `vercel.json`, automatically install dependencies from `requirements.txt`, and serve the web application.

---

## 11. AI Integration & Transparency (Jev Message Classification)

Axeom includes an optional intent classifier designed to analyze unstructured client messages and extract billing-actionable requests:
- **Offline Deterministic Fallback Engine:** A high-precision regex and semantic pattern classifier built into [`services/jev.py`](services/jev.py). It operates entirely offline with zero external network dependencies and achieved **96.0% accuracy** on the 25-sample held-out Axeom benchmark.
- **Live Typesafe AI (Jev) System One API:** Supported when `TYPESAFE_API_KEY` is provided. If the key is omitted or external network calls fail, the system transparently logs the fallback state without crashing or falsifying live responses.

---

## 12. Security & Operational Safety

- **Public Mobile-Accessible Access:** Engineered to satisfy zero-friction mobile demonstration requirements without mandatory logins.
- **Parameterization:** All queries use parameterized SQL (`%s` in PostgreSQL / `?` in SQLite) to prevent SQL injection vulnerabilities.
- **Defensive Headers:** Automatically serves `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and strict referrer policies.
- **Read-Only Serverless Resilience:** File uploads operate fully in-memory with `/tmp` storage fallbacks for temporary files, preventing read-only filesystem exceptions on Vercel.
- **Safety Protocol:** Outbound messaging is draft-only; financial transactions require manual human execution in external accounting tools.

---

## 13. Future Roadmap

- [ ] Role-Based Access Control (RBAC) with OAuth2 / SSO for multi-user production studio environments.
- [ ] Asynchronous background job processing (Celery / Redis) for multi-gigabyte batch uploads.
- [ ] Bi-directional webhooks with Stripe, QuickBooks, and Slack for real-time transaction streaming.
- [ ] Automated PDF statement generation for client credit and overdue reminders.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
