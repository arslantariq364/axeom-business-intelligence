# Axeom Studio — Phase 3 Evidence, Calculations & Reconciliation Report

**As-of Reference Date**: October 6, 2026  
**Dataset Reference**: Pack 01 (`PACK.txt`)  
**Scope**: Complete financial reconciliation, operational audit, client churn evaluation, marketing efficiency analysis, and immediate owner action plan.

---

## 1. Executive Summary of Financial & Operational Metrics

| Metric | Measured Value | Unit / Format | Status / Verification Method |
|---|---|---|---|
| **Canonical Client Count** | **29** | Deduplicated businesses | Cross-entity reconciliation across 8 source files (Phase 2 canonical inventory). |
| **Third-Party Agency Payers** | **1** (`BRIGHTLINE MARKETING LLC`) | Agency payer entity | Verified payer paying on behalf of Greenway Pediatrics & Summit Chiropractic. |
| **Overdue Receivables** | **$9,250.00** | Net balance past due | Exactly 9 invoices with outstanding balances past due date as of 2026-10-06. |
| **We Owe (Client Liabilities)** | **$2,400.00** | Client credit / refund | Glow Aesthetics ($900 double payment) + Lone Star Realty ($1,500 cancelled shoot). |
| **Never Billed Earned Work** | **$2,950.00** | Unbilled completed shoots | Exactly 3 completed chargeable sessions (DFW Founders B136, Ironclad B123, Vega B144). |
| **Billing Tool Discrepancies** | **6** | Invoices with false status | 1 invoice falsely marked paid (`INV-1066`) + 5 fully paid invoices falsely marked unpaid. |
| **Lost Edit Requests** | **33** | Documented video edits | Client change orders communicated via chat/voice notes but omitted from board notes. |
| **Request Failure Inflection Month** | **`2026-08`** | ISO Year-Month (`YYYY-MM`) | Complaints doubled in August (6) following Sam's hire (July 20), peaking in Sept (13). |
| **Unreplied Incoming Leads** | **22** | Abandoned lead records | Inbound inquiries with empty `first_reply` in `leads.csv` (including Nina Patel L097). |
| **Highest Churn Risk Client** | **Patel Insurance Group** | $2,500/mo retainer client | Nina Patel contract review request unreplied; Raj Patel angry over branding; $2.5k withheld. |
| **Most Profitable Marketing Channel** | **Website form** | Acquisition channel | Generated highest gross profit ($11,424.70) at 61.0% margin; Referral had top conv (71.4%). |

---

## 2. Invoices & Payments Reconciliation

### 2.1 Ledger Invariants & Audit Method
- **Total Invoices**: 152 invoices in `invoices.csv` ($157,690.00 gross face value).
- **Total Payments**: 131 payments in `payments.csv` ($119,790.00 total cash collected).
- **Date Conventions**:
  - `invoices.csv`: ISO format (`YYYY-MM-DD`).
  - `payments.csv`: Day-Month-Year format (`DD/MM/YYYY`).
  - `bookings.csv`: Month-Day-Year format (`MM/DD/YYYY`).
  - All days late calculated as: `days_late = (2026-10-06 - invoice.due).days`.

### 2.2 Complete Itemization of Overdue Invoices ($9,250.00 Total)

As of October 6, 2026, exactly 9 invoices have unpaid balances past their contractual due date:

| Invoice # | Client Name / Bill-To | Due Date | Days Late | Gross Amount | Payments Applied | Net Amount Owed | Underlying Shoot / Service Memo |
|---|---|---|---|---|---|---|---|
| `INV-1066` | Crown Barbers | 2026-07-18 | **80 days** | $900.00 | $0.00 | **$900.00** | Reels Pack shoot B068. Tool reports paid, but 0 payments received (`P5030` paid `INV-1029`). |
| `INV-1104` | Lonestar Realty Group | 2026-08-26 | **41 days** | $1,500.00 | $0.00 | **$1,500.00** | Content Day shoot B107 on 2026-08-12. Email 2026-09-12 promised accounting would pay. |
| `INV-1112` | H&H Podcast | 2026-09-09 | **27 days** | $300.00 | $0.00 | **$300.00** | Podcast Studio 2hr shoot B114 on 2026-08-26. |
| `INV-1119` | Mike's Roofing LLC | 2026-09-15 | **21 days** | $900.00 | $0.00 | **$900.00** | Reels Pack shoot B124 on 2026-09-01. |
| `INV-1120` | Angela Price (TLC Home Care) | 2026-09-15 | **21 days** | $1,500.00 | $0.00 | **$1,500.00** | Content Day shoot B127 on 2026-09-01. Client withheld payment until videos posted. |
| `INV-1122` | Patel Ins | 2026-09-15 | **21 days** | $2,500.00 | $0.00 | **$2,500.00** | Monthly Retainer for September 2026. Withheld due to branding compliance dispute. |
| `INV-1123` | Hustle & Heart | 2026-09-16 | **20 days** | $300.00 | $0.00 | **$300.00** | Podcast Studio 2hr shoot B122 on 2026-08-31. |
| `INV-1125` | Prime Roofing Co | 2026-09-17 | **19 days** | $900.00 | $450.00 (`P5118`) | **$450.00** | Reels Pack shoot B130. Tony Russo paid half ($450 on 2026-09-28); $450 remains unpaid. |
| `INV-1130` | Brightline Marketing | 2026-09-29 | **7 days** | $900.00 | $0.00 | **$900.00** | Reels Pack shoot B139 for Summit Chiropractic. |
| **TOTAL** | | | | **$9,700.00** | **$450.00** | **$9,250.00** | |

$$\sum \text{amount\_owed} = 900 + 1500 + 300 + 900 + 1500 + 2500 + 300 + 450 + 900 = \mathbf{\$9,250.00}$$

### 2.3 Independent Proof on Unpaid Invoices Due After Reference Date
Nine additional invoices have unpaid balances totaling $9,440.00, but their contractual due dates fall *after* October 6, 2026. These are strictly not overdue as of the reference date:
1. `INV-1137` | Hustle & Heart | $300.00 | Due 2026-10-07 (in 1 day)
2. `INV-1140` | Hustle and Heart | $300.00 | Due 2026-10-12 (in 6 days)
3. `INV-1144` | Mike's Roofing | $900.00 | Due 2026-10-15 (in 9 days)
4. `INV-1145` | Ironclad Fitness | $900.00 | Due 2026-10-15 (in 9 days)
5. `INV-1146` | Torres Law | $2,500.00 | Due 2026-10-15 (in 9 days)
6. `INV-1147` | Raj Patel | $2,500.00 | Due 2026-10-15 (in 9 days)
7. `INV-1149` | NorthPoint DFW | $240.00 | Due 2026-10-16 (in 10 days)
8. `INV-1150` | Prime Roofing | $900.00 | Due 2026-10-16 (in 10 days)
9. `INV-1151` | Oaklane Dental | $1,500.00 | Due 2026-10-20 (in 14 days)

---

## 3. Discrepancies & Liabilities

### 3.1 What We Owe (`we_owe` — $2,400.00 Total)

Axeom holds cash liabilities totaling **$2,400.00** to two clients:

1. **Glow Aesthetics (Nadia Hassan) — $900.00 Overpayment**
   - **Transaction Trace**: Invoice `INV-1086` was issued on 2026-07-28 for $900.00 (Reels Pack shoot B078).
   - **Payments Received**:
     - `P5091` on 08/08/2026 ($900.00, method Stripe, ref `INV-1086`)
     - `P5093` on 09/08/2026 ($900.00, method Stripe, ref `INV-1086`)
   - **Proof**: Glow Aesthetics was billed $900.00 but paid twice ($1,800.00 collected). Across all 4 invoices issued to Glow Aesthetics (`INV-1025` $900, `INV-1044` $900, `INV-1065` $900, `INV-1086` $900 = $3,600 total billed), Axeom collected $4,500 across 5 payments (`P5024`, `P5044`, `P5065`, `P5091`, `P5093`). Axeom holds a net cash surplus of **$900.00** owed to the client.

2. **Lone Star Realty (Dana Brooks) — $1,500.00 Prepaid Unperformed Shoot Credit**
   - **Transaction Trace**: Shoot `B148` (Content Day, $1,500) was scheduled for 2026-09-24 and billed on invoice `INV-1135` ($1,500.00).
   - **Payment Received**: Dana Brooks paid $1,500.00 on 2026-09-24 (`P5122`).
   - **Cancellation & Reschedule**: On 2026-09-24 at 18:08, Dana messaged via WhatsApp: *"We have to cancel today's shoot, family emergency. Can we move it? We already paid."*
   - **Double Billing**: The shoot was rescheduled as `B152` on 2026-09-30. However, Axeom issued a *new* invoice `INV-1143` for $1,500.00 and collected another $1,500.00 (`P5130` on 2026-09-30).
   - **Proof**: Dana paid $3,000.00 for a single completed Content Day session. Axeom owes Lone Star Realty a **$1,500.00** credit or refund for the cancelled shoot B148.

### 3.2 Completed Work Never Billed (`never_billed` — $2,950.00 Total)

Cross-referencing all 163 completed bookings on `bookings.csv` and 333 completed video assets on `production_board.csv` against `invoices.csv` identifies exactly three completed chargeable sessions that were never invoiced:

| Client | Booking ID | Shoot Date | Service Delivered | Chargeable Rate | Verification Proof |
|---|---|---|---|---|---|
| **DFW Founders Podcast** | `B136` | 2026-09-11 | Podcast Studio 4hr | **$550.00** | Status is `completed` in `bookings.csv`. Standard 4hr podcast rate is $550 (e.g., `INV-1094`, `INV-1107`, `INV-1121`). Zero invoice exists in `invoices.csv` referencing B136 or issued for DFW Founders on 2026-09-11. |
| **Ironclad Gym** | `B123` | 2026-08-31 | Reels Pack | **$900.00** | Shoot completed on 2026-08-31. Produced 3 completed reels on production board (`V253`, `V254`, `V255` all marked Delivered). Marcus Webb paid for shoot B092 (`INV-1090`) and B149 (`INV-1145`), but shoot B123 was never invoiced. |
| **Vega Auto Detailing** | `B144` | 2026-09-18 | Content Day | **$1,500.00** | Carlos Vega booked Content Day on 2026-09-18. Produced 4 videos (`V304`, `V305`, `V306`, `V307` all Delivered). Invoices exist for B066 (`INV-1064` $900) and B112 (`INV-1118` $900), but B144 ($1,500 Content Day) was never billed. |
| **TOTAL** | | | | **$2,950.00** | |

$$\sum \text{unbilled\_amount} = 550.00 + 900.00 + 1500.00 = \mathbf{\$2,950.00}$$

> [!NOTE]
> Retainer client shoot bookings (Torres Law, Patel Insurance, Meridian Wealth, Apex PT) have `$0` listed in `bookings.csv`. These are covered under fixed $2,500/month retainer invoices and are not unbilled per-booking work.

### 3.3 Billing Tool Software Errors (`billing_tool_is_wrong` — 6 Cases)

Comparing status flags in `invoices.csv` against actual bank transactions in `payments.csv` reveals exactly 6 critical billing tool errors:

1. **`INV-1066` (Crown Barbers)**:
   - *Tool Says*: `paid`
   - *Truth*: `unpaid` ($900.00 balance outstanding)
   - *How You Know*: Tool reports paid, but `payments.csv` contains zero receipts for `INV-1066`. The only payment ever received from Crown Barbers was `P5030` ($900 on 2026-05-18), which paid earlier invoice `INV-1029`. `INV-1066` was issued on 2026-07-04 and never paid.

2. **`INV-1093` (Hustle & Heart Podcast)**:
   - *Tool Says*: `unpaid`
   - *Truth*: `paid` ($0.00 balance)
   - *How You Know*: Tool reports unpaid, but Tasha Green emailed on 2026-08-10 asking to batch August sessions into September. Batch payment `P5110` ($900.00) was received on 2026-09-04 covering `INV-1093` ($300), `INV-1103` ($300), and `INV-1106` ($300) in full.

3. **`INV-1097` (Mike's Roofing LLC)**:
   - *Tool Says*: `unpaid`
   - *Truth*: `paid` ($0.00 balance)
   - *How You Know*: Tool reports unpaid, but payment `P5107` ($900.00) was received on 2026-09-02 with explicit reference `"INV-1097"`. The billing software failed to match and clear the invoice.

4. **`INV-1103` (H&H Podcast)**:
   - *Tool Says*: `unpaid`
   - *Truth*: `paid` ($0.00 balance)
   - *How You Know*: Tool reports unpaid, but batch payment `P5110` ($900.00 on 2026-09-04) covered this August session ($300.00) in full per client agreement.

5. **`INV-1106` (Tasha Green)**:
   - *Tool Says*: `unpaid`
   - *Truth*: `paid` ($0.00 balance)
   - *How You Know*: Tool reports unpaid, but batch payment `P5110` ($900.00 on 2026-09-04) covered this August session ($300.00) in full per client agreement.

6. **`INV-1117` (Harbor Coffee Roasters)**:
   - *Tool Says*: `unpaid`
   - *Truth*: `paid` ($0.00 balance)
   - *How You Know*: Tool reports unpaid, but payment `P5117` ($900.00) was received on 2026-09-11 with explicit reference `"INV-1117"`.

---

## 4. Operational Failure Audit: Lost Edit Requests

### 4.1 Root Cause Analysis (`lost_requests_root_causes`)
1. **Communication Channel Fragmentation**: Client edit requests arrive across 4 separate, unintegrated platforms: Email (88 messages), WhatsApp direct chats (85 messages), Voice Notes (23 messages), and Instagram Direct Messages (9 messages). Without a unified intake desk or ticketing system, feedback is siloed.
2. **Untranscribed Voice Notes & Neglected Social Inboxes**: Clients frequently send spoken instructions via WhatsApp voice notes (e.g. Mike Delgado, Paul Grant, Raj Patel, Dr. Sarah Khan). These were listened to casually on mobile but never transcribed or transferred into project management cards on `production_board.csv`. Similarly, Instagram DMs (@khansautospa, @lunabridaldfw, @ironcladgymtx) were ignored by production staff.
3. **Absence of Centralized Ticketing / Blank Task Cards**: Instructions live in personal messaging threads between the owner and clients rather than being attached to the video card on `production_board.csv`. For 33 videos, `notes_on_board` remained completely blank, leaving editors to edit without knowing client requirements.
4. **Editor Scaling & Onboarding Breakdown**: The hiring of junior editor Sam on July 20, 2026 ($22/hr) and freelance editor Dev on September 1, 2026 ($40/hr) occurred without style guides, client branding sheets, or standardized handoff processes. Revision loops surged:
   - Ali: 0.44 avg revisions/video (120 videos, 53 revs)
   - Rita: 0.55 avg revisions/video (129 videos, 71 revs)
   - Sam: 0.81 avg revisions/video (70 videos, 57 revs)
   - Dev: 1.21 avg revisions/video (14 videos, 17 revs)
5. **No Structured QA Approval Gate**: Edited video drafts were delivered back to clients without any internal quality check against the client's original feedback, causing clients to complain repeatedly about identical unaddressed issues.

### 4.2 Timeline Analysis (`lost_requests_started_getting_worse_in`)
- **Inflection Point**: **`2026-08`**
- **Evidence**:
  - April 2026: 1 complaint
  - May 2026: 4 complaints
  - June 2026: 5 complaints
  - July 2026: 3 complaints (Paul Grant churned on July 20: *"Too many rounds of fixes, and my notes keep getting missed"*)
  - **August 2026**: **6 complaints** — doubled from July as junior editor Sam took on full video editing volume. Multiple clients (Greg Whitfield at Lonestar RG, Kim Lee at Apex PT, Alan Cho at Greenway Peds) suffered missed notes.
  - **September 2026**: **13 complaints** — surged to more than double August and quadruple July as freelance editor Dev joined, creating severe bottlenecks across Patel Insurance, TLC Home Care, Prime Roofing, and Luna Bridal.

### 4.3 Verified Lost Request Register (33 Items)

Every item below links an explicit client edit request to a specific video ID on `production_board.csv` where the instruction was omitted from board notes or ignored:

| Video ID | Request Date | Channel (`came_by`) | Target Video Title & Client | Why It Was Lost |
|---|---|---|---|---|
| `V010` | 2026-04-24 | `voice note` | Hail claim help (Mike's Roofing) | Voice note from Mike requesting bigger captions was never transcribed or transferred to the board; `notes_on_board` remained blank. |
| `V019` | 2026-05-04 | `voice note` | Why fees matter (Meridian Wealth) | Voice note from Paul requesting brand color pink was never added to the production board; `notes_on_board` remained blank. |
| `V022` | 2026-05-04 | `voice note` | Retirement myths (Meridian Wealth) | Voice note from Paul requesting end phone number was omitted from board notes, leaving editor Rita without instructions. |
| `V044` | 2026-05-16 | `voice note` | Estate planning basics (Meridian) | Voice note from Paul requesting removal of spoken stumble was never logged on production board notes. |
| `V020` | 2026-05-19 | `voice note` | College savings (Meridian Wealth) | Voice note from Paul requesting face blur for non-release client was never transcribed to board notes. |
| `V210` | 2026-05-28 | `whatsapp` | Why bundle home and auto (Patel Ins) | Edit request for brand color navy sent via WhatsApp was not logged onto production board notes. |
| `V329` | 2026-06-06 | `voice note` | Open house recap (Lone Star Realty) | Voice note from Dana requesting removal of price discussion was not transcribed or added to production board. |
| `V238` | 2026-06-08 | `email` | First time buyer tips (Lone Star) | Email request from Dana to use outside b-roll shot was omitted from board notes during editor handoff. |
| `V292` | 2026-06-11 | `voice note` | Life insurance basics (Patel Ins) | Voice note from Raj requesting alternate outside shot was missed; board instead recorded incorrect note 'Calmer music'. |
| `V273` | 2026-06-13 | `voice note` | Meet the attorney (Torres Law Firm) | Voice note from Mike Torres requesting larger captions was never transcribed to production board notes. |
| `V107` | 2026-06-25 | `voice note` | Implants explained (Dr. Sarah Khan) | Voice note from Dr. Sarah Khan requesting larger captions was not added to the board, forcing repeated revisions. |
| `V140` | 2026-06-15 | `whatsapp` | Client story (Meridian Wealth) | WhatsApp request from Paul to remove price discussion was never entered on board notes; contributed directly to client churn. |
| `V176` | 2026-07-29 | `instagram` | Interior deep clean (Khan's Auto Spa) | Client sent edit request via Instagram DM; social inbox was not monitored by production team and never added to board. |
| `V199` | 2026-08-07 | `whatsapp` | Storm damage tips (Mike's Roofing) | WhatsApp request from Mike noting misspelled caption was not entered on board notes, causing delivery of incorrect video. |
| `V223` | 2026-08-15 | `whatsapp` | Custody myths (Torres Law Firm) | WhatsApp request from Mike Torres to cut slow opening 3 seconds was omitted from board notes during handoff to Sam. |
| `V220` | 2026-08-20 | `email` | Neighborhood guide (Lonestar RG) | Email request from Greg to use outside b-roll was never entered on board notes for new editor Sam. |
| `V217` | 2026-08-20 | `email` | Market update (Lonestar RG) | Email request from Greg to blur client face was missed and omitted from production board notes. |
| `V228` | 2026-08-21 | `whatsapp` | Insurance we take (Apex PT) | WhatsApp request from Kim Lee to add end phone number was omitted from board notes assigned to Sam. |
| `V233` | 2026-08-27 | `voice note` | Patient story (Greenway Pediatrics) | Voice note from Alan Cho requesting removal of pricing discussion was never transcribed to board notes. |
| `V235` | 2026-08-29 | `whatsapp` | Market update (Lone Star Realty) | WhatsApp request from Dana to trim first 3 seconds was missed and omitted from production board notes. |
| `V001` | 2026-08-29 | `voice note` | Implants explained (Dr. Sarah Khan) | Voice note from Dr. Sarah Khan requesting 'walk-ins welcome' outro was not transcribed to board notes. |
| `V291` | 2026-09-02 | `voice note` | Teen driver tips (Patel Insurance) | Voice note from Raj Patel requiring mandatory compliance branding 'Patel Insurance Group' was not logged on board notes. |
| `V182` | 2026-09-02 | `voice note` | Whitening before & after (Dr. Khan) | Voice note from Dr. Sarah Khan requesting 'walk-ins welcome' line was omitted from board notes for editor Sam. |
| `V265` | 2026-09-07 | `email` | Walk-ins welcome (TLC Home Care) | Email request from Angela Price to cut spoken stumble was omitted from board notes, driving revisions up to 3. |
| `V196` | 2026-08-05 | `whatsapp` | Trainer intro (Ironclad Gym) | WhatsApp request from Marcus Webb to swap to outside shot was never logged on board notes for Sam. |
| `V263` | 2026-09-06 | `whatsapp` | Free estimate promo (Mike's Roofing) | WhatsApp request from Mike noting name misspelling in caption was omitted from board notes for editor Sam. |
| `V271` | 2026-09-12 | `email` | Gutter guards (Prime Roofing Co) | Email request from Tony Russo to trim slow start was not communicated to freelance editor Dev; notes left blank. |
| `V289` | 2026-09-16 | `instagram` | Try-on day (Luna Bridal) | Instagram DM from Sofia noting background music was too loud was never checked or added to board notes. |
| `V296` | 2026-09-14 | `email` | Insurance we take (Summit Chiro) | Client edit instruction regarding price changes sent via email was not passed to freelance editor Dev. |
| `V274` | 2026-09-16 | `whatsapp` | What a consult costs (Torres Law) | WhatsApp request from Mike Torres to cut spoken stumble was omitted from board notes assigned to freelance editor Dev. |
| `V287` | 2026-09-23 | `whatsapp` | New arrivals (Luna Bridal) | Spanish WhatsApp message from Sofia about loud music was never translated or logged on board notes for Sam. |
| `V305` | 2026-09-26 | `email` | Tesla detail (Vega Auto Detailing) | Spanish email from Carlos Vega regarding audio level was not entered into board notes for editor Sam. |
| `V291` | 2026-09-22 | `email` | Teen driver tips (Patel Insurance) | Email from Raj Patel requesting outside b-roll shot for teen driver tips was never added to board notes for editor Dev. |

---

## 5. Sales Inbound: Never Replied Leads (22 Records)

Querying `leads.csv` where `first_reply` is empty or null yields exactly **22 abandoned leads**:
`["L020", "L023", "L034", "L035", "L044", "L048", "L062", "L065", "L067", "L071", "L075", "L076", "L078", "L080", "L082", "L083", "L084", "L087", "L088", "L090", "L097", "L098"]`

### High-Value Commercial Leads Abandoned:
- **`L097` (Nina Patel, Patel Insurance Group)**: Submitted on 2026-09-30 via Website form asking to discuss contract renewal. Abandoned without reply, compounding client churn risk.
- **`L088` (Omar Haddad, Haddad Auto Group)**: Inbound inquiry via **Referral** submitted on 2026-09-12. Referrals have a 71.4% close rate, yet Omar received zero response.
- **`L098` (Bella Diaz, Diaz Realty)**: Warm inbound real estate lead submitted on 2026-09-30 via Website form.
- **`L080` (Jade Haddad, Haddad Family Dentistry)**: Medical/dental lead from Google (2026-08-30).
- **`L082` (Samir Hill, Hill Med Spa)**: High-ticket medspa lead from LinkedIn (2026-09-01).
- **`L087` (Nate Reyes, Reyes Pediatrics)**: Healthcare practice lead from Instagram (2026-09-10).

---

## 6. Client Retention & Churn Risk: `most_likely_to_leave`

### 6.1 Identified Client: Patel Insurance Group (Raj & Nina Patel)
- **Account Value**: $2,500.00/month retainer ($30,000/year contract).

### 6.2 Supporting Evidence:
1. **Explicit Contract Reconsideration Messages**:
   - `2026-09-30 10:29` (Website Form, Lead L097): *"We would like to talk about our contract and whether we continue."* — **Received 0 reply**.
   - `2026-10-02 18:44` (Email from `nina@patelinsures.com`): *"Following up. We need to talk about the contract this week."* — **Received 0 reply**.
2. **Repeated Regulatory Compliance Frustrations**:
   - `2026-09-02` (Voice Note): *"Raj here. In the videos please say Patel Insurance Group, the full name, not just Patel Insurance. Compliance cares about this."*
   - `2026-09-08` (Email): *"The videos say 'Patel Insurance' again. I asked for the full name. Not happy."*
   - `2026-10-01` (WhatsApp): *"teen driver tips still has the same problem. I already told you about this."*
3. **Payment Withheld**: Retainer invoice `INV-1122` ($2,500.00 due 2026-09-15) remains completely unpaid and is now **21 days overdue**.
4. **Historical Precedent**: Follows the identical failure pattern of Paul Grant / Meridian Wealth Partners, who cancelled their $2,500/mo retainer in July for the exact same reason (*"Too many rounds of fixes, and my notes keep getting missed"*).

### 6.3 Immediate Owner Action This Week:
Owner must call Nina and Raj Patel personally first thing Monday morning (2026-10-06 at 9:00 AM). Formally apologize for the compliance name error, confirm immediate correction of all active video assets to display "Patel Insurance Group" with the requested b-roll swap on "teen driver tips", schedule a formal contract review meeting for Wednesday, and offer a $500 goodwill credit to secure the contract and unblock collection of overdue invoice `INV-1122` ($2,500.00).

---

## 7. Marketing Channel Profitability & Blind Spots

### 7.1 Channel Financial Audit

| Channel | Inbound Leads | Converted Clients | Conversion Rate | Invoiced Revenue | Collected Cash | Delivery Costs (Studio + Editor) | Realized Gross Profit | Gross Margin |
|---|---|---|---|---|---|---|---|---|
| **Website form** | 20 | 9 | **45.0%** | $19,940.00 | $18,740.00 | $7,315.30 | **$11,424.70** | **61.0%** |
| **Google** | 15 | 4 | **26.7%** | $24,250.00 | $17,600.00 | $7,856.70 | **$9,743.30** | **55.4%** |
| **Instagram** | 18 | 6 | **33.3%** | $30,600.00 | $21,300.00 | $12,690.40 | **$8,609.60** | **40.4%** |
| **Referral** | 7 | 5 | **71.4%** | $32,100.00 | $16,800.00 | $11,892.50 | **$4,907.50** | **29.2%** |
| **LinkedIn** | 12 | 1 | **8.3%** | $7,500.00 | $5,000.00 | $2,508.00 | **$2,492.00** | **49.8%** |
| **Meta ad** | 27 | 7 | **25.9%** | $32,000.00 | $14,900.00 | $12,633.00 | **$2,267.00** | **15.2%** |

### 7.2 Determination: `best_marketing_channel`
- **Primary Selection**: **`Website form`**
- **Rationale**: Website form delivers the highest absolute gross profit ($11,424.70) and highest gross margin (61.0%) across all channels, converting 45.0% of incoming leads with virtually zero collection lag ($18,740 collected of $19,940 invoiced). While Referral delivers a higher conversion rate (71.4%, 5/7 leads, $32,100 invoiced), Website form provides scalable organic acquisition without partner commission dependencies. In contrast, Meta ads acquired the highest lead volume (27 leads) but suffered low conversion (25.9%), severe collection delays, and razor-thin gross profit ($2,267.00, 15.2% margin before subtracting ad spend).

### 7.3 Data Blind Spots (`what_this_data_cannot_tell_us`)
1. **Advertising Expenditure & True CAC**: The dataset records studio time ($40/hr) and editor wages in `costs.csv`, but contains zero advertising spend data (Meta ad budgets, Google PPC spend, LinkedIn campaign costs). True customer acquisition cost (CAC) and net marketing ROI cannot be computed.
2. **Offline Communications & Verbal Agreements**: Several messages in `messages.txt` reference phone calls or in-person studio discussions; verbal agreements regarding shoot reschedules, verbal approvals, or payment arrangements are unrecorded.
3. **Long-Term Client LTV Beyond 6 Months**: All transaction records span exclusively from April 2026 to October 2026. Annual client retention, repeat booking rates beyond six months, and seasonal demand cannot be observed.
4. **Third-Party Agency Billing Terms**: Brightline Marketing LLC pays on behalf of multiple medical clients (Greenway Pediatrics, Summit Chiropractic), but the contractual markup, agency fee agreement, or service level commitments between Axeom and Brightline are undocumented.
5. **Fixed Studio Operating Overheads**: Beyond hourly studio rate allocations, fixed monthly overheads (facility lease, utilities, equipment depreciation, cloud software subscriptions, insurance) are omitted from the data.

---

## 8. Prioritized Owner Action Plan: `monday_top_3`

On Monday morning, October 6, 2026, the studio owner must execute three prioritized, high-leverage actions:

1. **Action 1 (Emergency Churn Intervention & $2,500 Cash Recovery)**:
   - Call Nina and Raj Patel (Patel Insurance Group) personally at 9:00 AM.
   - Formally apologize for compliance branding errors, confirm immediate correction of video assets to "Patel Insurance Group", review the contract to prevent cancellation of their $2,500/mo retainer, and collect 21-day overdue invoice `INV-1122` ($2,500.00).

2. **Action 2 (Capture $2,950 Unbilled Revenue & Reconcile Client Credits)**:
   - Immediately issue invoices for the 3 completed unbilled shoots: Vega Auto Detailing (`B144`, $1,500.00), Ironclad Gym (`B123`, $900.00), and DFW Founders (`B136`, $550.00) to collect **$2,950.00** in earned revenue.
   - Concurrently apply a $1,500.00 credit to Lone Star Realty for cancelled shoot `B148` and refund Glow Aesthetics $900.00 for duplicate payment on `INV-1086`.

3. **Action 3 (Enforce Collections on $6,750 in Aged Receivables & Fix Billing Tool)**:
   - Directly follow up on the remaining 8 overdue invoices totaling $6,750.00 (prioritizing Crown Barbers `INV-1066` $900 at 80 days late, Lonestar Realty Group `INV-1104` $1,500 at 41 days late, and TLC Home Care `INV-1120` $1,500 at 21 days late).
   - Correct the 6 billing tool software errors so paid invoices are no longer mislabeled as unpaid.

---

## 9. Independent Checks & Reproducibility Proof

- **Template Preservation**: The original `answers.json` file in the workspace remains untouched. All working findings are output to `answers_working.json` matching the exact JSON schema.
- **Mathematical Invariant Verification**:
  $$\text{overdue\_total} = \sum \text{overdue.amount\_owed} = \$9,250.00 \quad \checkmark$$
  $$\text{never\_billed\_total} = \sum \text{never\_billed.amount} = \$2,950.00 \quad \checkmark$$
  $$\text{client\_count} = |\text{clients}| = 29 \quad \checkmark$$
- **Reproducible Script**: Full analysis verified via `scratch/generate_answers_working.py` with 0 warnings or errors.
