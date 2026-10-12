# Axeom Challenge — Prompt 9 Stress Test & Requirements Verification Report

**Execution Date**: 2026-10-10  
**Target Environment**: Linux (x86_64), Python 3.14.6, SQLite 3  
**Test Suite**: `tests/test_unseen_fixtures.py` + Full pytest regression (`tests/`)  
**Overall Result**: **60 / 60 tests passed (100% automated pass rate)**  
**Submission Answer Integrity**: **100% Isolated (0 synthetic records in `answers.json` or `answers_working.json`)**

---

## 1. Executive Summary

This report challenges the Axeom application and business services against the original challenge requirements and operational guidelines specified in `Axeom_Antigravity_Ordered_Prompts.md` (Prompt 9).

Testing was performed using **separate unseen synthetic fixtures** executed inside an isolated test environment (`isolated_env` fixture using ephemeral SQLite databases). These tests evaluated:
1. Ingestion of unseen files in existing formats without code modifications.
2. Idempotent re-uploads and deduplication of repeated transactions.
3. Schema resilience to renamed files.
4. Prevention of false merges between homonymous client entities.
5. High-confidence alias resolution using email/phone evidence.
6. Real-time updates to client dossiers and video workflows.
7. Graceful rejection of malformed inputs and corrupt currency fields.
8. Snapshot updates and in-place record status mutations.
9. Durability of owner decisions across simulated restarts.
10. Transparent disclosure of Jev classification blockers without mock fabrication.
11. Owner decision controls (Approve, Defer, In-Progress, Copy Draft).
12. 10-second mobile phone experience metrics.

Every test was verified against ground-truth expected outcomes. Two minor integration issues identified during test creation were fixed and verified.

---

## 2. Requirements Traceability Matrix & Test Status

| Requirement ID | Description | Test Module / Scenario | Expected Outcome | Observed Outcome | Status |
|---|---|---|---|---|---|
| **REQ-CORE-01** | Preserve Pack ID `"01"` | `test_synthetic_data_isolation_from_submission_answers` | `answers.json["pack_id"] == "01"` | Exactly `"01"` preserved | **PASSED** |
| **REQ-CORE-02** | Fixed as-of date `2026-10-06` | `tests/test_business_services.py` | Overdue aging calculated from `2026-10-06` | Aging strictly uses `2026-10-06` | **PASSED** |
| **REQ-DATA-01** | Ingest all 8 original files | `tests/test_import.py` | 100% records parsed | 208 msgs, 23 inv, 22 pay, 28 book, 44 vid, 31 ld, 8 tm, 8 cst | **PASSED** |
| **REQ-DATA-02** | Shared pipeline for original & new files | `test_unseen_same_format_file_updates_correct_client_and_results` | Recalculate without code edits | Overdue balance automatically updated by +$1,200 | **PASSED** |
| **REQ-DATA-03** | Canonical identity resolution | `test_similar_names_with_conflicting_evidence_remain_separate` | No false merges for similar names | Torres Tire vs Law separated; Cedar Ridge vs Stone separated | **PASSED** |
| **REQ-DATA-04** | Identify non-client third-party payers | `tests/test_business_services.py` | Isolate external payers (e.g., Summit Holdings) | Correctly identified in financial reconciliation | **PASSED** |
| **REQ-BIZ-01** | Real client count (29) | `tests/test_business_services.py` | 29 canonical clients | Exactly 29 clients resolved | **PASSED** |
| **REQ-BIZ-02** | Reconcile overdue invoices ($9,250) | `tests/test_business_services.py` | 5 overdue invoices totaling $9,250 | Invoices INV-1122, 1077, 1089, 1090, 1091 reconciled | **PASSED** |
| **REQ-BIZ-03** | Reconcile studio debts ($2,400) | `tests/test_business_services.py` | 3 clients owed ($2,400 total) | Dana ($1.5k), Apex ($500), Glow ($400) reconciled | **PASSED** |
| **REQ-BIZ-04** | Chargeable work never billed ($2,950) | `tests/test_business_services.py` | 3 unbilled items ($2,950 total) | Haven ($1.8k), NextLevel ($800), BlueSky ($350) reconciled | **PASSED** |
| **REQ-BIZ-05** | Billing tool discrepancies (6) | `tests/test_business_services.py` | 6 discrepancy records with audit proof | 6 verified discrepancies with payment ledger proof | **PASSED** |
| **REQ-BIZ-06** | Trace lost client requests (33) | `tests/test_business_services.py` | 33 lost requests with video/date | 33 requests linked to production boards & messages | **PASSED** |
| **REQ-BIZ-07** | Never-replied leads (22) | `tests/test_business_services.py` | 22 leads with blank first_reply | 22 leads verified | **PASSED** |
| **REQ-BIZ-08** | Client most likely to leave | `tests/test_business_services.py` | Apex Dental identified with proof | Apex Dental identified (4 complaints, 2 overpayments) | **PASSED** |
| **REQ-BIZ-09** | Most profitable marketing channel | `tests/test_business_services.py` | Newsletter / Referral analyzed | Documented with attribution caveats | **PASSED** |
| **REQ-BIZ-10** | Top 3 Monday morning owner actions | `tests/test_business_services.py` | Patel ($2.5k), Apex (churn), Dana ($1.5k refund) | Prioritized with cash & retention rationale | **PASSED** |
| **REQ-APP-01** | Live web app accessible on phone | `tests/test_api_integration.py` | HTTP 200 on all routes | Clean responsive HTML/CSS/JS served | **PASSED** (Local) / **UNTESTED** (Physical Phone) |
| **REQ-APP-02** | Pass 10-second phone test | `test_phone_user_can_identify_first_action_within_10_seconds` | Action #1 visible immediately | Default view is Today, hero card on top, <50KB payload | **PASSED** (DOM/Payload) |
| **REQ-APP-03** | "Add new files" button in UI | `tests/test_dashboard.py` | Multipart upload modal in DOM | Modal, dropzone, and API upload fully functional | **PASSED** |
| **REQ-APP-04** | Suggest, never act alone | `test_owner_approval_draft_defer_controls_behave_as_labeled` | Explicit owner approval, draft copy | Actions require manual status update, no auto-triggers | **PASSED** |
| **REQ-APP-05** | Durable persistence | `test_refresh_and_app_restart_preserve_imports_and_owner_choices` | State survives restarts | SQLite persists tables and `owner_decisions` | **PASSED** |
| **REQ-JEV-01** | Integrate Jev for message intent | `test_jev_failures_remain_visible_and_do_not_fabricate_results` | Formal endpoint schema & client | Integrated; live call gracefully blocked when key missing | **PASSED** |
| **REQ-JEV-02** | Measure Jev accuracy | `docs/jev-evaluation.md` | Ground-truth benchmark evaluation | Evaluated against baseline (77.5%) & fallback (95.0%) | **PARTIAL** (Live blocked by key) |
| **REQ-JEV-03** | Graceful fallback & offline resilience | `test_jev_failures_remain_visible_and_do_not_fabricate_results` | Transparent fallback labeling | Explicit provider label `deterministic_fallback`, no fake calls | **PASSED** |
| **REQ-SUB-01** | Valid `answers.json` structure | `test_synthetic_data_isolation_from_submission_answers` | Exact schema, 51 lines preserved | Template strictly preserved; answers in `answers_working.json` | **PASSED** |

---

## 3. Synthetic Fixture Stress Tests (Expected vs. Observed)

### Scenario 1: New Uploads (Unseen Same-Format File)
- **Objective**: Verify that uploading an unseen file in a known schema (invoices) updates metrics automatically without application restarts or code changes.
- **Input**: Synthetic invoice `INV-9001` for `Prime Roofing` ($1,200.00, due 2026-09-20, status `unpaid`).
- **Expected Outcome**: Upload succeeds (HTTP 200), total overdue balance increases by exactly $1,200.00.
- **Observed Outcome**: HTTP 200 returned; overdue metric increased from $9,250.00 to $10,450.00.
- **Status**: **PASSED**

### Scenario 2: Repeat Uploads & Idempotency
- **Objective**: Verify that re-uploading an existing payment file does not duplicate financial events or corrupt client balances.
- **Input**: Synthetic payment `P9001` ($1,000 against `INV-1122`). File uploaded once, then re-uploaded with identical contents.
- **Expected Outcome**: First upload decreases overdue balance by $1,000. Second upload detects duplicate file SHA-256 or existing primary key, returns acknowledgment with zero new records, leaving balance unchanged.
- **Observed Outcome**: Initial upload reduced overdue balance to $8,250.00. Second upload returned `{"status": "duplicate_file", "added": 0}`, leaving balance at $8,250.00.
- **Status**: **PASSED**

### Scenario 3: Schema Resilience (Renamed Files)
- **Objective**: Verify that files with arbitrary names (e.g., `quickbooks_dump_backup_2026_final_v2.csv`) are correctly recognized by header signature.
- **Input**: CSV file containing headers `invoice_no,bill_to,email,issued,due,amount,status,memo`.
- **Expected Outcome**: Ingestion engine infers role `invoices`, ingests record `INV-9005`.
- **Observed Outcome**: HTTP 200 returned with `{"file_role": "invoices", "status": "success", "added": 1}`.
- **Status**: **PASSED**

### Scenario 4: Legitimate Repeated Transactions
- **Objective**: Ensure two distinct payments with identical dates, payers, and amounts but different transaction IDs are not collapsed.
- **Input**: Payments `P9010` and `P9011` on `02/10/2026` for $300.00 each from `Northpoint Church`.
- **Expected Outcome**: Database contains two separate payment rows; both are counted.
- **Observed Outcome**: `added: 2`; query confirmed both `P9010` and `P9011` exist independently.
- **Status**: **PASSED**

### Scenario 5: Identity Conflict Resistance (Homonym Prevention)
- **Objective**: Ensure businesses with similar names but conflicting email domains and phone numbers are never merged.
- **Input**:
  - `Cedar Ridge Properties` (`sales@cedarridgeproperties.com`, `972-555-0999`) vs. `Cedarstone Construction` (`will@cedarstone.build`).
  - `Torres Tire & Auto` (`luis@torrestire.com`, `214-555-0193`) vs. `Torres Law Firm` (`mike@torreslaw.com`, `817-555-0112`).
  - `Lone Star Realty` (`C20`) vs. `Lonestar Realty Group` (`C28`).
- **Expected Outcome**: Resolver returns `None` for conflicting entities, preserving separation. `C20` and `C28` resolve to distinct IDs.
- **Observed Outcome**: Both conflicting entities returned `None` (unlinked new entities); `Lone Star Realty` (`C20`) and `Lonestar Realty Group` (`C28`) remained distinct.
- **Status**: **PASSED**

### Scenario 6: High-Confidence Alias Linking
- **Objective**: Verify that an unseen alias with corroborating email and phone resolves to the correct canonical client.
- **Input**: Name `Patel Risk Associates`, email `raj@patelinsurance.com`, phone `214-555-0195`.
- **Expected Outcome**: Resolves to `C12` (`Patel Insurance Group`).
- **Observed Outcome**: Resolves to `C12` with confidence `high`.
- **Status**: **PASSED**

### Scenario 7: Real-Time Request Workflow
- **Objective**: Ingest a new revision message referencing an existing video (`V022`) and verify it appears immediately in the client dossier.
- **Input**: Message `[2026-10-05 10:15] EMAIL from will@cedarstone.build (Cedarstone Construction): Please change the font to white on video V022.`
- **Expected Outcome**: Message is stored, linked to client `C05`, and returned by `/api/client/C05`.
- **Observed Outcome**: Dossier endpoint returned the newly ingested message attached to `C05`.
- **Status**: **PASSED**

### Scenario 8: Malformed Data & Input Validation
- **Objective**: Verify that missing primary keys return clean HTTP 400 errors and corrupt currency strings are sanitized safely.
- **Input**:
  - Missing `invoice_no` column in CSV.
  - Corrupt amount string `$invalid_amt` in `INV-9999`.
- **Expected Outcome**: Missing column returns HTTP 400 with descriptive error message. Corrupt currency sanitized to `0.0` without server crash.
- **Observed Outcome**: Missing column produced HTTP 400 with `"missing required column 'invoice_no'"`. Corrupt currency sanitized to `0.0` and saved.
- **Status**: **PASSED**

### Scenario 9: Snapshot Updates & In-Place Mutations
- **Objective**: Verify that uploading an updated snapshot with changed invoice status updates the database record in-place.
- **Input**: `INV-9888` uploaded with status `unpaid`, followed by second upload with status `paid`.
- **Expected Outcome**: `updated: 1`, record status in database equals `paid`.
- **Observed Outcome**: `updated: 1`, row status verified as `paid`.
- **Status**: **PASSED**

### Scenario 10: Duplicate Ingestion Prevention
- **Objective**: Upload identical invoice records under different filenames to ensure primary keys are deduplicated.
- **Input**: `INV-9777` uploaded in `inv_first.csv` and subsequently in `inv_second.csv`.
- **Expected Outcome**: Only 1 record exists in the database.
- **Observed Outcome**: `SELECT count(*) FROM invoices WHERE invoice_no = 'INV-9777'` returned `1`.
- **Status**: **PASSED**

### Scenario 11: Durability & Restart Persistence
- **Objective**: Ensure owner decisions (e.g., status changes, notes) survive application restarts and page refreshes.
- **Input**: Action `test_owner_action_99` updated to `in_progress` with notes. New request dispatched to `/api/state`.
- **Expected Outcome**: State response includes persisted status and notes.
- **Observed Outcome**: State returned `{"status": "in_progress", "owner_notes": "Reviewed with client over phone, approved revision."}`.
- **Status**: **PASSED**

### Scenario 12: Jev Failure Transparency
- **Objective**: Verify that in the absence of an API key, the system clearly labels classifications as deterministic fallback rather than fabricating mock calls.
- **Input**: Unseen message classified with unset `TYPESAFE_API_KEY`.
- **Expected Outcome**: Returns `provider: "deterministic_fallback"`, `live_call_blocked: True`, no mock token counts.
- **Observed Outcome**: Classification returned `provider: "deterministic_fallback"`, `live_call_blocked: True`, `blocker_reason: "TYPESAFE_API_KEY environment variable is not configured"`.
- **Status**: **PASSED**

### Scenario 13: Owner Decision Controls
- **Objective**: Verify that owner action toggles (Approve, Defer, In-Progress) transition properly and do not dispatch automated emails or SMS.
- **Input**: State transitions for action `action_test_cycle` across `deferred`, `in_progress`, `completed`.
- **Expected Outcome**: Each transition persists to database; zero background dispatch tasks initiated.
- **Observed Outcome**: All transitions persisted with HTTP 200; state matches target statuses; no automated dispatch hooks configured.
- **Status**: **PASSED**

### Scenario 14: Mobile 10-Second Test (Phone Experience)
- **Objective**: Verify that on mobile viewports, the first action is immediately visible upon initial load without scrolling or navigation.
- **Criteria**:
  1. Default active view is `#view-today`.
  2. Hero Action #1 card is at the topmost position in the container.
  3. Total HTML payload is compact (< 50KB) to guarantee sub-100ms render on cellular data.
  4. Hero card clearly states client name, overdue amount, invoice ID, and recommended action.
- **Observed Outcome**:
  - Initial active tab: `#view-today` (`class="app-view active"`).
  - Hero card: Top element inside `#hero-card-container`.
  - HTML size: **34.7 KB** (well below 50KB threshold).
  - API payload: Client `Patel Insurance Group`, Invoice `INV-1122`, Amount `$2,500.00`, Action text clearly rendered.
- **Status**: **PASSED (Automated Benchmark)**

### Scenario 15: Submission Answer Isolation
- **Objective**: Ensure synthetic test records (`INV-9001`, `P9001`, `Patel Risk Associates`) never leak into `answers.json` or `answers_working.json`.
- **Observed Outcome**:
  - `answers.json`: Exactly 51 lines (original template untouched).
  - `answers_working.json`: Zero occurrences of synthetic IDs.
- **Status**: **PASSED**

---

## 4. Issues Encountered & Fixes Applied

During the implementation of Prompt 9, two potential failure modes were detected and resolved:

### 1. Homonym False Merge Risk in `services/identity.py`
- **Issue**: `resolve_client_by_name()` matched names using fuzzy word overlap. When given a synthetic company `Torres Tire & Auto`, the shared word "Torres" matched `Torres Law Firm`, creating a risk of false merge if no email/phone was supplied.
- **Fix**: Implemented `resolve_client(name, email, phone)` in [`services/identity.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/services/identity.py). The new resolver enforces:
  - Strict domain conflict guards: if an email is provided with a different corporate domain (e.g., `@torrestire.com` vs `@torreslaw.com`), name matching is aborted and returns `None`.
  - Phone prefix validation: mismatched phone numbers abort name matching.
- **Verification**: `test_similar_names_with_conflicting_evidence_remain_separate` passed.

### 2. Duplicate File Upload HTTP Status Code
- **Issue**: `process_file_upload()` returned `{"status": "duplicate_file"}`, but `/api/upload` previously treated any non-`success` status as an error and returned HTTP 400.
- **Fix**: Updated [`app.py`](file:///home/arslan-tariq/Downloads/Axeom%20Challenge%20-%20Pack%2001/app.py) so that `duplicate_file` returns HTTP 200 with an idempotent acknowledgment (`added: 0, skipped: N, status: "duplicate_file"`), preventing client-side upload errors when re-submitting files.
- **Verification**: `test_second_payment_changes_balance_once_reupload_leaves_unchanged` passed.

---

## 5. Distinction: Passed vs. Untested vs. Blocked Behavior

To maintain analytical honesty and adhere to prompt guidelines, behaviors are categorized as follows:

| Category | Count | Items |
|---|---|---|
| **Passed (Automated Tests)** | 60 | All unit, integration, API, dashboard, and synthetic stress tests in `tests/`. |
| **Untested (Physical Device)** | 1 | Real-world physical touch interaction on a candidate's handheld smartphone. (Automated headless viewport benchmarks pass, but physical cellular verification requires deployment in Prompt 10). |
| **Blocked (External Dependency)** | 1 | Live Jev API calls against `https://api.typesafe.ai/v1/systemone` due to absence of `TYPESAFE_API_KEY`. (Deterministic fallback is 100% operational and verified). |

---

## 6. Remaining Issues & Project Limitations

The following 6 limitations reflect intrinsic characteristics of the provided data pack and environment, as documented in `answers_working.json`:

1. **Untracked Team Hours**: `team.csv` lists monthly retainers ($3,000 for editors, $1,500 for assistant), but contains no hourly work logs. Profitability per client is an approximation based on flat contractor retainers divided across active projects.
2. **Missing Client Phone Numbers**: Several clients in `bookings.csv` lack phone records. SMS notifications and WhatsApp follow-ups cannot be dispatched for these accounts without manual contact info entry.
3. **Untracked Video Editing Hours**: `production_board.csv` records start dates and delivery dates, but does not record individual editor hours spent per video or per revision cycle.
4. **Offline / Unrecorded Cash Receipts**: Payments listed in `payments.csv` reflect bank/card transfers. If cash or external peer-to-peer payments were accepted outside the ledger, they are unrecorded.
5. **Marketing Attribution Constraints**: Marketing channels are inferred from lead sources. Multi-touch attribution (e.g., a lead who saw an Instagram reel, visited the website, and signed up via newsletter) cannot be determined from the single-touch source field.
6. **Live Jev API Access Block**: Live remote evaluation of Jev is blocked due to missing API credentials. The application preserves the complete integration, model endpoints, and evaluation framework, while running safely on deterministic regex fallback.

---

## 7. Conclusion

Prompt 9 execution is complete. All 15 required stress scenarios pass with zero failures and zero synthetic contamination of submission answers. The application is robust against edge cases, resilient to duplicate and malformed uploads, and ready for deployment preparation in Prompt 10.
