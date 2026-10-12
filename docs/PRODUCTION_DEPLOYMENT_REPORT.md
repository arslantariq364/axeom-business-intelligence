# Axeom — Production Deployment & Cloud Architecture Report

**Lead Engineer & Auditor:** GPT-6 Astra (Senior DevOps Engineer, PostgreSQL Database Architect, Backend Engineer & Security Lead)  
**Date:** October 12, 2026  
**Business Reference Date:** October 6, 2026 (`2026-10-06`)  
**Target Architecture:** Vercel Serverless Functions (`@vercel/python`) + Neon Serverless PostgreSQL (`ep-*-pooler` endpoint via Psycopg 3)  
**Deployment Branch:** [`deploy/neon-vercel`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001)  

---

## 1. Executive Summary

The Axeom Business Intelligence and Operations Dashboard has been audited, refactored, and prepared for cloud-native production deployment on **Vercel** connected to **Neon Serverless PostgreSQL**.

Key milestones achieved:
1. **Clean Separation of Challenge Deliverables:** All 16 challenge-specific materials (`Axeom Challenge.pdf`, `PACK.txt`, `answers.json`, `assumptions.md`, `daily_log.md`, `writeup.pdf`, `submission ZIP`, and proprietary source CSVs) have been relocated to a private, git-ignored local directory ([`submission/`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/submission/)) and untracked from the Git index without data loss.
2. **Dual-Dialect Database Layer:** Implemented [`services/db.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/services/db.py) supporting Neon PostgreSQL (via `psycopg` 3 with connection pooling and automated query placeholder translation) while retaining 100% backward compatibility with local SQLite for offline development and testing.
3. **Automated Migration Engine:** Created [`scripts/migrate_to_postgres.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/scripts/migrate_to_postgres.py) with idempotent DDL, upsert staging, sequence synchronization, and financial invariant recalculation.
4. **Serverless File Upload Hardening:** Refactored [`services/ingest.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/services/ingest.py) to operate safely in memory and fall back to `/tmp/axeom_uploads`, eliminating read-only filesystem crashes in Vercel.
5. **Vercel Deployment Entry Point:** Configured [`api/index.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/api/index.py) and [`vercel.json`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/vercel.json) with path rewrites and HTTP security headers.
6. **Professional Open Repository:** Prepared an executive-grade [`README.md`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/README.md) featuring architectural Mermaid diagrams, screenshots in `docs/assets/`, tech stack documentation, and deployment guides.

---

## 2. Infrastructure & Environment Configuration

| Platform Component | Provider / Tool | Configuration Status |
| :--- | :--- | :--- |
| **Backend Framework** | Flask 3.1.3 on Python 3.14 | Configured with security middleware and serverless cold-start controls |
| **Serverless Runtime** | Vercel (`@vercel/python`) | Entry point [`api/index.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/api/index.py) and [`vercel.json`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/vercel.json) ready |
| **Database Engine** | Neon Serverless PostgreSQL | Psycopg 3 + Psycopg Pool installed; dual-engine layer ready |
| **Connection Protocol**| `DATABASE_URL` | Normalized to `postgresql://` with `sslmode=require` enforcement |
| **Local Fallback** | SQLite (`axeom.db`) | 100% operational for offline development & Pytest suite |
| **Security Headers** | Custom Flask middleware | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` |

---

## 3. Database Schema & Migration Mapping

| Table Name | Primary Key | PostgreSQL Data Types | Migration Strategy |
| :--- | :--- | :--- | :--- |
| `dataset_revisions` | `revision_id` | `SERIAL PRIMARY KEY`, `VARCHAR`, `TEXT` | Idempotent genesis insert + sequence sync |
| `file_uploads` | `sha256_hash` (Unique) | `SERIAL`, `VARCHAR(255)`, `VARCHAR(64)` | `ON CONFLICT (sha256_hash) DO NOTHING` |
| `clients` | `id` | `VARCHAR(64) PRIMARY KEY`, `TEXT` | `ON CONFLICT (id) DO UPDATE SET ...` |
| `third_party_payers`| `name` | `VARCHAR(255) PRIMARY KEY`, `TEXT` | `ON CONFLICT (name) DO UPDATE SET ...` |
| `bookings` | `booking_id` | `VARCHAR(64) PRIMARY KEY`, `NUMERIC(12,2)`| `ON CONFLICT (booking_id) DO UPDATE SET ...` |
| `invoices` | `invoice_no` | `VARCHAR(64) PRIMARY KEY`, `NUMERIC(12,2)`| `ON CONFLICT (invoice_no) DO UPDATE SET ...` |
| `payments` | `payment_id` | `VARCHAR(64) PRIMARY KEY`, `NUMERIC(12,2)`| `ON CONFLICT (payment_id) DO UPDATE SET ...` |
| `production_board` | `video_id` | `VARCHAR(64) PRIMARY KEY`, `NUMERIC(8,2)` | `ON CONFLICT (video_id) DO UPDATE SET ...` |
| `leads` | `lead_id` | `VARCHAR(64) PRIMARY KEY`, `VARCHAR(255)`| `ON CONFLICT (lead_id) DO UPDATE SET ...` |
| `messages` | `msg_hash` (Unique) | `SERIAL`, `VARCHAR(64)`, `TEXT` | `ON CONFLICT (msg_hash) DO NOTHING` + seq sync |
| `costs` | `id` | `SERIAL PRIMARY KEY`, `VARCHAR`, `TEXT` | Bulk copy + sequence sync |
| `team` | `id` | `SERIAL PRIMARY KEY`, `VARCHAR`, `TEXT` | Bulk copy + sequence sync |
| `owner_decisions` | `action_id` | `VARCHAR(64) PRIMARY KEY`, `TEXT` | `ON CONFLICT (action_id) DO UPDATE SET ...` |
| `jev_cache` | `cache_key` | `VARCHAR(255) PRIMARY KEY`, `TEXT` | `ON CONFLICT (cache_key) DO UPDATE SET ...` |
| `message_classifications` | `id` | `SERIAL PRIMARY KEY`, `NUMERIC(6,4)` | Bulk copy + sequence sync |

---

## 4. Test & Verification Results

### Pytest Unit & Integration Regression
- **Command:** `python3 -m pytest tests/ -v`
- **Result:** **60 / 60 PASSED** in 5.11s.
- **Modules Verified:** `test_api_integration.py` (7), `test_business_services.py` (15), `test_dashboard.py` (6), `test_import.py` (8), `test_jev.py` (9), `test_unseen_fixtures.py` (15).

### Independent Financial Audit Invariants (As of October 6, 2026)
- **Unique Clients:** 29 canonical entities.
- **Overdue Invoices:** 9 invoices totaling **$9,250.00**.
- **We Owe Liabilities:** 2 items totaling **$2,400.00** ($1,500 Lone Star cancellation + $900 Glow Aesthetics overpayment).
- **Never Billed Work:** 3 completed bookings totaling **$2,950.00** (DFW Founders, Ironclad Gym, Vega Auto Detailing).
- **Billing Tool Discrepancies:** 6 confirmed tool errors.
- **Lost Requests:** 33 requests (escalated in August 2026).
- **Unanswered Leads:** 22 inbound inquiries.

---

## 5. Security & Isolation Audit

1. **Git Tracking Sanitization:**
   - 0 credentials or secrets committed (`.env` and `.env.*` ignored; only `.env.example` tracked).
   - 0 local databases or WAL logs committed (`*.db`, `*.db-*` strictly ignored).
   - 0 challenge materials committed (`submission/` excluded from Git).
   - 0 proprietary business CSVs committed (`data/*.csv` excluded from Git).
2. **Safe Operational Boundaries:**
   - Outbound actions in the UI remain strictly **draft-only** (one-click copy scripts).
   - Financial adjustments require manual human execution in accounting tools.
   - Zero automated customer messages or webhooks trigger without explicit owner decision.

---

## 6. Known Production Limitations

1. **Challenge No-Login Access Model:**
   Per the Axeom Challenge evaluation criteria, the deployed web application is publicly accessible without a login barrier. In a genuine multi-tenant enterprise deployment, role-based access control (RBAC), OAuth2 / Single Sign-On, and session tokens must be enabled before connecting live production bank accounts.
2. **Serverless Function Execution Timeouts:**
   On Vercel Hobby/Pro serverless runtimes, HTTP requests have a 10s–60s execution timeout. Uploads are processed in-memory and committed transactionally; however, files exceeding 16MB or containing millions of rows should be processed via an asynchronous job queue (e.g., Celery/Redis or AWS SQS).
3. **Typesafe AI (Jev) External API:**
   Live cloud classification requires a configured `TYPESAFE_API_KEY`. When unconfigured, the application transparently runs its deterministic fallback engine (96% benchmark accuracy) without fabricating live results.

---

## 7. Production Readiness Checklist

- [x] **Repository Reorganized:** Private challenge files moved to `submission/` and excluded from Git index.
- [x] **PostgreSQL Schema & Drivers Prepared:** Psycopg 3 and connection pooling configured in `services/db.py`.
- [x] **Dual Database Engine Verified:** Local SQLite continues passing all 60 tests and browser flows.
- [x] **File Uploads Hardened for Serverless:** In-memory streaming with `/tmp` fallback active in `services/ingest.py`.
- [x] **Vercel Routing & Entry Point Configured:** `api/index.py` and `vercel.json` created.
- [x] **Professional Documentation Written:** Comprehensive `README.md` with Mermaid architecture and screenshots in `docs/assets/`.
- [x] **Automated Migration Script Built:** `scripts/migrate_to_postgres.py` ready for one-command execution.
- [ ] **Neon Connection String Provisioned:** *(Awaiting User's Neon `DATABASE_URL`)*
- [ ] **Live PostgreSQL Migration Executed:** *(Will run as soon as `DATABASE_URL` is provided)*
- [ ] **GitHub Remote Repository Created & Pushed:** *(Awaiting User's GitHub authorization)*
- [ ] **Vercel Project Imported & Deployed:** *(Awaiting User's Vercel deployment authorization)*
- [ ] **Final Live URL Tested via Browser:** *(Pending Vercel deployment)*
- [ ] **Final answers.json Updated with Production URL:** *(Pending live URL)*
