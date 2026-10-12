# Axeom Challenge — Questions, Assumptions, Evidence & Risk Register

Per the challenge brief:
> *"You can't ask us questions. That's on purpose. Write down every question you would have asked, and what you decided to assume instead. Good assumptions count."*

This document logs all business, financial, operational, and technical questions, our documented assumptions, the evidence justifying them, and associated risks.

---

## 1. Business & Operational Questions

### Q1: What constitutes a "Real Client"?
- **Question for Owner**: Does a client mean anyone who submitted a lead inquiry, booked studio time, received video editing services, or paid an invoice? Specifically, are one-time podcast studio rentals considered clients, or only recurring video editing accounts?
- **Our Working Assumption**: Any individual or company that booked chargeable services or had video production work performed is a "client." Inquiries in `leads.csv` that resulted in no bookings, shoots, or invoices are classified as "unconverted leads," not clients.
- **Evidence**: `bookings.csv` and `production_board.csv` represent actual operational delivery.
- **Risk & Mitigation**: Risk of over-counting or under-counting depending on whether dead leads are counted. Mitigation: `clients` list will clearly trace every client to specific booking/production records.

### Q2: Third-Party Payers vs. Client Entities
- **Question for Owner**: When a payment is made by an individual or company whose name differs from the invoice or booking name (e.g. sponsor, spouse, parent company), is that payer considered a separate client?
- **Our Working Assumption**: Third-party payers who only appear in `payments.csv` and have no direct bookings or production projects are classified under `payers_who_are_not_clients`. They are linked to the canonical client whose invoices they paid.
- **Evidence**: `answers.json` contains a distinct `payers_who_are_not_clients` schema explicitly designed for this scenario.
- **Risk & Mitigation**: Conflating payers with clients could distort `client_count`. Separating them preserves identity integrity.

### Q3: Discrepancy Between Invoices and Bank Receipts
- **Question for Owner**: If an invoice in `invoices.csv` is marked "paid", but there is no corresponding record in `payments.csv`, or conversely if `payments.csv` shows full payment but `invoices.csv` says "unpaid", which source is the financial truth?
- **Our Working Assumption**: The bank account (`payments.csv`) represents cash reality. The billing tool (`invoices.csv`) is software prone to human error or synchronization lag. Where `payments.csv` has a cleared transaction referencing an invoice, that invoice is treated as paid, and the billing tool is flagged as inaccurate in `billing_tool_is_wrong`.
- **Evidence**: The PDF notes: *"He doesn't know who really owes him money... Some files disagree with each other. Some files are wrong."*
- **Risk & Mitigation**: Misallocating funds. Mitigation: Document explicit payment ID and date for every discrepancy claim.

### Q4: Completed Chargeable Work Never Invoiced
- **Question for Owner**: Are all completed bookings in `bookings.csv` expected to have a matching invoice in `invoices.csv`? What about video edits on the `production_board.csv`?
- **Our Working Assumption**: Bookings marked `status == 'completed'` with a positive price that have no matching invoice in `invoices.csv` constitute unbilled revenue (`never_billed`). Video revisions included within standard shoot scopes or retainers are not billed separately unless explicitly indicated by costs/rates.
- **Evidence**: `costs.csv` notes studio hourly rates and editor pay, while `bookings.csv` lists distinct service packages.
- **Risk & Mitigation**: Invoicing work that was intended to be complimentary. Mitigation: Cross-check booking service types against discount memos in `messages.txt` before claiming unbilled revenue.

### Q5: "Lost Client Requests" Definition
- **Question for Owner**: What defines a "lost request"? Is it an email/message that never received a reply, or an edit note that was never reflected in the final video deliverable?
- **Our Working Assumption**: A lost request is client edit feedback communicated via message (email, WhatsApp, Instagram, voice note) regarding a specific video (`Vxxx`) that was either ignored, missed by the assigned editor, or contradicted in the final deliverable.
- **Evidence**: `messages.txt` contains client messages like *"Can roof inspection walkthrough have a calmer song?..."*, while `production_board.csv` notes what revisions occurred.
- **Risk & Mitigation**: Subjective interpretation. Mitigation: Ground each lost request in an exact message timestamp, video ID, and documented absence on the production board.

---

## 2. Technical & Architecture Assumptions

### Q6: Business Reference Time Horizon
- **Assumption**: All aging calculations (e.g. `days_late`) are anchored to `2026-10-06`. Records dated after `2026-10-06` (if any) are flagged as post-reference events.
- **Justification**: Nonnegotiable constraint from `Axeom Challenge.pdf` and Prompt 0.

### Q7: Date Formats Across Disparate Files
- **Assumption**: Date formats are heterogeneous:
  - `bookings.csv`: `DD/MM/YYYY` (e.g. `04/03/2026` for March 4, 2026 or April 3, 2026; confirmed by entries like `16/04/2026` in `payments.csv`).
  - `invoices.csv`: `YYYY-MM-DD`.
  - `leads.csv`: `YYYY-MM-DD HH:MM`.
  - `messages.txt`: `[YYYY-MM-DD HH:MM]`.
- **Justification**: Observed syntax in raw CSV files. Strict multi-format parsing is required to prevent month/day transposition errors.

### Q8: Public Access & Phone Friendly Requirement
- **Assumption**: Evaluators will inspect the application using mobile browsers without logging in. The system will run on a publicly accessible web host with a random, unguessable path or URL.
- **Justification**: PDF Part 2 explicitly specifies: *"A real link that works on a phone... No login. Use a hard-to-guess link instead (the data is fake)."*

---

## 3. Technology & Dependency Assumptions

### Q9: Architecture Selection (Flask + Vanilla HTML/CSS vs. Streamlit)
- **Assumption**: Flask with lightweight HTML/CSS is recommended over Streamlit.
- **Justification**:
  1. Streamlit mobile UI has viewport lag, heavy bundle size (>200MB dependencies), and full-script reruns on every button click, which risks failing the 10-second test.
  2. Flask offers instant page loads (<50ms), pinpoint mobile-responsive styling, native multipart file uploads, and a tiny memory footprint (<30MB RAM) on resource-constrained free hosts.
  3. SQLite provides durable ACID storage that survives process restarts.

### Q10: Jev Model Availability & Fallback
- **Assumption**: The Jev model (`jev-1.13.0` / `POST https://api.typesafe.ai/v1/systemone`) will be used to classify client messages by intent and urgency.
- **Justification**: Official documentation at `https://docs.typesafe.ai` demonstrates the `Choice` and `Noul` primitives for message routing.
- **Contingency / Blocker**: Requires `TYPESAFE_API_KEY`. If the candidate has not yet generated an API key from `console.typesafe.ai`, a deterministic fallback classifier will provide operational continuity while explicitly disclosing the pending account step without fabricating model calls.

---

## 4. Phase 2 Discovered Identity Facts & Confirmations

### Q11: Rebrand vs. New Client (Elevate Fitness $\to$ Elevate Athletics)
- **Finding & Evidence**: On `2026-08-01 21:37`, Jordan Reed sent an email from `jordan@elevatefit.co`: *"Big news: Elevate Fitness is now Elevate Athletics! New email is jordan@elevateathletics.com."* Both accounts share phone `469-555-0133`.
- **Decision**: Merged into single canonical client **Elevate Athletics** (`C19`).

### Q12: Homonym Businesses (Lone Star Realty vs. Lonestar Realty Group)
- **Finding & Evidence**: Dana Brooks (`dana@lonestarrealty.com`, `214-555-0164`, Lead `L037`) vs. Greg Whitfield (`greg@lonestarrg.com`, `817-555-0119`, Lead `L069`).
- **Decision**: Maintained strictly separate as **Lone Star Realty** (`C20`) and **Lonestar Realty Group** (`C28`). Merging them would be an incorrect false merge.

### Q13: Agency Third-Party Payer (Brightline Marketing)
- **Finding & Evidence**: On `2026-06-08 17:53`, Kelsey Moore emailed: *"Hi, Kelsey from Brightline Marketing. Please bill us (Brightline) for Greenway Pediatrics and Summit Chiropractic. We pay monthly."*
- **Decision**: `BRIGHTLINE MARKETING LLC` is recorded under `payers_who_are_not_clients`. The actual clients receiving video production are **Greenway Pediatrics** (`C26`) and **Summit Chiropractic** (`C27`).

### Q14: Email Domain Typo (`sarah@khandental.con`)
- **Finding & Evidence**: Booking `B045` records email `sarah@khandental.con` with client name `Khan Dental` for `Content Day` ($1,500).
- **Decision**: Mapped to canonical client **Khan Dental** (`C04`, Dr. Sarah Khan).

---

## 5. Phase 3 Financial, Operational & Marketing Assumptions

### Q15: Heterogeneous Date Parsing Standards
- **Finding & Evidence**: `bookings.csv` dates follow `MM/DD/YYYY` (96 entries have day > 12 in the second position, e.g. `04/13/2026`), whereas `payments.csv` dates follow `DD/MM/YYYY` (e.g. `16/04/2026`). Invoices use ISO `YYYY-MM-DD`.
- **Decision**: Implemented dedicated, file-specific date parsers to prevent critical transposition errors.

### Q16: Unreferenced Batch Payments
- **Finding & Evidence**: Payment `P5110` ($900.00 on 2026-09-04) from Tasha Green contained no reference string, but Tasha emailed on 2026-08-10 asking: *"Can I pay the August sessions together at the start of September?"*
- **Decision**: Reconciled $300.00 each against August session invoices `INV-1093`, `INV-1103`, and `INV-1106`. All three are confirmed paid, and the billing tool marking them unpaid is flagged as inaccurate.

### Q17: Partially Paid Invoices
- **Finding & Evidence**: Tony Russo / Prime Roofing sent payment `P5118` ($450.00 on 2026-09-28) with message: *"Sent half. Rest when the next batch is done."* The invoice `INV-1125` was for $900.00.
- **Decision**: Recorded net remaining balance of $450.00 under `overdue` (19 days late), not the gross amount of $900.00.

### Q18: Retainer Bookings vs. Unbilled Work
- **Finding & Evidence**: Retainer clients (Torres Law Firm, Patel Insurance Group, Meridian Wealth Partners, Apex Physical Therapy) have shoot bookings in `bookings.csv` with price `$0` or `0`.
- **Decision**: These shoots are covered under contractual monthly retainer invoices ($2,500/month) and are not unbilled per-booking sessions.

### Q19: Client Liabilities (We Owe)
- **Finding & Evidence**:
  1. Glow Aesthetics was billed $900 on `INV-1086` and paid twice via `P5091` and `P5093` ($900 overpayment).
  2. Lone Star Realty paid $1,500 on `INV-1135` for shoot `B148`, which was cancelled on 2026-09-24 due to a family emergency. Axeom subsequently billed and collected another $1,500 on `INV-1143` without applying credit.
- **Decision**: Documented both as verified liabilities under `we_owe` totaling $2,400.00.

### Q20: Marketing Profitability & Missing Ad Spend
- **Finding & Evidence**: `costs.csv` provides studio hourly rates ($40/hr) and editor wages, but completely lacks advertising spend data (Meta ad budgets, Google PPC spend).
- **Decision**: Calculated channel gross profit as collected revenue minus direct delivery costs (studio time + editor hours). Named `Website form` as top channel for highest gross profit ($11,424.70) and 61% margin, while noting `Referral` had the highest conversion rate (71.4%). Disclosed missing ad spend under `what_this_data_cannot_tell_us`.

### Q21: Churn Risk Evaluation
- **Finding & Evidence**: Nina Patel submitted a website form inquiry (L097) and follow-up email explicitly requesting to discuss contract continuation, both left unanswered. Raj Patel sent multiple angry messages over branding compliance and unfixed edits. Retainer invoice `INV-1122` ($2,500) was withheld.
- **Decision**: Designated **Patel Insurance Group** as `most_likely_to_leave` due to imminent risk to Axeom's largest retainer ($2,500/mo), mirroring Paul Grant's July cancellation.

### Q22: Typesafe AI (Jev) API Key Access & Deterministic Fallback Distinction
- **Finding & Evidence**: The production request schema (`POST https://api.typesafe.ai/v1/systemone`, model `jev-latest`, application question version `axeom-intent-v2.0`, `choice` + `noul` primitives), server-side secret isolation, persistent SHA-256 caching, and deterministic fallback (96.0% accuracy on genuine 25-item held-out test set) are fully implemented. However, the `TYPESAFE_API_KEY` environment variable is not configured in this environment.
- **Decision**: Live Jev evaluation and live API call status are strictly recorded as **"Not evaluated"** (blocked by missing account credentials). Fallback classifications are explicitly labeled as `deterministic_fallback` across the database, REST API, and dashboard, and must never be described as Jev accuracy. Once credentials are provided, `reprocess_fallback_classifications()` and the live caller activate immediately without code changes.


