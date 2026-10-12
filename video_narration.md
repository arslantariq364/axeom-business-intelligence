# Axeom Studio Operations & Business Intelligence OS
## Official Video Narration Script & Technical Production Storyboard

**Candidate:** Arslan Tariq (`tsa6648@gmail.com`)  
**Project:** [https://axeom-business-intelligence.vercel.app](https://axeom-business-intelligence.vercel.app)  
**Repository:** [https://github.com/arslantariq364/axeom-business-intelligence](https://github.com/arslantariq364/axeom-business-intelligence)  
**Target Video Duration:** 6–8 minutes (~430 seconds total)  
**Business Reference Date:** October 6, 2026 (`2026-10-06`)  
**Narration Engine:** Microsoft Neural Studio Synthesis (`en-US-AndrewNeural`, clear AI narration attribution for Part 1; direct candidate script for Part 2)

---

## Storyboard & Timing Overview

| Scene | Section Title | Timestamp | Duration | Visual Focus & On-Screen Choreography |
| :--- | :--- | :---: | :---: | :--- |
| **01** | Introduction & Overview | `00:00 - 00:36` | 36s | Live production header, reference date badge, responsive dashboard layout, pulse cards overview |
| **02** | Today View — Owner Triage | `00:36 - 01:20` | 44s | Patel Insurance hero action card ($600 overdue), Monday Top 3 triage cards, interactive decision state |
| **03** | Money View — Financial Intelligence | `01:20 - 02:06` | 46s | $9,250 overdue, $2,400 we owe, $2,950 unbilled, 6 software discrepancies, subtab transitions |
| **04** | Clients View — Identity Matching | `02:06 - 02:41` | 35s | Canonical client directory (29 clients C01–C29), third-party payer decoupling, client history dossier |
| **05** | Requests & Leads View | `02:41 - 03:16` | 35s | 33 lost requests root causes, August 2026 lead cliff (22 unreplied leads), response latency metrics |
| **06** | Evidence Register & Provenance | `03:16 - 03:41` | 25s | Cross-reference search, line-item CSV row provenance, banking deposit matching |
| **07** | Upload Business Files | `03:41 - 04:10` | 29s | Idempotent file ingestion, multi-counter feedback (added, updated, skipped, rejected), baseline data safety |
| **08** | Architecture & Transparent Jev Status | `04:10 - 04:48` | 38s | Dual-engine Neon PostgreSQL + SQLite, Vercel WSGI serverless, $0/mo cost profile, honest Jev fallback status |
| **09** | Export answers.json | `04:48 - 05:15` | 27s | Direct browser-streamed in-memory JSON export adhering strictly to Pack 01 schema |
| **10** | Q&A Segment Introduction | `05:15 - 05:34` | 19s | High-contrast title card: Part 2 Candidate Technical Q&A briefing |
| **11** | Q&A 1: Hardest Technical Challenge | `05:34 - 06:01` | 27s | Question 1 title card & teleprompter: Identity matching & third-party payer decoupling |
| **12** | Q&A 2: Debugging & Initial Mistakes | `06:01 - 06:32` | 31s | Question 2 title card & teleprompter: Authoritative truth assumption, 6 billing tool bugs, test fixture isolation |
| **13** | Q&A 3: Strategic Owner Advice | `06:32 - 06:57` | 25s | Question 3 title card & teleprompter: Stop delivering before invoicing ($2,950 leaked), stop informal inquiry handling |
| **14** | Conclusion & Outro | `06:57 - 07:14` | 17s | Final deliverable summary, test suite verification (69/69 green), GitHub links |

---

## PART 1 — AUTOMATED DEMONSTRATION (00:00 - 05:15)
*(Audio Attribution: Professional AI Narration)*

### Scene 01: Introduction & Challenge Pack 01 Overview (`00:00 - 00:36`)
- **Visual:** Smooth zoom and pan over `https://axeom-business-intelligence.vercel.app`. Virtual cursor glides over the header badge: `"Reference Date: 2026-10-06 | Neon PostgreSQL AWS us-east-2"`. Camera smoothly scrolls to reveal the high-level pulse metrics ($9,250 Overdue, $2,400 Owed, $2,950 Unbilled, 29 Active Clients) and returns to top.
- **Narration:**
  > "Welcome to the Axeom Studio Business Intelligence and Operations Dashboard. This demonstration provides an executive technical walkthrough of our solution for Axeom Challenge Pack 01. The system is live in production on Vercel Edge, backed by a dual-engine database architecture using Neon Serverless PostgreSQL and local SQLite. All business calculations are anchored to the strict business reference date of October 6th, 2026. Please note that this initial walkthrough utilizes clear AI-assisted narration to guide you through the operational dashboard and data architecture."

### Scene 02: Today View — Owner Command Center & Monday Triage (`00:36 - 01:20`)
- **Visual:** Focus snaps to the Hero Action Card for **Patel Insurance Group**. Virtual cursor hovers over the invoice badge: `INV-1122 ($600.00 Overdue)`. Cursor clicks "In Progress", dynamically persisting the owner's decision in PostgreSQL. Cursor scrolls down to the **Monday Top Three** priority cards:
  1. Southside Athletics ($1,000 overdue shoot, `INV-1098`)
  2. Sarah Jenkins (contract renewal review)
  3. Metroplex Logistics ($750 unbilled commercial video, `S-058`)
- **Narration:**
  > "Here on the Today view, the studio owner is immediately presented with high-priority operational decisions rather than raw data tables. The hero action card highlights Patel Insurance Group, where a 600-dollar retainer from August 2026 is currently overdue. Below the hero card, our triage engine computes the Monday Top Three priorities: first, recovering a 1,000-dollar overdue shoot from Southside Athletics; second, addressing contract renewal and unbilled deliverables for Sarah Jenkins; and third, resolving a 750-dollar unbilled commercial shoot for Metroplex Logistics. The owner can click Approve, Defer, or In Progress to persist triage decisions directly into PostgreSQL."

### Scene 03: Money View — Financial Intelligence & Leakage Reconciliation (`01:20 - 02:06`)
- **Visual:** Cursor clicks `#nav-money`. View transitions smoothly; top header updates to `AXEOM • Financial & Revenue Intelligence`. Focus shifts to four financial pulse cards:
  - Overdue Invoices: **$9,250.00** (9 Invoices)
  - We Owe Clients: **$2,400.00** (2 Credits)
  - Never Billed Work: **$2,950.00** (3 Shoots)
  - Billing Discrepancies: **6 Issues**
  Cursor clicks each subtab:
  - Subtab "We Owe Clients": displays Summit Dental ($1,200) and Highland Park ($1,200).
  - Subtab "Never Billed Work": displays Oakridge High ($1,400), Trinity Presbyterian ($800), Downtown Arts ($750).
  - Subtab "Billing Tool Discrepancies": displays the 6 software bugs in legacy exports.
- **Narration:**
  > "Navigating to the Money view reveals the core financial reconciliation engine. Our audit uncovered 9,250 dollars in overdue unpaid invoices across nine separate accounts. Simultaneously, we identified 2,400 dollars owed back to clients, including a 1,200-dollar credit for Summit Dental due to weather cancellations, and a 1,200-dollar credit for Highland Park. Crucially, the system exposed 2,950 dollars in completed work that was delivered but never invoiced, spanning Oakridge High, Trinity Presbyterian, and Downtown Arts. Furthermore, our cross-table audit flagged six software discrepancies where the legacy billing tool falsely marked unpaid invoices as settled."

### Scene 04: Clients View — Canonical Identity & Third-Party Payers (`02:06 - 02:41`)
- **Visual:** Cursor clicks `#nav-clients`. Header updates to `AXEOM • Canonical Client Directory`. Displays the master list of **29 active canonical clients** (`C01`–`C29`). Cursor types `"Patel"` into the search box, instantly filtering the table. Cursor clicks "View History", opening the Patel Insurance client dossier with complete historical shoots, invoices, and payment provenance.
- **Narration:**
  > "The Clients view manages our canonical directory of exactly 29 active clients, designated C01 through C29. A critical data integrity challenge in Axeom Studio was distinguishing actual clients from third-party funding entities. For instance, entities like Texas Community Foundation, Horizon Media Group, and Northpoint Parent LLC act as third-party payers rather than client accounts. Our identity resolution service disentangles these aliases while linking complete production dossiers, tracking shoots, invoices, and payment histories per client."

### Scene 05: Requests & Leads View — Operational Leakage & August Cliff (`02:41 - 03:16`)
- **Visual:** Cursor clicks `#nav-requests`. Header updates to `AXEOM • Lost Requests & Lead Pipeline`. Focus highlights the **33 Lost Requests** card and the **22 Unreplied Leads** card. Cursor scrolls down through the root-cause distribution chart (Pricing Friction: 14, Slow Turnaround: 11, Scheduling Conflicts: 8) and highlights the August 2026 inquiry cliff where response timestamps are completely blank.
- **Narration:**
  > "In the Requests and Leads view, we analyze operational leakage. Out of 118 total inquiries, 33 requests were lost. Our root cause classification attributes 14 losses to pricing friction, 11 to slow response turnaround, and 8 to scheduling conflicts. More alarmingly, the data reveals an August 2026 cliff, where 22 qualified inquiries went completely unanswered due to the absence of an automated intake workflow. Every lead is indexed with response latency, stage tracking, and estimated revenue impact."

### Scene 06: Evidence Register & Provenance Tracking (`03:16 - 03:41`)
- **Visual:** Cursor clicks `#nav-evidence`. Header updates to `AXEOM • Evidence & Provenance Register`. In the search input, cursor types `"Patel"` then `"INV-1122"`. The results instantly render cross-system provenance linking invoice lines to specific CSV file rows, banking settlement records, and message timestamp logs.
- **Narration:**
  > "Data trust requires verifiable proof. Our Evidence Search view maintains an exhaustive cross-reference register connecting every financial metric and operational claim to source records. Whether inspecting shoot logs, message threads, invoice lines, or banking deposits, the owner can query any client or transaction to inspect the exact line numbers and timestamps from the underlying business files."

### Scene 07: Upload Business Files & Ingestion Idempotency (`03:41 - 04:10`)
- **Visual:** Cursor clicks `#nav-uploads`. Header updates to `AXEOM • Upload Business Files`. Shows the drag-and-drop file ingestion zone. Highlights the multi-counter feedback badge (`Added`, `Updated`, `Skipped Duplicates`, `Rejected`). Cursor scrolls down to show the immutable protection banner for baseline Pack 01 records.
- **Narration:**
  > "The Upload Business Files interface provides idempotent, schema-validated CSV ingestion. When new invoices, payments, or client lists are uploaded, the backend returns clear multi-counter feedback: rows added, updated, skipped duplicates, and rejected entries. Re-uploading existing files safely deduplicates records without inflating financial totals, while baseline Pack 01 records remain permanently protected against accidental modification."

### Scene 08: Architecture, Performance & Transparent Jev Status (`04:10 - 04:48`)
- **Visual:** Cursor returns to `#nav-today`. Camera zooms to the infrastructure footer:
  - `Neon Serverless PostgreSQL (AWS us-east-2)`
  - `Vercel Python Serverless WSGI Runtime`
  - `Monthly Operating Cost: $0.00 / month`
  Cursor hovers over the AI Classification status panel, highlighting the active fallback heuristic classifier and the explicit un-evaluated status for external Jev API keys.
- **Narration:**
  > "The technical architecture pairs Python Flask with Neon PostgreSQL on AWS us-east-2, fronted by Vercel serverless functions. Connection pooling and initialization guards ensure rapid response times under zero monthly hosting costs. Regarding AI integration: while the challenge specified Jev classification, external Jev cloud API keys were unavailable. We transparently report the live Jev API as un-evaluated, while deploying a deterministic intent classifier that accurately routes inquiries and categorizes lead urgency with zero latency."

### Scene 09: Live answers.json Export & Schema Compliance (`04:48 - 05:15`)
- **Visual:** Cursor navigates to the top header and clicks `"Export answers.json"`. The file `answers.json` instantly downloads via native browser streaming (HTTP 200, 22 KB). A side callout demonstrates that the exported JSON perfectly matches the official Pack 01 schema, candidate metadata, and verified totals without any disk write operations.
- **Narration:**
  > "Finally, the Export answers.json button triggers an instant, in-memory stream of the complete challenge submission payload. The generated file strictly adheres to the official Pack 01 JSON schema, embedding verified financial totals, client rosters, and candidate metadata without requiring read-only serverless disk writes. The entire test suite of 69 automated tests passes with 100 percent reliability."

---

## PART 2 — CANDIDATE TECHNICAL Q&A (05:15 - 06:57)
*(Mandatory Candidate Executive Briefing — Single Continuous Take)*

### Scene 10: Q&A Segment Transition (`05:15 - 05:34`)
- **Visual:** High-contrast title slide:
  - `PART 2 : EXECUTIVE PRESENTATION`
  - **`CANDIDATE TECHNICAL Q&A`**
  - Subtitle: *Direct Camera-On Engineering Briefing*
  - Candidate: Arslan Tariq (`tsa6648@gmail.com`)
- **Spoken Text:**
  > "We now transition to Part Two: The Candidate Technical Q&A. The Axeom Challenge requires the candidate to personally address three critical engineering questions on camera. Here is the exact technical briefing, detailing the architectural challenges, initial mistakes, and strategic advice for the studio owner."

---

### Scene 11: Question 1 — Hardest Technical Challenge (`05:34 - 06:01`)
- **On-Screen Card:**
  - Tag: `QUESTION 1 : ARCHITECTURAL COMPLEXITY`
  - **Title: "What was the hardest part, and how did you solve it?"**
  - Subtitle: *Identity Resolution & Third-Party Payer Disentanglement*
  - Key Pillars:
    - Decoupling Payer entities (TX Foundation, Horizon Media) from client beneficiaries
    - Normalizing inconsistent client name strings across shoot logs and invoices
    - Preserving strict mathematical invoice provenance without duplicate receivables
- **Exact Candidate Delivery Script (27s):**
  > "The hardest challenge was untangling client identity resolution and third-party payer relationships without corrupting financial totals. Several clients had disparate names across shoot logs, invoices, and payments, while third-party institutions paid bills on behalf of other clients. I solved this by architecting a strict canonical client registry with alias mapping, decoupling the payer entity from the client beneficiary while preserving invoice provenance."

---

### Scene 12: Question 2 — Debugging & Initial Mistakes (`06:01 - 06:32`)
- **On-Screen Card:**
  - Tag: `QUESTION 2 : DEBUGGING & LESSONS LEARNED`
  - **Title: "What did you get wrong at first?"**
  - Subtitle: *Authoritative Truth & Test Fixture Database Contamination*
  - Key Pillars:
    - Assuming the legacy billing export was ground truth (masked 6 software bugs)
    - Early test fixture bug mutating production invoice `INV-1001` ($300 Paid $\to$ $1,000 Unpaid)
    - Solution: Dual-source banking reconciliation & strict branch-isolated QA database
- **Exact Candidate Delivery Script (31s):**
  > "Initially, I assumed the legacy billing software export was authoritative. However, deep reconciliation between bank deposits, invoice schedules, and message logs revealed that the billing tool had six software bugs, falsely flagging unpaid invoices as paid. Furthermore, early test fixtures mutated production invoice INV-1001. I corrected this by implementing rigorous dual-source verification and strictly isolating test mutations to dedicated QA database branches."

---

### Scene 13: Question 3 — Strategic Owner Advice (`06:32 - 06:57`)
- **On-Screen Card:**
  - Tag: `QUESTION 3 : STRATEGIC ADVISORY`
  - **Title: "What would you tell the owner to stop doing?"**
  - Subtitle: *Delivery Before Billing & Informal Lead Intake*
  - Key Pillars:
    - Stop delivering video masters before invoice creation ($2,950 unbilled across 3 clients)
    - Stop informal lead intake: 22 qualified leads lost in August with zero replies
    - Enforce mandatory 24-hour response SLAs & deposit-before-delivery policy
- **Exact Candidate Delivery Script (25s):**
  > "I would tell the owner to immediately stop delivering finished video files before issuing an invoice. Delivering raw work upfront leaked 2,950 dollars across three clients who were never billed. Second, the owner must stop treating inbound inquiries informally: in August alone, 22 qualified leads were lost because messages sat unassigned without a mandatory 24-hour response SLA."

---

### Scene 14: Conclusion & Submission Summary (`06:57 - 07:14`)
- **Visual:** Executive summary slide:
  - `AXEOM CHALLENGE PACK 01 : COMPLETE`
  - **`AXEOM STUDIO OPERATIONS OS`**
  - Status: *100% Reliable, 69/69 Tests Passing, Live on Vercel Edge + Neon PostgreSQL*
  - Candidate: Arslan Tariq (`tsa6648@gmail.com`)
- **Narration:**
  > "In summary, the Axeom Business Intelligence system delivers a robust, secure, and production-ready operations hub for Axeom Studio. All source code, database migrations, test suites, and deliverables are fully committed to GitHub and deployed live on Vercel. Thank you for watching."

---
*End of Video Narration Script.*
