# Axeom Challenge — Requirements Traceability Matrix

This matrix captures all requirements from `Axeom Challenge.pdf`, `PACK.txt`, `answers.json`, and the operational guidelines in `Axeom_Antigravity_Ordered_Prompts.md`.

## Metadata and Constraints

- **Business As-Of Date**: October 6, 2026 (`2026-10-06`). All relative date calculations (e.g., `days_late`, overdue status, request chronologies) use this reference date.
- **Pack ID**: Pack `"01"` (must remain a 2-character text string with leading zero preserved).
- **Elapsed Time Budget**: 72 hours from receipt.
- **Cost Constraint**: Free tools and free tiers only. No paid infrastructure or mandatory credit card commitments.

---

## Requirements Register

| Req ID | Source / Section | Requirement Description | Priority | Planned Implementation | Acceptance Test | Status |
|---|---|---|---|---|---|---|
| **REQ-CORE-01** | PDF p.1, PACK.txt | Preserve Pack ID `"01"` as exact text in answers.json. | P0 | Configuration / constants module. | Validate `answers.json["pack_id"] === "01"`. | Pending (Phase 1 documented) |
| **REQ-CORE-02** | PDF p.1 (Situation) | Enforce fixed business date `2026-10-06` for all calculations. | P0 | Core business date utility (`AS_OF_DATE = datetime.date(2026, 10, 6)`). | Unit test date diffs and aging against `2026-10-06`. | Planned |
| **REQ-DATA-01** | PDF p.1 (Files) | Ingest and parse all 8 original files (`leads.csv`, `bookings.csv`, `invoices.csv`, `payments.csv`, `production_board.csv`, `messages.txt`, `team.csv`, `costs.csv`). | P0 | Ingestion service supporting CSV and raw text message boundary extraction. | Verify 100% records parsed without data loss or corruption. | Planned |
| **REQ-DATA-02** | PDF p.2 (Part 2) | Shared pipeline for original pack and "Add new files". Must accept new files in identical format without code changes. | P0 | Unified file upload handler and schema validator storing raw inputs and persisting state. | Upload test files of each format and verify state recalculation. | Planned |
| **REQ-DATA-03** | PDF p.1 (Messy data) | Canonical client identity resolution linking aliases, emails, and phone numbers without aggressive false merges. | P0 | Deterministic identity resolution engine; ambiguous cases routed to review table. | Run identity checks; verify no false mergers of distinct clients with identical names. | Planned |
| **REQ-DATA-04** | PDF p.1 & answers.json | Identify non-client third-party payers (`payers_who_are_not_clients`). | P1 | Cross-reference payments vs bookings/invoices to isolate external payers. | Verify third-party payer mapping in tests. | Planned |
| **REQ-BIZ-01** | PDF p.2 (Part 1, Q1) | Determine exact real client count and list canonical client records. | P0 | Client identity aggregation service. | Client count matches verified canonical count. | Planned |
| **REQ-BIZ-02** | PDF p.2 (Part 1, Q2) | Reconcile overdue invoices: identify who owes, invoice ID, balance owed, days late, and total overdue. | P0 | Invoice-payment reconciliation matching receipts to invoice balances. | Invariant check: paid + remaining == invoice total. Days late == `(2026-10-06 - due_date)`. | Planned |
| **REQ-BIZ-03** | PDF p.2 (Part 1, Q2) | Reconcile amounts studio owes clients (`we_owe`), including overpayments, credits, refunds. | P1 | Financial credit ledger scanning unapplied payments and overpayments. | Verify individual client credits with reasons. | Planned |
| **REQ-BIZ-04** | PDF p.2 (Part 1, Q2) | Identify completed chargeable work never billed (`never_billed`) and total unbilled amount. | P0 | Cross-audit `bookings.csv` and `production_board.csv` against `invoices.csv`. | Every unbilled booking/month has verified completion status and pricing. | Planned |
| **REQ-BIZ-05** | PDF p.2 (Part 1, Q2) | Identify billing tool discrepancies (`billing_tool_is_wrong`): invoice ID, tool claim, truth, and audit proof. | P0 | Discrepancy detector comparing invoice status vs actual bank payments. | Audit proof verified against `payments.csv` transaction logs. | Planned |
| **REQ-BIZ-06** | PDF p.2 (Part 1, Q3) | Trace lost client requests: video ID, date, channel, why lost, root causes, and month problem worsened. | P0 | Message-to-production correlation engine analyzing timestamps, editor notes, revisions. | Verify timeline evidence proving when lost requests accelerated. | Planned |
| **REQ-BIZ-07** | PDF p.2 (Part 1, Q3 & answers.json) | Identify never-replied leads (`never_replied_leads`). | P1 | Audit `leads.csv` where `first_reply` is empty or missing. | Verify list of `Lxxx` IDs against raw lead data. | Planned |
| **REQ-BIZ-08** | PDF p.2 (Part 1, Q4) | Identify client most likely to leave, concrete evidence, and action to take this week. | P0 | Client health/churn scoring based on revision counts, unaddressed feedback, and sentiment. | Churn justification grounded in documented facts. | Planned |
| **REQ-BIZ-09** | PDF p.2 (Part 1, Q5) | Determine most profitable marketing channel, rationale, and state what the data cannot tell us. | P1 | Marketing channel profitability analysis combining lead revenue and attributable costs. | Document attribution caveats and unknown marketing spends. | Planned |
| **REQ-BIZ-10** | PDF p.2 (Part 1, Q6) | Determine top 3 Monday morning owner actions with ranking justification. | P0 | Action prioritization matrix based on cash urgency, client retention risk, and lead speed. | Ranked list with clear reasoning. | Planned |
| **REQ-APP-01** | PDF p.2 (Part 2) | Live web application accessible on a phone with no login requirement and hard-to-guess URL. | P0 | Public deployment (Flask/HTML/CSS or Streamlit) on free hosting platform. | Open URL on mobile browser without credentials. | Planned |
| **REQ-APP-02** | PDF p.2 (Part 2) | Pass the 10-second test: owner opens on phone and immediately knows the single most urgent action. | P0 | Mobile-first dashboard layout with prominent "First Action" hero card. | User testing: first action identifiable in < 10 seconds. | Planned |
| **REQ-APP-03** | PDF p.2 (Part 2) | "Add new files" button in UI that accepts pack-format files and updates data dynamically. | P0 | Multipart file upload endpoint feeding the unified ingestion pipeline. | Upload new file; observe updated UI totals without server restart. | Planned |
| **REQ-APP-04** | PDF p.2 (Part 2) | Suggest, never act alone: provide draft actions (e.g. reminder drafts) requiring owner approval; no automatic mutations. | P0 | Draft action interface with clear "Draft" labeling and manual copy/approval toggle. | Verify no external webhooks or emails trigger automatically. | Planned |
| **REQ-APP-05** | Prompt 0 / Architecture | Durable persistence across container restarts and file uploads. | P0 | SQLite database (or serverless relational store) persisting state and owner decisions. | Restart application server; confirm uploaded data and decisions persist. | Planned |
| **REQ-JEV-01** | PDF p.2 (Part 3) | Integrate Jev (`https://docs.typesafe.ai`) for at least one meaningful job (e.g. message intent/urgency classification). | P0 | Jev Python SDK (`typesafe-sdk`) or HTTP client with server-side API key handling. | Live API call returns typed Choice/Score/Noul responses. | Planned |
| **REQ-JEV-02** | PDF p.2 (Part 3) | Measure and document Jev accuracy and performance against manually verified benchmark sample. | P0 | Evaluation harness comparing Jev predictions vs ground-truth labels on real messages. | Report sample size, accuracy score (e.g. 36/40), failure cases. | Planned |
| **REQ-JEV-03** | Prompt 0 / Architecture | Graceful fallback and offline resilience for Jev API calls (timeouts, rate limits, missing key). | P1 | Deterministic fallback pipeline with explicit "fallback" labeling; never fabricate API successes. | Run offline test; verify system functions with clear model-unavailable warning. | Planned |
| **REQ-SUB-01** | PDF p.2-3 (Submit) | Complete `answers.json` using exact schema and verified findings. | P0 | Export service validating types against template. | Schema validation test against `answers.json`. | Planned |
| **REQ-SUB-02** | PDF p.2-3 (Submit) | Maximum 2-page rendered writeup (`writeup.md` or PDF). | P0 | Markdown writeup rendered to PDF to ensure strict 2-page limit. | Page count validation (< 2 printed pages). | Planned |
| **REQ-SUB-03** | PDF p.2-3 (Submit) | `assumptions.md` documenting questions we would have asked Axeom and our assumptions. | P0 | Continuous tracking document. | Review assumptions for completeness and business rigor. | Ongoing |
| **REQ-SUB-04** | PDF p.2-3 (Submit) | `daily_log.md` detailing daily actions, pivots, and failures. | P0 | Chronological session journal. | Fact-checked session log. | Ongoing |
| **REQ-SUB-05** | PDF p.2-3 (Submit) | 5–10 minute demonstration video + transcript, answering the 3 reflection questions with camera on, no notes, no cuts. | P0 | Video demo recording plan and script cues. | User records video; transcript generated. | Planned |
| **REQ-SUB-06** | PDF p.2-3 (Submit) | Single submission archive (ZIP or shared folder) containing all deliverables within 72 hours. | P0 | Packaging script excluding secrets, `__pycache__`, and virtualenv. | Verify zip contents against checklist. | Planned |

---

## Scoring Criteria Cross-Reference

1. **Truth**: Ground-truth validation of `answers.json` against actual data relationships.
2. **Functionality**: Live mobile application that ingests new files and recalculates correctly.
3. **Simplicity**: Passing the 10-second mobile test.
4. **Analytical Rigor**: Quality of `writeup.md`, `assumptions.md`, `daily_log.md`, and video responses.
5. **Fast Learning**: Meaningful Jev integration with measured, honest accuracy.
6. **Honesty**: Clear disclosure of limitations, gaps, and unverified data.
