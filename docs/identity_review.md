# Axeom Challenge — Canonical Identity Review & Evidence Register

This document establishes the canonical identity map for all entities present in the Axeom dataset. It documents match evidence, separates clients from leads and third-party payers, details false-merge protections, and defines durable ingestion semantics.

---

## 1. Identity Resolution Methodology & Conservative Linking Principles

Per the working contract:
> *"Use conservative identity links and explicit payment allocation. Uncertainty creates review items, not silent guesses. Names, shared emails or shared phones alone must not force a merge."*

### Hierarchy of Identity Evidence
1. **Tier 1 (Authoritative Documentary Evidence)**:
   - Explicit written instructions from clients in `messages.txt` establishing rebrands, updated email domains, or new phone numbers (e.g. Jordan Reed's rebrand notification; Kelsey Moore's agency billing directive; Dr. Sarah Khan's office phone change).
2. **Tier 2 (Relational Key Consistency)**:
   - Relational cross-referencing between tables: `bookings.booking_id` appearing in `invoices.memo`, `invoices.invoice_no` appearing in `payments.reference`, and `bookings.booking_id` appearing in `production_board.shoot_booking`.
3. **Tier 3 (Contact & Domain Concurrence)**:
   - Co-occurrence of specific professional email domains (e.g. `@khandental.com`, `@torreslaw.com`) with unique personal contact names.
4. **Negative Rules (Invalidators that Halt Merging)**:
   - Shared surname alone (e.g., Khan) does NOT justify a merge.
   - Similar company names with differing contacts, phone numbers, or distinct email domains (e.g., Lone Star Realty vs. Lonestar Realty Group) MUST remain separate.
   - Generic webmail domains (e.g. `@gmail.com`) must never be used to merge records without matching phone and full name.

---

## 2. High-Level Entity Breakdown

- **Total Real Clients**: **29** (all verified by completed bookings, video production, or studio rental history).
- **Third-Party Payers (Non-Clients)**: **1** (`BRIGHTLINE MARKETING LLC` / Kelsey Moore, paying for Greenway Pediatrics and Summit Chiropractic).
- **Unconverted Leads**: **69** (leads recorded in `leads.csv` who never completed a booking, never received video production, and never paid).

---

## 3. Canonical Client Register (29 Verified Clients)

| Client ID | Canonical Name | Primary Contact | Observed Aliases across Files | Associated Email(s) | Associated Phone(s) | Activity Summary | Match Status & Provenance Evidence |
|---|---|---|---|---|---|---|---|
| **C01** | **Northpoint Church** | Pastor David Kim | Northpoint Church, NorthPoint Church, NORTHPOINT CHURCH, NorthPoint DFW, NorthPoint Media Team, NORTHPOINT MEDIA TEAM, David Kim, Pastor David Kim, PASTOR DAVID KIM | `media@northpointdfw.org` | `972-555-0112` | 27 bookings, 25 invoices, 24 payments, 0 videos (Studio rental), Lead L001 | **Confirmed**. Dedicated podcast studio client. Reconciled via email, lead L001, and recurring studio bookings B001–B172. |
| **C02** | **Hustle & Heart Podcast** | Tasha Green | H&H Podcast, Hustle & Heart, Hustle and Heart, Hustle & Heart Podcast, Tasha Green, TASHA GREEN | `tasha@hustleandheart.fm`, `tasha.green.mail@gmail.com` | `469-555-0157` | 26 bookings, 22 invoices, 15 payments, 0 videos (Studio rental), Lead L002 | **Confirmed**. Dedicated podcast client. Initial booking B002 used personal gmail; subsequent bookings used `@hustleandheart.fm`. Reconciled by Lead L002 and phone. |
| **C03** | **DFW Founders Podcast** | Ethan Cole | DFW Founders, DFW Founders Podcast, DFW FOUNDERS PODCAST, Ethan Cole, ETHAN COLE | `ethan@dfwfounders.fm` | `214-555-0118` | 15 bookings, 11 invoices, 11 payments, 0 videos (Studio rental), Lead L004 | **Confirmed**. Dedicated 4hr podcast studio client. Bookings B004..B171 tied to invoice memos and payments. |
| **C04** | **Khan Dental** | Dr. Sarah Khan | Dr. Sarah Khan, Sarah Khan, DR. SARAH KHAN, Khan Dental, KHAN DENTAL, Sarah Khan DDS, Dr Khan, Khan Dental PLLC | `sarah@khandental.com`, `sarah@khandental.con` (typo on B045) | `214-555-0141`, `214-555-0177` | 6 bookings, 6 invoices, 6 payments, 16 videos, Lead L040 | **Confirmed**. Content Day video client. Email typo on B045 (`.con`) confirmed by identical contact and address. Email on 2026-09-05 explicitly updated office phone to `214-555-0177`. |
| **C05** | **Cedar & Stone Builders** | Will Carter | Cedar and Stone, Cedar & Stone, Cedar & Stone Builders, Will Carter, WILL CARTER | `will@cedarstone.build` | `817-555-0122` | 2 bookings, 2 invoices, 2 payments, 7 videos, Lead L003 | **Confirmed**. Content Day client. Bookings B005 & B040, invoices INV-1006 & INV-1042. |
| **C06** | **Torres Law Firm** | Mike Torres | Torres Law Firm, Torres Law Firm PLLC, Torres Law, Torres, Mike Torres, MIKE TORRES | `mtorres@torreslaw.com` | `214-555-0188` | 6 bookings, 5 invoices, 4 payments, 14 videos, Lead L019 | **Confirmed**. Retainer shoot client. Tied through booking shoot IDs and invoice references. |
| **C07** | **Mike's Roofing** | Mike Delgado | Mikes Roofing, Mike's Roofing, Mike's Roofing LLC, Mike Delgado, MIKE DELGADO | `mike@mikesroofingtx.com` | `469-555-0172` | 7 bookings, 7 invoices, 5 payments, 16 videos, Lead L013 | **Confirmed**. Reels Pack client. WhatsApp and voice notes match phone `469-555-0172`. |
| **C08** | **Meridian Wealth Partners** | Paul Grant | Meridian WP, MERIDIAN WP, Meridian Wealth, MERIDIAN WEALTH, Meridian Wealth Partners, Paul Grant | `pgrant@meridianwp.com` | `214-555-0182` | 4 bookings, 3 invoices, 3 payments, 12 videos, Lead L011 | **Confirmed**. Retainer client. Phone matches voice note transcripts referencing video edits. |
| **C09** | **Luna Bridal Boutique** | Sofia Ramirez | Luna Bridal Boutique, Luna Bridal, LUNA BRIDAL, Sofia Ramirez | `sofia@lunabridal.com` | `214-555-0135` | 7 bookings, 6 invoices, 6 payments, 13 videos, Lead L018 | **Confirmed**. Reels Pack client. Invoices match bookings; WhatsApp matches contact. |
| **C10** | **Glow Aesthetics** | Nadia Hassan | Glow Aesthetics, Glow Aesthetic, Glow Med, GLOW MED, Nadia Hassan, NADIA HASSAN | `nadia@glowaesthetics.co` | `972-555-0153` | 5 bookings, 4 invoices, 5 payments, 9 videos, Lead L024 | **Confirmed**. Reels Pack client. Booking B011, invoices, payments, and Lead L024 aligned. |
| **C11** | **Bloom Medspa** | Priya Shah | Bloom Medspa, Bloom Med Spa, BLOOM MEDSPA, Bloom, Bloom Med Spa - Frisco, BLOOM MED SPA - FRISCO, Bloom Med Spa - Plano, BLOOM MED SPA - PLANO, Priya Shah | `priya@bloommedspa.com` | `972-555-0110` | 7 bookings, 7 invoices, 6 payments, 16 videos, Lead L068 | **Confirmed**. Content Day client with two locations (Frisco and Plano) operated by same owner Priya Shah using single email. |
| **C12** | **Patel Insurance Group** | Raj Patel | Patel Insurance Group, Patel Insurance, PATEL INSURANCE GROUP, Patel Ins, Raj Patel | `raj@patelinsures.com` | `214-555-0195` | 6 bookings, 5 invoices, 3 payments, 14 videos, Lead L032 | **Confirmed**. Retainer client. Verified through booking B014..B152 and matching production videos. |
| **C13** | **Apex Physical Therapy** | Dr. Kim Lee | Apex PT Dallas, APEX PT, Apex PT, Apex Physical Therapy, DR. KIM LEE, Kim Lee | `klee@apexptdallas.com` | `972-555-0144` | 6 bookings, 4 invoices, 4 payments, 17 videos, Lead L022 | **Confirmed**. Reels Pack client. Connected across all production boards (V033..V277). |
| **C14** | **Crown Barbershop** | Andre Jackson | Crown Barbershop, Crown Barbers, Andre Jackson | `andre@crownbarbers.com` | `469-555-0115` | 2 bookings, 2 invoices, 1 payment, 5 videos, Lead L008 | **Confirmed**. Reels Pack client. Bookings B016 and B068. |
| **C15** | **Oak Lane Dental** | Dr. Hannah Brooks | Oak Lane Dental, Oaklane Dental, OAK LANE DENTAL, Hannah Brooks DDS, HANNAH BROOKS DDS, DR. HANNAH BROOKS, Hannah Brooks | `hbrooks@oaklanedental.com` | `469-555-0108` | 4 bookings, 4 invoices, 3 payments, 13 videos, Lead L036 | **Confirmed**. Content Day client. Bookings B017..B145. Distinct from Dana Brooks. |
| **C16** | **The Brew Lab** | Lena Ortiz | The Brew Lab, Brew Lab, BREW LAB, Brewlab Coffee, Lena Ortiz | `lena@thebrewlab.coffee` | `214-555-0161` | 3 bookings, 3 invoices, 3 payments, 6 videos, Lead L029 | **Confirmed**. Reels Pack client. Bookings B018, B058, B118. |
| **C17** | **Ironclad Gym** | Marcus Webb | Ironclad Gym, Ironclad Fitness, Marcus Webb | `marcus@ironcladgym.com` | `469-555-0126` | 4 bookings, 3 invoices, 2 payments, 7 videos, Lead L057 | **Confirmed**. Reels Pack client. Bookings B019..B147. |
| **C18** | **Khan Family Law** | Aisha Khan | Khan Family Law, Khan Law, KHAN LAW, Aisha Khan, AISHA KHAN | `info@khanfamilylaw.com` | `214-555-0150` | 3 bookings, 3 invoices, 3 payments, 6 videos, Lead L045 | **Confirmed**. Reels Pack client. Completely separate legal business from Khan Dental and Khan's Auto Spa. |
| **C19** | **Elevate Athletics** | Jordan Reed | Elevate Fitness, Elevate Fit, ELEVATE FIT, Elevate Athletics, ELEVATE ATHLETICS, Elevate, ELEVATE, Jordan Reed, JORDAN REED | `jordan@elevatefit.co`, `jordan@elevateathletics.com` | `469-555-0133` | 8 bookings, 7 invoices, 6 payments, 16 videos, Leads L027 & L071 | **Confirmed Rebrand**. Email on 2026-08-01: *"Elevate Fitness is now Elevate Athletics! New email is jordan@elevateathletics.com."* Unified entity. |
| **C20** | **Lone Star Realty** | Dana Brooks | Lone Star Realty, Lone Star Realty LLC, Dana Brooks, DANA BROOKS | `dana@lonestarrealty.com` | `214-555-0164` | 5 bookings, 5 invoices, 5 payments, 13 videos, Lead L037 | **Confirmed**. Content Day client. Strictly distinguished from Lonestar Realty Group (Greg Whitfield). |
| **C21** | **Harbor Coffee Roasters** | Jen Walsh | Harbor Coffee, HARBOR COFFEE, Harbor Roasters, Harbor Coffee Roasters, Jen Walsh, JEN WALSH | `jen@harborcoffee.com` | `972-555-0165` | 3 bookings, 2 invoices, 2 payments, 5 videos, Lead L031 | **Confirmed**. Reels Pack client. Bookings B044, B086, B153. |
| **C22** | **Sage Family Therapy** | Dr. Maria Lopez | Sage Family Therapy, Sage Therapy, Dr. Maria Lopez, DR. MARIA LOPEZ, Maria Lopez | `mlopez@sagefamilytherapy.com` | `214-555-0174` | 1 booking, 1 invoice, 1 payment, 3 videos, Lead L025 | **Confirmed**. Reels Pack client. Booking B047, invoice INV-1045, payment P5058. |
| **C23** | **Vega Auto Detailing** | Carlos Vega | Vega Auto Detailing, Vega Auto, Vega Detailing, Carlos Vega, CARLOS VEGA | `carlos.vega.detail@gmail.com` | `469-555-0190` | 4 bookings, 2 invoices, 2 payments, 7 videos | **Confirmed**. Reels Pack client. Voice note messages from phone `469-555-0190` confirm client Carlos Vega. |
| **C24** | **Khan's Auto Spa** | Imran Khan | Khan's Auto Spa, Khans Auto, Imran Khan | `imran@khansautospa.com` | `972-555-0138` | 1 booking, 1 invoice, 1 payment, 3 videos, Lead L049 | **Confirmed**. Reels Pack client. Booking B074, invoice INV-1075, payment P5082. |
| **C25** | **Prime Roofing Co** | Tony Russo | Prime Roofing Co, Prime Roofing, Tony Russo, TONY RUSSO | `tony@primeroofingco.com` | `817-555-0131` | 3 bookings, 3 invoices, 2 payments, 4 videos, Lead L070 | **Confirmed**. Reels Pack client. Bookings B093, B131, B167. Unreferenced payments P5077 and P5119. |
| **C26** | **Greenway Pediatrics** | Dr. Alex Cho | Greenway Pediatrics, Greenway Peds, Brightline - Greenway | `acho@greenwaypeds.com` | `214-555-0145` | 4 bookings, 11 videos on production board | **Confirmed Client**. Service recipient for Reels Packs; billed through Brightline Marketing per written agreement. |
| **C27** | **Summit Chiropractic** | Dr. Alan Hale | Summit Chiropractic, Summit Chiro, Brightline - Summit | `drhale@summitchiro.com` | `972-555-0129` | 4 bookings, 9 videos on production board | **Confirmed Client**. Service recipient for Reels Packs; billed through Brightline Marketing per written agreement. |
| **C28** | **Lonestar Realty Group** | Greg Whitfield | Lonestar Realty Group, Lonestar RG, Greg Whitfield | `greg@lonestarrg.com` | `817-555-0119` | 1 booking, 1 invoice, 0 payments, 4 videos, Lead L069 | **Confirmed Distinct Client**. Booking B107, invoice INV-1104, videos V240..V243. Verified separate company from Dana Brooks. |
| **C29** | **TLC Home Care** | Angela Price | TLC Home Care, TLC Homecare, Angela Price | `angela@tlchomecare.com` | `214-555-0187` | 1 booking, 1 invoice, 0 payments, 4 videos, Lead L079 | **Confirmed**. Reels Pack client. Booking B127, invoice INV-1123, videos V266..V269. |

---

## 4. Third-Party Payer Register

### `BRIGHTLINE MARKETING LLC` (Kelsey Moore)
- **Role**: Agency Payer (Non-Client).
- **Contact**: Kelsey Moore (`kelsey@brightlinemktg.com`, `214-555-0170`, Lead `L038`).
- **Clients Paid For**:
  1. `Greenway Pediatrics` (`acho@greenwaypeds.com`)
  2. `Summit Chiropractic` (`drhale@summitchiro.com`)
- **Documentary Evidence**:
  - Message dated `2026-06-08 17:53`: *"Hi, Kelsey from Brightline Marketing. Please bill us (Brightline) for Greenway Pediatrics and Summit Chiropractic. We pay monthly."*
  - Invoices `INV-1046`, `INV-1061`, `INV-1080`, `INV-1100`, `INV-1110`, `INV-1130`, `INV-1141` are all billed to Brightline Marketing.
  - Payments `P5059`, `P5087`, `P5111`, `P5131` from `BRIGHTLINE MARKETING LLC` aggregate these client charges into monthly ACH transfers.

---

## 5. False Merge & False Split Guardrail Analysis

### Guardrail Case 1: Rebrand Merge (Elevate Fitness $\to$ Elevate Athletics)
- *Initial Risk*: Seeing two distinct email domains (`@elevatefit.co` vs `@elevateathletics.com`) could cause a false split into two clients.
- *Resolution*: Direct email evidence on `2026-08-01` (*"Elevate Fitness is now Elevate Athletics! New email is jordan@elevateathletics.com"*), shared phone `469-555-0133`, and continuous booking sequence (`B021`..`B162`) proves this is a single client that rebranded.

### Guardrail Case 2: Prevention of False Merge (Lone Star Realty vs. Lonestar Realty Group)
- *Initial Risk*: Very similar names could lead an automated naive string matcher to merge them.
- *Resolution*:
  - Client 1: **Dana Brooks**, Lone Star Realty, `dana@lonestarrealty.com`, `214-555-0164`, Lead `L037` (Referral).
  - Client 2: **Greg Whitfield**, Lonestar Realty Group, `greg@lonestarrg.com`, `817-555-0119`, Lead `L069` (Meta ad).
  - They have distinct owners, separate cities/area codes (214 Dallas vs 817 Fort Worth), separate email domains, separate leads, and separate bookings (`B039` vs `B107`). Merging them would be an incorrect false merge.

### Guardrail Case 3: Surnames & Separate Businesses (The Khan Family Entities)
- *Initial Risk*: Three businesses in the dataset contain the surname "Khan".
- *Resolution*:
  1. `Dr. Sarah Khan` operates **Khan Dental** (`sarah@khandental.com`, dental clinic).
  2. `Aisha Khan` operates **Khan Family Law** (`info@khanfamilylaw.com`, law firm).
  3. `Imran Khan` operates **Khan's Auto Spa** (`imran@khansautospa.com`, car detailing).
  - Three distinct industries, three separate owners, three separate domains. Maintained strictly separate.

### Guardrail Case 4: Contact Typo Recovery
- *Risk*: Booking `B045` contains email `sarah@khandental.con`.
- *Resolution*: Client name is `Khan Dental`, service is `Content Day`, price is `$1,500`. Matches Dr. Sarah Khan's practice exactly. Recovered into canonical entity `C04` without creating an artificial splinter client.

---

## 6. Durable Ingestion Semantics

When evaluators upload new files via "Add new files", the ingestion engine must apply strict semantic rules:

1. **Duplicate Files**:
   - An exact byte/hash duplicate file re-uploaded must be detected via SHA-256 and treated as a no-op (idempotent skip), returning a notice without creating duplicate records or mutating financial totals.
2. **Changed Records vs. New Records**:
   - Primary key lookup (`booking_id`, `invoice_no`, `payment_id`, `video_id`, `lead_id`).
   - If an existing record ID appears with updated fields (e.g. invoice status changes from `unpaid` to `paid`, or `client_approved_on` date is added), the system updates the existing record and increments dataset revision.
3. **Overlapping Exports & Incremental Appends**:
   - If an evaluator uploads an export containing rows from months 1–4 plus new month 5 rows, the system deduplicates rows 1–4 by primary key and appends only novel records.
4. **Snapshot Semantics & Non-Deletion Rule**:
   - **Crucial Rule**: Absence of a record from a new export file **does NOT signify deletion**. In business operations, exports are frequently filtered (e.g. "Last 30 Days"). Deletions must require an explicit administrative action, preventing accidental data loss when partial snapshot files are ingested.
