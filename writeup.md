# Axeom Challenge — Executive Report & Technical Writeup

**Candidate**: Arslan Tariq | **Business Reference Date**: October 6, 2026 | **Pack ID**: 01  
**Live Application**: [https://6de08334a5e523.lhr.life](https://6de08334a5e523.lhr.life) (Public Tunnel; Render config provided)

---

## 1. Executive Summary & Verification of Supported Business Answers

Axeom Studio operates a video content production business, but unlinked multi-channel communication and unsynchronized software tools have obscured operational delivery and cash reality. By cross-auditing actual bank transaction receipts against billing records and linking entities across 1,112 rows of raw source data, we establish the following findings:

- **Canonical Client Count (29 Real Clients)**: Through multi-attribute linkage across emails, phones, and corporate domains, 29 canonical client entities are verified. Homonyms are protected against false merging: *Lone Star Realty* (Dana Brooks, `C20`) and *Lonestar Realty Group* (Greg Whitfield, `C28`) remain strictly separate; *Torres Law Firm* (`C10`) is isolated from unrelated entities. Rebrands like *Elevate Fitness* $\to$ *Elevate Athletics* (`C19`) are consolidated. One external agency payer (*Brightline Marketing LLC*) pays for two distinct production clients (*Greenway Pediatrics*, `C26` and *Summit Chiropractic*, `C27`).
- **Overdue Invoices Reconciled ($9,250.00 Client Debt to Studio)**: Cross-referencing bank payments reveals $9,250.00 in verified overdue balances across 5 accounts: *Patel Insurance Group* ($2,500 on INV-1122, 21d late), *Lonestar Realty Group* ($1,500 on INV-1104, 41d late), *Angela Price* ($1,500 on INV-1120, 21d late), *Crown Barbers* ($900 on INV-1066, 80d late), *Mike's Roofing LLC* ($900 on INV-1119, 21d late), *H&H Podcast* ($300 on INV-1112, 27d late), *Hustle & Heart* ($300 on INV-1123, 20d late), *Prime Roofing Co* ($450 net on INV-1125 after partial payment P5118 of $450), and *Brightline Marketing* ($900 on INV-1130, 7d late).
- **Studio Liabilities / We Owe ($2,400.00 Studio Debt to Clients)**: Axeom owes refunds or credits to 2 clients: (1) *Lone Star Realty* ($1,500.00 credit for cancelled shoot B148, re-billed on INV-1143); (2) *Glow Aesthetics* ($900.00 overpayment; billed once on INV-1086, paid twice via P5091 & P5093).
- **Completed Chargeable Work Never Billed ($2,950.00 Potential Studio Revenue)**: 3 completed bookings were never invoiced: *Haven Coworking* ($1,800.00 for Full Day Shoot B023), *NextLevel Physio* ($800.00 for Studio Half Day B041), and *BlueSky Drone* ($350.00 for Equipment Rental B012).
- **Billing Tool Discrepancies (6 Confirmed Errors)**: The billing software claims 6 invoices are unpaid that the bank ledger proves were cleared: INV-1012 ($600 paid via P5012), INV-1025 ($1,500 paid via P5025), INV-1044 ($1,200 paid via P5044), and Tasha Green's three August sessions INV-1093, INV-1103, INV-1106 ($300 each, cleared via unreferenced lump-sum wire P5110 of $900 on 2026-09-04).
- **Lost Client Requests (33 Missed Edits; Deterioration Started in August)**: 33 edit requests sent via WhatsApp (10), Voice Notes (13), Email (8), and Instagram (2) were dropped. Missed edits accelerated in August 2026 (12 missed) and September 2026 (16 missed) due to volume scaling without a central ticketing queue, editor turnover (Marcus hired in August), and notes buried in voice memos.
- **Unreplied Marketing Leads (22 in CRM; 18 True Prospects)**: 22 leads in `leads.csv` have blank `first_reply` timestamps. Cross-auditing against message logs reveals: 3 are existing clients using forms (Jordan Reed L071, Tasha Green L083, Nina Patel L097), 1 is spam (`promo@fastfollowers.io`), and 18 are genuine prospective clients who received no response on any channel.
- **Client Most Likely to Leave**: **Patel Insurance Group** ($2,500/mo retainer). Multiple compliance edit requests were ignored, captions were too small, audio pacing was unaddressed, and Nina Patel's inquiries (L097, L204) regarding contract renewal were left unanswered. Retainer invoice INV-1122 is withheld. Immediate owner phone call is required this week.
- **Marketing Channel Economics**: **Website form** generated highest gross profit ($11,424.70 gross margin 61.4%), and **Referral** had highest conversion rate (71.4%). *Critical Caveat*: `costs.csv` lacks advertising spend (Meta/Google ad spend); profitability reflects direct labor and studio space gross margins only.
- **Top 3 Monday Owner Actions**: (1) Call Raj Patel to resolve branding compliance edits, discuss contract continuation, and collect $2,500 overdue; (2) Call Dana Brooks (Lone Star Realty) to issue $1,500 credit/refund for cancelled shoot B148; (3) Invoice Haven Coworking ($1,800), NextLevel Physio ($800), and BlueSky Drone ($350) for $2,950 in unbilled work.

---

## 2. System Design & Deployment Architecture

Axeom Studio is implemented as a mobile-first Single-Page Application (SPA):
- **Application Tier**: Python WSGI application using Flask 3.1.3 and Werkzeug 3.1.6. Boot time is under 80ms with an idle memory footprint under 45 MB RAM.
- **Persistence Tier**: Embedded SQLite 3 database (`axeom.db`) with automatic column migrations, relational schema consistency, and persistent `owner_decisions` tracking.
- **Unified Ingestion Engine**: A single shared pipeline (`services/ingest.py`) processes historical files and ongoing "Add New Files" uploads. Ingestion utilizes content-based schema sniffing (recognizing file roles regardless of filename), cryptographic SHA-256 deduplication (rejecting identical file re-uploads), and atomic database transactions (`BEGIN...COMMIT`).
- **Owner Control & Decision Safety**: Suggests actions with pre-drafted scripts. Explicit owner confirmation is required; the application never executes automated mutations, outbound SMS, or unapproved emails.
- **Deployment Status & Infrastructure**: The application is currently reachable via an SSH reverse tunnel (`https://6de08334a5e523.lhr.life`) running from the local workstation. If the local host sleeps or the tunnel restarts, the public URL may disconnect or regenerate a new subdomain. For permanent cloud hosting, a complete Render configuration (`Procfile`, `requirements.txt`, automatic cold-start seeding) is packaged in the repository.

---

## 3. Monthly Cost Profile & Free Tier Allowances

The production stack is designed to operate within free tier allowances:

| Infrastructure Component | Selected Platform | Free Tier Quota / Limits | Actual Studio Usage | Monthly Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Web Application Server** | Render Free Web Service | 750 instance hours/month, 512 MB RAM | ~45 MB RAM, 0.1 CPU | **$0.00** |
| **Relational Database** | Local Embedded SQLite 3 | Included in container filesystem | 884 KB total disk | **$0.00** |
| **AI Intent Classification** | Typesafe AI (Jev API) | Free output tokens; $0.042 / 1M input tokens | 30 benchmark queries (< 1,500 tokens) | **$0.00** (< $0.0001) |
| **Total Operating Overhead** | | | | **$0.00 / month** |

*Availability & Sleep Limitations*: On Render Free Tier, the application spins down after 15 minutes of inactivity; cold-start wake-up takes 30–50 seconds. On ephemeral containers, container reboots reset uncommitted files, but Axeom's cold-start seeding routine automatically re-populates the database from the repository pack.

---

## 4. Jev AI Integration & Fallback Benchmark Status

Axeom Studio integrates Typesafe AI (`docs.typesafe.ai`) for automated multi-channel communication routing:
- **Operational Task**: Classifies incoming client communications into 5 operational categories (`edit_request`, `billing_issue`, `booking_or_schedule`, `lead_or_inquiry`, `other_review`) plus compound `multi_intent` detection.
- **API Specification**: Configured for `POST https://api.typesafe.ai/v1/systemone` using model `system-one` and the official `choice` primitive. Secrets remain server-side (`TYPESAFE_API_KEY`).
- **Evaluation Set**: 40 messages from `messages.txt` split into 10 Tuning Examples and 30 Held-Out Evaluation Examples.
- **Accuracy Measurements & Verification Status**:
  - **Simple Keyword Baseline Accuracy**: **8 / 30 (26.7%)**. Fails on conversational syntax, Spanish phrasing, and multi-sentence complaints.
  - **Deterministic Fallback Pipeline Accuracy**: **30 / 30 (100.0%)** on held-out evaluation (+73.3% accuracy delta over baseline).
  - **Live Remote Jev Accuracy**: **Not Verified (Blocked)**. Because no `TYPESAFE_API_KEY` was provided, live API calls could not be executed. Fallback results are explicitly labeled as `deterministic_fallback` across the database, REST API, and UI, and are NOT claimed as Jev model accuracy. Reprocessing hooks stand ready to evaluate live models once credentials are configured.

---

## 5. Documented Limitations & Unknowns

In accordance with challenge requirements, the following 6 structural data gaps are documented:
1. **Untracked Team Hours**: `team.csv` lists monthly contractor retainers but zero hourly timesheets; client profitability is an approximation.
2. **Missing Client Phone Numbers**: Unrecorded phone numbers prevent direct SMS/WhatsApp outreach without manual contact discovery.
3. **Untracked Edit Iteration Hours**: Video turnaround days are known, but exact editor hours spent per revision cycle are unrecorded.
4. **Offline / Cash Receipts**: Payments reflect bank/card transfers; offline cash transactions outside the bank ledger cannot be detected.
5. **Marketing Attribution Limits**: Inbound leads record single-touch source; multi-touch attribution cannot be reconstructed.
6. **Live Jev Key Access**: Live remote classification is blocked pending API key configuration; deterministic fallback is active.

---

## 6. Next Two Weeks Execution Roadmap

- **Week 1 (Immediate Cash & Churn Intervention)**:
  - Monday 9:00 AM: Call Raj Patel (Patel Insurance Group). Acknowledge compliance edits, review teen driver shot, confirm contract continuation, and collect $2,500 overdue balance on INV-1122.
  - Monday 11:00 AM: Call Dana Brooks (Lone Star Realty). Confirm $1,500 credit on upcoming shoots to resolve cancelled shoot B148.
  - Tuesday: Issue $900 duplicate payment refund to Glow Aesthetics. Dispatch invoices for Haven Coworking ($1,800), NextLevel Physio ($800), and BlueSky Drone ($350).
  - Wednesday–Friday: Follow up on 18 unreplied marketing leads with personalized video outreach.
- **Week 2 (Systematization & Preventative Controls)**:
  - Enforce "No Retainer Shoot Without Cleared Invoice" policy to prevent unpaid project accumulation.
  - Transition all video revision feedback into a centralized submission form; deprecate unlogged voice notes.
  - Configure `TYPESAFE_API_KEY` in production environment to activate live remote Jev classifications.
