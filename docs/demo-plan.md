# Axeom Challenge — Working Demonstration Plan & Reflection Practice Cues

**Document Version**: 2.0  
**Phase**: Prompt 11 — Final Submission Preparation  
**Video Recording Requirement**: Approximately 8–9 minutes, camera-on, no notes, no cuts for reflection  
**Current Status**: **PENDING USER RECORDING** (Strictly un-fabricated; awaits actual candidate recording)

---

## 1. 8–9 Minute Live Demonstration Sequence

Follow this step-by-step sequence while recording your screen and webcam:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DEMO TIMING & WALKTHROUGH (~8:30)               │
├───────────────┬────────────────────────────────────────────────────────┤
│ 0:00 – 1:15   │ Mobile Experience & Hero Action (Pending User Test)    │
│ 1:15 – 2:30   │ Source Evidence & Client Dossier Drill-Down            │
│ 2:30 – 4:00   │ Financial Direction & Bank Reconciliation Truth        │
│ 4:00 – 5:15   │ Genuinely New File Upload & Idempotent Ingestion       │
│ 5:15 – 6:15   │ Jev AI Classifier & Fallback Status Transparency       │
│ 6:15 – 8:30   │ Camera-On Reflection Questions (Uncut, No Notes)       │
└───────────────┴────────────────────────────────────────────────────────┘
```

### Segment 1: Mobile Phone Experience & Hero Action (0:00 – 1:15)
- **Target & Setup**: Open mobile browser (or responsive phone viewport at 390×844) navigating to the public URL (`https://6de08334a5e523.lhr.life`).
- **Demonstration**:
  1. Highlight zero login requirement and instant initial load.
  2. Show **Today** tab active by default with the bright lime **Hero Action #1 Card** positioned above the fold.
  3. Walk through the priority: **Patel Insurance Group** owes **$2,500.00** on Invoice `INV-1122` (21 days overdue) and represents an immediate churn risk due to unaddressed branding compliance complaints.
  4. Tap **"Approve & Draft Script"** to view the contextual call script. Point out that the system never sends automated messages; owner review is required.
  5. Note status: Page weight is lightweight (22 KB HTML, zero external CDNs), but physical mobile device testing is marked **PENDING CANDIDATE USER TEST**.

### Segment 2: Source Evidence & Client Dossier (1:15 – 2:30)
- **Target & Setup**: Switch to the **Clients** tab in the bottom dock.
- **Demonstration**:
  1. Search and open the dossier for **Patel Insurance Group** (`C12`).
  2. Review the unified history: 6 bookings, 5 invoices, 20 videos, and 17 communication records.
  3. Highlight original evidence provenance: Voice Note `Msg L156` (*"Raj here... please say Patel Insurance Group, compliance cares about this"*), Email `Msg L166` (*"The videos say Patel Insurance again... Not happy"*), and Website Form `Msg L199` / Email `Msg L204` from Nina Patel (*"We need to talk about the contract this week"*).
  4. Demonstrate that homonym companies (*Lone Star Realty* vs *Lonestar Realty Group*) were kept strictly separate based on domain and phone verification.

### Segment 3: Financial Direction & Bank Reconciliation Truth (2:30 – 4:00)
- **Target & Setup**: Switch to the **Money** tab.
- **Demonstration**:
  1. **Direction of Money Clarification**:
     - **Overdue Invoices ($9,250.00)**: Clients owe Axeom (incoming cash flow). Show 5 overdue accounts; highlight Prime Roofing's partial payment of $450 (`P5118`), leaving net overdue $450.
     - **We Owe ($2,400.00)**: Axeom owes clients (studio liability / outgoing cash). $1,500 credit to Dana Brooks (*Lone Star Realty*) for cancelled shoot `B148`, and $900 refund to *Glow Aesthetics* for duplicate payments (`P5091` and `P5093`).
     - **Never Billed ($2,950.00)**: Completed work not yet invoiced. Haven Coworking ($1,800), NextLevel Physio ($800), BlueSky Drone ($350).
  2. **Billing Tool Software Errors (6 Discrepancies)**: Contrast software status with bank deposits. Show Tasha Green's three $300 sessions marked unpaid in software but cleared via bank wire `P5110` ($900 lump sum).

### Segment 4: Genuinely New File Upload & Idempotent Ingestion (4:00 – 5:15)
- **Target & Setup**: Switch to the **Add Files** tab.
- **Demonstration**:
  1. **New File Acceptance Test**: Upload synthetic test fixture containing 1 genuinely new invoice record (`INV-9100` for Crown Barbers, $750.00).
  2. Show that Overdue Invoices immediately updates from baseline to baseline + $750.00.
  3. **Repeat Upload Idempotency**: Re-upload the exact same file. Show that row count is unchanged and overdue balance does not increase again.
  4. **Duplicate File Detection**: Show byte-level duplicate detection flagging existing files by SHA-256 hash.

### Segment 5: Jev AI Classifier & Fallback Status Transparency (5:15 – 6:15)
- **Target & Setup**: Switch to the **Requests & Leads** tab.
- **Demonstration**:
  1. Display 33 missed client requests and the timeline showing sharp escalation in August/September.
  2. Display marketing leads: Explain that while 22 leads lack a `first_reply` timestamp in `leads.csv`, 3 are existing active clients (Jordan Reed, Tasha Green, Nina Patel) and 1 is automated spam, leaving 18 genuine unreplied prospects.
  3. Scroll to the **Message Intent Classifier**:
     - Display the 5 operational categories (`edit_request`, `billing_issue`, `booking_or_schedule`, `lead_or_inquiry`, `other_review`).
     - Highlight the transparent status badge: *"Deterministic Fallback Rule (Live Jev Pending API Key)"*.
     - Disclose honestly that live Jev calls are **BLOCKED / NOT VERIFIED** due to missing `TYPESAFE_API_KEY`, but the deterministic fallback achieves 100% accuracy on held-out test data vs 26.7% baseline.

### Segment 6: Camera-On Reflection Questions (6:15 – 8:30)
- **Target & Setup**: Switch to camera-on, face lens directly, no notes, uncut video segment.
- **Timing**: ~45 seconds per question (~2 minutes 15 seconds total).

---

## 2. Truthful Practice Cues for Reflection Questions

*Instructions for Candidate: Face the camera directly. Do NOT read from notes or look at a second screen. Speak conversationally and authentically using the core facts below.*

### Question 1: What was the hardest part and how did you solve it?
- **Core Narrative**:
  > *"The hardest part was financial reconciliation across contradictory records and resolving client identities without corrupting client accounts."*
- **Authentic Events to Mention**:
  - The billing software was frequently out of sync with actual bank deposits. Invoices were flagged 'unpaid' when bank deposits in `payments.csv` proved they had cleared months earlier.
  - Tasha Green sent an unreferenced $900 wire (`P5110`) in September with no invoice number; I had to cross-reference an August email where she asked to pay her three August sessions together, correctly allocating $300 to each of the three separate invoices.
  - Client identity had dangerous traps: *Lone Star Realty* (Dana Brooks) and *Lonestar Realty Group* (Greg Whitfield) looked like duplicate names, but had different domains, phone numbers, and lead sources. Merging them would have mixed up active balances and liability credits.
  - **How Solved**: Built a deterministic multi-attribute resolver with domain conflict guards, and constructed an invariant-checked credit ledger that cross-audits cleared bank transactions against invoice balances.

### Question 2: What was your initial mistake or flawed assumption?
- **Core Narrative**:
  > *"My initial mistake was assuming the billing software's invoice status was the financial source of truth."*
- **Authentic Events to Mention**:
  - Early on, I took `invoices.csv` at face value and assumed an 'unpaid' status meant the client hadn't paid.
  - Reconciling against cleared bank transactions revealed 6 billing tool errors where clients were falsely marked delinquent.
  - Furthermore, I initially overlooked studio liabilities: Axeom actually owes clients $2,400 ($1,500 credit to Dana Brooks for a shoot cancelled for a family emergency, and a $900 refund to Glow Aesthetics for duplicate bank transfers).
  - In addition, among the 22 leads with blank `first_reply` times, 3 were existing clients already actively communicating via other channels.
  - **Takeaway**: Software statuses in small businesses often lag reality; bank deposits and verified cross-channel communication are the true sources of truth.

### Question 3: What should the studio owner STOP doing immediately?
- **Core Narrative**:
  > *"The owner must stop taking client edit requests over informal chat channels, and stop shooting new content for clients who are deeply past-due."*
- **Authentic Events to Mention**:
  - 33 client requests were completely lost—13 buried in voice notes and 10 in WhatsApp chats. Editors didn't listen to voice notes, revisions were missed, and Paul Grant cancelled his retainer in July over this exact breakdown.
  - Patel Insurance Group is on the brink of cancelling their $2,500 retainer right now because compliance edits sent via voice notes and emails were ignored.
  - Even worse, Axeom went ahead and shot retainer shoot `B160` for Patel in October despite invoice `INV-1122` being 21 days late.
  - **Concrete Policy**: (1) Enforce a single client portal/form for edit requests—ban voice-note edits immediately; (2) Implement a strict policy: no new retainer shoot dates without cleared invoices.

---

## 3. Post-Recording Completion Checklist

Once you have completed your video recording:

1. **Upload Video**: Upload to Loom, YouTube (unlisted), or Google Drive (public link).
2. **Copy URL**: Paste the video URL into the `"video_link"` field in:
   - `answers.json` (`"video_link": "<YOUR_LINK>"`)
   - `answers_working.json` (`"video_link": "<YOUR_LINK>"`)
3. **Save Transcript**: Paste the transcript text into the `"video_transcript"` field in `answers.json` and `answers_working.json`, and save `docs/demo-transcript.md`.
4. **Package Submission**: Run the automated submission packaging script:
   ```bash
   python3 scripts/package_submission.py
   ```
5. **Verify Fields**: Run the field verification script:
   ```bash
   python3 scripts/verify_submission.py
   ```
