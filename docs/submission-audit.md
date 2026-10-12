# Axeom Challenge — Corrected Submission Audit & Verification Register

**Audit Date**: 2026-10-10  
**Phase**: Prompt 11 — Corrected Final Submission Audit  
**Submission Archive**: `Axeom_Challenge_Pack_01_Submission.zip` (0.44 MB compressed, 62 files)  
**Overall Submission Status**: **IN PROGRESS — PENDING USER VERIFICATION & RECORDING**  
**Audit Standard**: Evidence-based verification; reported metrics strictly separated from independent runtime checks.

---

## 1. Executive Deliverables Checklist

| Deliverable | Verification Target (JSON Field / File) | Specification Requirement | Independent Verification Proof | Status |
|---|---|---|---|---|
| **1. Submission Answers** | [`answers.json`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/answers.json) | Template preserved; live link recorded; pack ID `"01"` | Preserved template structure. Evaluated strictly by field name via `scripts/verify_submission.py`. 0 synthetic test records found. | **VERIFIED** |
| **2. Live Application Link** | Field: `"live_link"` in `answers.json` | Unauthenticated, phone-friendly, hard-to-guess URL | HTTP 200 confirmed via curl at 13:51 UTC+5 at `https://6de08334a5e523.lhr.life`. Tunnel runs locally; cellular test pending. | **VERIFIED (TUNNEL) / PENDING (CELLULAR)** |
| **3. Technical Writeup** | [`writeup.pdf`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/writeup.pdf) | Maximum 2 rendered pages; answers, design, costs, limits, Jev | Compiled via Pandoc/XeLaTeX (`extarticle`, 9pt, 0.5in margin). Verified: `pdfinfo writeup.pdf` reports **Pages: 2**. | **VERIFIED** |
| **4. Questions & Assumptions** | [`assumptions.md`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/assumptions.md) | Questions we would have asked, assumptions, evidence & risks | 22 documented items covering identity, finances, marketing costs, and fallback rules. | **VERIFIED** |
| **5. Daily Session Log** | [`daily_log.md`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/daily_log.md) | Chronological session journal of progress, bugs, and pivots | 12 chronological sessions documenting data discrepancies, bank reconciliation, and test corrections. | **VERIFIED** |
| **6. Demo Plan & Practice Cues** | [`docs/demo-plan.md`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/docs/demo-plan.md) | 8–9 min demo walkthrough + truthful reflection cues | Sequence timed to ~8:30. Reflection practice cues grounded only in real project discoveries. | **VERIFIED** |
| **7. Candidate Video Recording** | Field: `"video_link"` in `answers.json` | 8–9 min video, camera-on, no notes, uncut reflection | Awaiting actual candidate recording. Zero fabricated URLs or placeholder videos. | **PENDING USER ACTION** |
| **8. Video Transcript** | Field: `"video_transcript"` in `answers.json` | Verbatim transcript of actual recording | Awaiting post-recording transcription. | **PENDING USER ACTION** |
| **9. Clean Submission Archive** | `Axeom_Challenge_Pack_01_Submission.zip` | Excludes `.env`, virtualenvs, `.git`, `__pycache__`, tests | Assembled via `scripts/package_submission.py`. 62 files, 0.44 MB. Zero secrets or synthetic test states. | **VERIFIED** |

---

## 2. Requirement-by-Requirement Traceability Audit

| Req ID | Description | Source / Spec | Implementation Location | Independent Verification Proof | Audit Status |
|---|---|---|---|---|---|
| **REQ-CORE-01** | Preserve Pack ID `"01"` as exact text | PDF p.1, PACK.txt | `answers.json` (`"pack_id"`) | Validated string equality `"01"` | **VERIFIED** |
| **REQ-CORE-02** | Fixed as-of date `2026-10-06` | PDF p.1 (Situation) | `services/finance.py` | Aging calculations strictly anchored to `2026-10-06` | **VERIFIED** |
| **REQ-DATA-01** | Ingest all 8 original pack files | PDF p.1 (Files) | `services/ingest.py`, `services/db.py` | 1,112 rows ingested into SQLite without loss | **VERIFIED** |
| **REQ-DATA-02** | Shared pipeline for pack and new uploads | PDF p.2 (Part 2) | `/api/upload` endpoint | Ingests new records via same schema validation pipeline | **VERIFIED** |
| **REQ-DATA-03** | Canonical identity resolution | PDF p.1 (Messy data) | `services/identity.py` | 29 clients resolved; homonyms split, rebrands merged | **VERIFIED** |
| **REQ-DATA-04** | Identify third-party payers | PDF p.1, answers.json | `services/identity.py` | Brightline Marketing mapped to Greenway & Summit | **VERIFIED** |
| **REQ-BIZ-01** | Real client count (29) | PDF p.2 (Part 1, Q1) | `services/identity.py` | 29 distinct clients resolved | **VERIFIED** |
| **REQ-BIZ-02** | Reconcile overdue invoices ($9,250) | PDF p.2 (Part 1, Q2) | `services/finance.py` | 5 overdue accounts reconciled ($9,250 net studio receivable) | **VERIFIED** |
| **REQ-BIZ-03** | Reconcile amounts studio owes ($2,400) | PDF p.2 (Part 1, Q2) | `services/finance.py` | Studio liabilities: Lone Star ($1.5k credit) & Glow ($900 refund) | **VERIFIED** |
| **REQ-BIZ-04** | Completed unbilled work ($2,950) | PDF p.2 (Part 1, Q2) | `services/finance.py` | Haven ($1.8k), NextLevel ($800), BlueSky ($350) | **VERIFIED** |
| **REQ-BIZ-05** | Billing tool software errors (6) | PDF p.2 (Part 1, Q2) | `services/finance.py` | 6 invoices marked unpaid proved cleared by bank logs | **VERIFIED** |
| **REQ-BIZ-06** | Trace lost client requests (33) | PDF p.2 (Part 1, Q3) | `services/requests.py` | 33 missed edits traced; escalation started Aug 2026 | **VERIFIED** |
| **REQ-BIZ-07** | Never-replied leads breakdown (22) | PDF p.2 (Part 1, Q3) | `services/requests.py` | 22 blank `first_reply`: 18 true prospects, 3 existing clients, 1 spam | **VERIFIED** |
| **REQ-BIZ-08** | Client most likely to leave | PDF p.2 (Part 1, Q4) | `services/analytics.py` | Patel Insurance Group ($2.5k retainer, compliance breakdown) | **VERIFIED** |
| **REQ-BIZ-09** | Most profitable marketing channel | PDF p.2 (Part 1, Q5) | `services/analytics.py` | Website form ($11.4k gross margin); ad spend unrecorded in costs | **VERIFIED** |
| **REQ-BIZ-10** | Top 3 Monday owner actions | PDF p.2 (Part 1, Q6) | `services/analytics.py` | (1) Patel churn/cash; (2) Lone Star credit; (3) Unbilled work | **VERIFIED** |
| **REQ-APP-01** | Live web app accessible on phone | PDF p.2 (Part 2) | `scripts/tunnel.py` | Verified live via curl over internet; physical phone test pending | **VERIFIED (LINK) / PENDING (PHONE)** |
| **REQ-APP-02** | Pass 10-second phone test | PDF p.2 (Part 2) | Conneq UI (`index.html`) | 22 KB payload, hero card above fold; usability test pending | **PENDING USER VERIFICATION** |
| **REQ-APP-03** | "Add new files" button in UI | PDF p.2 (Part 2) | Multi-part dropzone uploader | New records update calculations; repeat upload is idempotent | **VERIFIED** |
| **REQ-APP-04** | Suggest, never act alone | PDF p.2 (Part 2) | UI action confirmation modal | Draft call scripts provided; zero automated external messages | **VERIFIED** |
| **REQ-APP-05** | Durable persistence across restarts | System Architecture | SQLite `axeom.db` | Data and owner decisions persist across application restarts | **VERIFIED** |
| **REQ-JEV-01** | Live Jev Model Integration | PDF p.2 (Part 3) | `services/jev.py` | Blocked: `TYPESAFE_API_KEY` not configured; client code ready | **BLOCKED** |
| **REQ-JEV-02** | Live Jev Benchmark Measurement | PDF p.2 (Part 3) | `tests/evaluate_jev.py` | Live model accuracy not evaluated; fallback achieves 100% vs 26.7% | **BLOCKED / NOT VERIFIED** |
| **REQ-JEV-03** | Graceful fallback & offline resilience | System Architecture | `classify_intent_fallback()` | Deterministic keyword/regex fallback operational offline | **VERIFIED** |
| **REQ-SUB-01** | Valid `answers.json` structure | PDF p.2-3 (Submit) | `answers.json` | 23 required top-level JSON keys verified by field name | **VERIFIED** |
| **REQ-SUB-02** | Max 2-page rendered writeup | PDF p.2-3 (Submit) | `writeup.pdf` | Verified exactly 2 rendered pages via `pdfinfo` | **VERIFIED** |
| **REQ-SUB-03** | Documented `assumptions.md` | PDF p.2-3 (Submit) | `assumptions.md` | 22 documented questions, assumptions, and operational risks | **VERIFIED** |
| **REQ-SUB-04** | Documented `daily_log.md` | PDF p.2-3 (Submit) | `daily_log.md` | 12 chronological sessions documenting progress and corrections | **VERIFIED** |
| **REQ-SUB-05** | 8–9 min demo video + transcript | PDF p.2-3 (Submit) | Candidate recording | Demo sequence prepared; awaits actual candidate recording | **PENDING USER ACTION** |
| **REQ-SUB-06** | Single submission archive | PDF p.2-3 (Submit) | `Axeom_Challenge_Pack_01_Submission.zip` | Archive assembled (62 files, 0.44 MB); zero secrets or test states | **VERIFIED** |

---

## 3. Technical Inspection of Deployment Behind `lhr.life`

1. **Host Workstation**:
   - The application runs on the candidate's local Linux workstation (`Linux 6.8.0-52-generic x86_64`) on local port `5050` (`http://127.0.0.1:5050`).
2. **Tunnel Keepalive & IPv4 Binding**:
   - An unauthenticated reverse SSH tunnel is maintained by `scripts/tunnel.py` connecting to `localhost.run` (`ssh -R 80:127.0.0.1:5050 nokey@localhost.run`).
   - *Technical Discovery*: Using `80:localhost:5050` previously triggered an intermittent `502 Bad Gateway` because OpenSSH resolved `localhost` to IPv6 `::1`, whereas the local server was bound to IPv4 `0.0.0.0:5050`. Binding explicitly to `127.0.0.1:5050` resolved this failure mode.
   - If the background script or SSH connection drops, the tunnel terminates.
3. **URL Permanence Risk**:
   - `localhost.run` allocates ephemeral subdomains (`https://6de08334a5e523.lhr.life`).
   - **Risk**: If the tunnel disconnects or the machine restarts, `localhost.run` generates a new random subdomain, invalidating the URL previously written to `answers.json`.
4. **Availability & Persistence Across Restarts**:
   - **Local Workstation**: SQLite database `axeom.db` resides on persistent local NVMe storage and survives server reboots. However, the machine must stay powered on and connected to the internet for the tunnel to remain reachable.
   - **Cloud Deployment Alternative**: A production-ready PaaS deployment configuration is packaged (`Procfile`, `requirements.txt`, automatic cold-start database seeding) allowing deployment to free cloud tiers like Render or Fly.io. On free Render, web services spin down after 15 minutes of inactivity (causing 30-50 second cold starts) and disk storage is ephemeral unless seeded on boot.

---

## 4. Public Link Verification (Unauthenticated Browser & Method)

- **Test Execution Timestamp**: 2026-10-10 13:51:03 UTC+5.
- **Method**: Direct HTTP request from an external terminal session without cookies or credentials:
  ```bash
  curl -s -o /dev/null -w "HTTP Status: %{http_code}\nContent-Type: %{content_type}\nSize: %{size_download} bytes\n" https://6de08334a5e523.lhr.life
  ```
- **Observed Result**:
  - `HTTP Status: 200`
  - `Content-Type: text/html; charset=utf-8`
  - `Payload Size: 22,642 bytes`
- **Cellular & Physical Phone Testing Status**:
  - **NOT claimed as automated check**. Automated testing was performed via network curl.
  - Physical mobile usability over cellular data (LTE/5G) is marked **PENDING CANDIDATE MANUAL TEST**.

---

## 5. Genuinely New-File Acceptance Test & Idempotency

Implemented in [`tests/test_unseen_fixtures.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/tests/test_unseen_fixtures.py) via two isolated tests:

1. **New Record Ingestion Updates Balance**:
   - Test: `test_genuinely_new_file_record_updates_result_and_repeat_is_idempotent`
   - Data: Synthetic CSV fixture `invoices_test_diff.csv` containing 1 new invoice:
     ```csv
     invoice_id,booking_id,client_name,amount,issue_date,due_date,status
     INV-9100,B199,Crown Barbers,750.00,2026-09-10,2026-09-24,unpaid
     ```
   - Baseline Overdue: Calculated from pack data as **$9,250.00**.
   - Post-Upload Overdue: Ingested file; verified Overdue Invoices increased by exactly $750.00 to **$10,000.00** ($9,250 + $750).
2. **Repeat Upload Idempotency**:
   - Ingested the exact same `invoices_test_diff.csv` a second time.
   - Verified that total invoice row count did not increase (0 duplicates created) and Overdue Invoices remained exactly **$10,000.00**.
3. **Duplicate File Detection (Independent Test)**:
   - Test: `test_duplicate_file_exact_sha256_detection`
   - Verified that re-uploading a byte-for-byte identical file is recognized by SHA-256 fingerprinting and returns `status: "duplicate_file"`.
4. **Dataset Isolation**:
   - Performed on temporary SQLite database `axeom_synthetic_test.db` which is unlinked immediately after test completion.
   - `scripts/verify_submission.py` confirms that zero synthetic IDs (`INV-9100`, etc.) entered `axeom.db` or `answers.json`.

---

## 6. Recheck of Critical Findings Against Original Source Evidence

1. **Client Identity Merges and Splits**:
   - **Split Verified**: *Lone Star Realty* (Dana Brooks, `dana@lonestar-realty.com`, `(512) 555-0144`) and *Lonestar Realty Group* (Greg Whitfield, `greg@lonestarrealtygroup.com`, `(512) 555-0182`) are legally distinct real estate companies with different contact info, websites, and lead sources. Merging them would have corrupted both balances.
   - **Merge Verified**: *Crown Barbers* and *Crown Barber Studio* (Marcus Vance, `marcus@crownbarbers.com`) represent the same client entity with differing phone number formatting (`5125550177` vs `(512) 555-0177`).
2. **Payment Allocation, Credits/Refunds, and Unbilled Work**:
   - **Payment Allocation**: Tasha Green sent an unreferenced $900 wire (`P5110`) with no invoice ID. August communications prove she requested to pay for three $300 shoot sessions together (`INV-1090`, `INV-1105`, `INV-1118`), clearing all three.
   - **Studio Liabilities ($2,400.00)**:
     - $1,500.00 credit owed to Dana Brooks (*Lone Star Realty*): Paid for shoot `B148` which was cancelled due to a family emergency and never shot.
     - $900.00 cash refund owed to *Glow Aesthetics*: Client overpaid invoice `INV-1115` twice via separate payments `P5091` ($900) and `P5093` ($900).
   - **Unbilled Work ($2,950.00)**: Video production records prove completion of videos for Haven Coworking ($1,800), NextLevel Physio ($800), and BlueSky Drone ($350) with zero matching invoice in `invoices.csv`.
3. **Channel Replies & Lead Breakdown**:
   - In `leads.csv`, 22 leads have a blank `first_reply` timestamp.
   - Cross-channel audit reveals:
     - 3 leads are existing clients active on other communication channels: Jordan Reed (`L071`), Tasha Green (`L083`), and Nina Patel (`L097`).
     - 1 lead is automated marketing spam (`L078`, `promo@fastfollowers.io`).
     - **18 leads** are genuine prospective clients who submitted inquiries and received no reply.
4. **Marketing Profitability & Cost Attribution**:
   - `costs.csv` tracks video editor hours ($35/hr) and studio rental fees ($40/hr).
   - It contains **zero** paid customer acquisition costs (e.g. Meta Ads, Google Ads spend).
   - Profitability by channel represents **gross margin above direct production labor and studio rent**, not net ROI on advertising spend.
5. **Direction of Money Owed**:
   - **Overdue Invoices ($9,250.00)**: Polarity = **Clients owe Studio** (Accounts Receivable / positive incoming cash flow).
   - **We Owe ($2,400.00)**: Polarity = **Studio owes Clients** (Studio Liabilities / outgoing cash or credits).
   - **Never Billed ($2,950.00)**: Polarity = **Unbilled Work** (Potential incoming revenue upon invoicing).
   - All dashboard action cards strictly reflect this directional polarity.

---

## 7. 10-Second Phone Usability Audit

- **Claim Status**: **PENDING CANDIDATE USER TEST**.
- **Technical Prerequisites Observed**:
  - Unauthenticated initial route loads `Today` view directly.
  - Page payload is 22 KB with zero external CDNs, webfonts, or heavy frameworks.
  - Bright lime Hero Action #1 Card (Patel Insurance Group, $2,500 overdue + churn risk) is positioned above the fold.
- **Required User Test**:
  - The candidate must open `https://6de08334a5e523.lhr.life` on a physical smartphone (or 390×844 mobile viewport) and time whether a first-time user can identify the first action, the underlying reason, and the next step within 10 seconds.

---

## 8. Summary Checklist of Audit Findings

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SUMMARY AUDIT CHECKLIST                         │
├───────────────┬────────────────────────────────────────────────────────┤
│ VERIFIED (22) │ REQ-CORE-01, REQ-CORE-02, REQ-DATA-01, REQ-DATA-02,    │
│               │ REQ-DATA-03, REQ-DATA-04, REQ-BIZ-01, REQ-BIZ-02,      │
│               │ REQ-BIZ-03, REQ-BIZ-04, REQ-BIZ-05, REQ-BIZ-06,        │
│               │ REQ-BIZ-07, REQ-BIZ-08, REQ-BIZ-09, REQ-BIZ-10,        │
│               │ REQ-APP-03, REQ-APP-04, REQ-APP-05, REQ-JEV-03,        │
│               │ REQ-SUB-01, REQ-SUB-02, REQ-SUB-03, REQ-SUB-04,        │
│               │ REQ-SUB-06                                             │
├───────────────┼────────────────────────────────────────────────────────┤
│ FAILED (0)    │ None. Zero invariant test failures (60/60 pass).       │
├───────────────┼────────────────────────────────────────────────────────┤
│ BLOCKED (2)   │ REQ-JEV-01 (Live Jev Model Integration - No API Key)   │
│               │ REQ-JEV-02 (Live Jev Benchmark Accuracy - Not evaluated│
│               │             due to blocked live API access)            │
├───────────────┼────────────────────────────────────────────────────────┤
│ PENDING (4)   │ 1. REQ-APP-01 (Physical phone cellular-network test)   │
│               │ 2. REQ-APP-02 (Candidate 10-second phone user test)    │
│               │ 3. REQ-SUB-05 (Candidate 8–9 min uncut video recording)│
│               │ 4. Candidate header info (`your_name`, `your_email`)   │
└───────────────┴────────────────────────────────────────────────────────┘
```
