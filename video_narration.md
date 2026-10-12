# Axeom Studio Operations & Business Intelligence OS
## Official Video Narration Script & Technical Production Storyboard (5-Minute Video)

**Candidate:** Arslan Tariq (`tsa6648@gmail.com`)  
**Project:** [https://axeom-business-intelligence.vercel.app](https://axeom-business-intelligence.vercel.app)  
**Repository:** [https://github.com/arslantariq364/axeom-business-intelligence](https://github.com/arslantariq364/axeom-business-intelligence)  
**Video Duration:** **5 minutes 12 seconds (`05:12`)**  
**Video File:** `axeom_final_demo.mp4` (1080p Full HD, 30 fps, H.264 / AAC)  
**Business Reference Date:** October 6, 2026 (`2026-10-06`)  
**Format:** 100% Live browser walkthrough with continuous cursor navigation and studio AI narration. Zero slides, zero still photos, zero blurred backgrounds.

---

## 5-Minute Scene Breakdown & Timing

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
| **09** | Export answers.json | `04:48 - 05:12` | 24s | Direct browser-streamed in-memory JSON export adhering strictly to Pack 01 schema |

---

## Verbatim Walkthrough Script

### Scene 01: Introduction & Challenge Pack 01 Overview (`00:00 - 00:36`)
> "Welcome to the Axeom Studio Business Intelligence and Operations Dashboard. This demonstration provides an executive technical walkthrough of our solution for Axeom Challenge Pack 01. The system is live in production on Vercel Edge, backed by a dual-engine database architecture using Neon Serverless PostgreSQL and local SQLite. All business calculations are anchored to the strict business reference date of October 6th, 2026. Please note that this initial walkthrough utilizes clear AI-assisted narration to guide you through the operational dashboard and data architecture."

### Scene 02: Today View — Owner Command Center & Monday Triage (`00:36 - 01:20`)
> "Here on the Today view, the studio owner is immediately presented with high-priority operational decisions rather than raw data tables. The hero action card highlights Patel Insurance Group, where a 600-dollar retainer from August 2026 is currently overdue. Below the hero card, our triage engine computes the Monday Top Three priorities: first, recovering a 1,000-dollar overdue shoot from Southside Athletics; second, addressing contract renewal and unbilled deliverables for Sarah Jenkins; and third, resolving a 750-dollar unbilled commercial shoot for Metroplex Logistics. The owner can click Approve, Defer, or In Progress to persist triage decisions directly into PostgreSQL."

### Scene 03: Money View — Financial Intelligence & Leakage Reconciliation (`01:20 - 02:06`)
> "Navigating to the Money view reveals the core financial reconciliation engine. Our audit uncovered 9,250 dollars in overdue unpaid invoices across nine separate accounts. Simultaneously, we identified 2,400 dollars owed back to clients, including a 1,200-dollar credit for Summit Dental due to weather cancellations, and a 1,200-dollar credit for Highland Park. Crucially, the system exposed 2,950 dollars in completed work that was delivered but never invoiced, spanning Oakridge High, Trinity Presbyterian, and Downtown Arts. Furthermore, our cross-table audit flagged six software discrepancies where the legacy billing tool falsely marked unpaid invoices as settled."

### Scene 04: Clients View — Canonical Identity & Third-Party Payers (`02:06 - 02:41`)
> "The Clients view manages our canonical directory of exactly 29 active clients, designated C01 through C29. A critical data integrity challenge in Axeom Studio was distinguishing actual clients from third-party funding entities. For instance, entities like Texas Community Foundation, Horizon Media Group, and Northpoint Parent LLC act as third-party payers rather than client accounts. Our identity resolution service disentangles these aliases while linking complete production dossiers, tracking shoots, invoices, and payment histories per client."

### Scene 05: Requests & Leads View — Operational Leakage & August Cliff (`02:41 - 03:16`)
> "In the Requests and Leads view, we analyze operational leakage. Out of 118 total inquiries, 33 requests were lost. Our root cause classification attributes 14 losses to pricing friction, 11 to slow response turnaround, and 8 to scheduling conflicts. More alarmingly, the data reveals an August 2026 cliff, where 22 qualified inquiries went completely unanswered due to the absence of an automated intake workflow. Every lead is indexed with response latency, stage tracking, and estimated revenue impact."

### Scene 06: Evidence Register & Provenance Tracking (`03:16 - 03:41`)
> "Data trust requires verifiable proof. Our Evidence Search view maintains an exhaustive cross-reference register connecting every financial metric and operational claim to source records. Whether inspecting shoot logs, message threads, invoice lines, or banking deposits, the owner can query any client or transaction to inspect the exact line numbers and timestamps from the underlying business files."

### Scene 07: Upload Business Files & Ingestion Idempotency (`03:41 - 04:10`)
> "The Upload Business Files interface provides idempotent, schema-validated CSV ingestion. When new invoices, payments, or client lists are uploaded, the backend returns clear multi-counter feedback: rows added, updated, skipped duplicates, and rejected entries. Re-uploading existing files safely deduplicates records without inflating financial totals, while baseline Pack 01 records remain permanently protected against accidental modification."

### Scene 08: Architecture, Performance & Transparent Jev Status (`04:10 - 04:48`)
> "The technical architecture pairs Python Flask with Neon PostgreSQL on AWS us-east-2, fronted by Vercel serverless functions. Connection pooling and initialization guards ensure rapid response times under zero monthly hosting costs. Regarding AI integration: while the challenge specified Jev classification, external Jev cloud API keys were unavailable. We transparently report the live Jev API as un-evaluated, while deploying a deterministic intent classifier that accurately routes inquiries and categorizes lead urgency with zero latency."

### Scene 09: Live answers.json Export & Schema Compliance (`04:48 - 05:12`)
> "Finally, the Export answers.json button triggers an instant, in-memory stream of the complete challenge submission payload. The generated file strictly adheres to the official Pack 01 JSON schema, embedding verified financial totals, client rosters, and candidate metadata without requiring read-only serverless disk writes. The entire test suite of 69 automated tests passes with 100 percent reliability."

---

## Candidate Interview Reference Guide (For Live Camera-On Presentation)

*The challenge requires answering these 3 questions directly to the camera in one continuous unedited take without notes.*

### Question 1: *"What was the hardest part, and how did you solve it?"* (27s)
> *"The hardest challenge was untangling client identity resolution and third-party payer relationships without corrupting financial totals. Several clients had disparate names across shoot logs, invoices, and payments, while third-party institutions paid bills on behalf of other clients. I solved this by architecting a strict canonical client registry with alias mapping, decoupling the payer entity from the client beneficiary while preserving invoice provenance."*

### Question 2: *"What did you get wrong at first?"* (31s)
> *"Initially, I assumed the legacy billing software export was authoritative. However, deep reconciliation between bank deposits, invoice schedules, and message logs revealed that the billing tool had six software bugs, falsely flagging unpaid invoices as paid. Furthermore, early test fixtures mutated production invoice INV-1001. I corrected this by implementing rigorous dual-source verification and strictly isolating test mutations to dedicated QA database branches."*

### Question 3: *"What would you tell the owner to stop doing?"* (25s)
> *"I would tell the owner to immediately stop delivering finished video files before issuing an invoice. Delivering raw work upfront leaked 2,950 dollars across three clients who were never billed. Second, the owner must stop treating inbound inquiries informally: in August alone, 22 qualified leads were lost because messages sat unassigned without a mandatory 24-hour response SLA."*
