# Axeom Challenge — Antigravity roadmap and ordered prompts

Use this as an execution playbook. The prompts are instructions for Antigravity; they do not claim that the application or business analysis is already complete.

## Before starting

1. Open a dedicated project folder in Antigravity. If work already exists, use that folder and preserve it.
2. Add the original challenge PDF, PACK.txt, answers.json, and complete data pack to a clearly named inputs/ directory. Keep originals unchanged. Extract any ZIP into a subdirectory while retaining the original archive. Do not paste credentials into prompts.
3. Tell the agent when you received the challenge, including timezone. If unknown, ask it to plan against a stated remaining-hours estimate, not a fabricated deadline.
4. Send Prompt 0 once, then Prompt 1. Send the remaining numbered prompts sequentially after reviewing the previous checkpoint. Do not paste the entire sequence as one request to implement everything at once.
5. Use the same agent conversation when practical. If the conversation resets, send the resume prompt at the end of this file.

## Roadmap

| Order | Work | Deliverable / checkpoint |
|---|---|---|
| 0–1 | Working rules and requirement audit | Exact requirements, template map and realistic schedule |
| 2 | Data inventory and identity investigation | Evidence map, conservative client links and ambiguities |
| 3 | Business analysis | Supported answers and evidence register |
| 4 | Visual design | Small phone wireframe, ingestion flow and acceptance plan |
| 5 | Project setup and import foundation | Runnable app shell and durable ingestion pipeline |
| 6 | Business services | Tested reconciliations, request tracking and priorities |
| 7 | Jev workflow | Real integration and measured evaluation |
| 8 | Dashboard | Working owner interface driven by real services |
| 9 | Acceptance tests | New-file, phone, persistence and approval results |
| 10 | Public deployment | No-login live URL verified on a phone |
| 11 | Submission | Validated answers, two-page writeup, logs, video and transcript |

Deployment feasibility and Jev free access must be checked early. Deploy the shell early if practical; Prompt 10 is the final deployment verification, not the first time hosting is considered.

### Suggested allocation of the 72 elapsed hours

- Day 1: 16 hours for requirements, data, findings and initial visual design; 8 hours for rest/meals.
- Day 2: 16 hours for ingestion, business services, early deployment and Jev; 8 hours for rest/meals.
- Day 3: 12 hours for dashboard, acceptance tests, documentation and recording; 4 hours of contingency; 8 hours for rest/meals.

This is a suggested 44 focused-work-hour budget inside 72 elapsed hours, not a demand to work continuously. Recalculate against time already used. Drop decorative or speculative features first. The challenge explicitly values judgment and honest incompleteness.

## What to review visually before application development

First inspect the real data. Then review three small visuals:

1. An evidence relationship diagram using actual discovered fields and source references. Do not invent a source schema.
2. An import flow showing valid, duplicate, changed and rejected records, followed by recalculation and review cases.
3. One phone home-screen wireframe: first action, reason, evidence, next step, next two actions and Add new files.

A fourth compact system diagram can explain browser, application, database and Jev. A local HTML design page and Mermaid source are sufficient; a separate design-tool account is optional. Time-box the first visual review to about 45–60 minutes. The visuals should expose design mistakes before implementation, not consume the build budget.

Wireframe text must use placeholders until actual findings exist. Distinguish a missing value from a measured zero. Never display fabricated business metrics for visual polish.

## Prompt 0 — Establish the working contract

```text
Act as my senior engineer, data analyst and technical mentor for the Axeom Challenge. Work inside the current project and implement the current phase with the available tools. Explain concepts simply. Preserve existing user work and inspect repository instructions before editing.

The actual challenge PDF, original PACK.txt, original answers.json and original data pack are authoritative. Inspect all of them before claiming their contents. Do not assume missing files, column names, data types, APIs or credentials. Do not ask Axeom questions. Record material questions, assumptions, evidence and risks in assumptions.md. Ask me only for missing files, access or a decision that genuinely blocks the current task; continue independent work when possible.

Nonnegotiable rules:
- Business reference date: 2026-10-06. The submission deadline is receipt time plus 72 hours; do not confuse these clocks.
- Preserve the pack ID exactly as text, including leading zeros. Preserve the supplied JSON keys and nested structure. Never turn illustrative placeholders into findings.
- Never invent clients, amounts, records, explanations, evaluation scores or successful test results. Separate evidence, assumptions, recommendations, unknowns and synthetic tests.
- Keep raw input unchanged. Every important result must trace to original file and record/message references.
- Use conservative identity links and explicit payment allocation. Uncertainty creates review items, not silent guesses.
- Initial and newly uploaded files use the same processing pipeline. New same-format files must update results without code edits.
- Build a public, phone-friendly app with no viewer login and a hard-to-guess URL. The first screen must make the first action clear within 10 seconds.
- Suggest actions; require an explicit owner decision. No automatic messages or external financial mutations. Draft-only controls must say draft, not sent.
- Free tools only. Verify current hosting, persistence and Jev access/allowance from official documentation and actual account availability. Do not assume finite trial credit is unlimited free operation.
- Use Jev meaningfully and measure actual performance. Keep secrets server-side and out of Git, logs, browser code and submitted files.
- Prefer small dependencies appropriate for Ubuntu, Python and a CPU-only laptop with limited RAM. Avoid unnecessary model training, GPU packages and infrastructure.
- Maintain daily_log.md, assumptions.md, docs/progress.md, docs/evidence.md and a compact docs/master-guide.html throughout the work. Record actual actions and failures, not fictional first-person experiences.
- Test meaningful business behavior. Do not claim unrun tests passed. Keep synthetic fixtures separate from the actual dataset.

Work only on the numbered phase I send. Make routine implementation decisions, explain them, complete that phase, and stop at its checkpoint. Do not ask permission for every reversible edit. End each phase with: completed work, files changed, commands run, tests and results, limitations, and the next manageable task for me.

For now acknowledge these rules briefly and wait for Prompt 1. Do not generate the entire app.
```

## Prompt 1 — Audit the challenge and plan the work

```text
Execute Phase 1 only: inspect the workspace and read the full challenge PDF, PACK.txt and original answers.json. Identify the original data files and existing code. Preserve everything.

Create:
1. docs/requirements.md with requirement ID, exact PDF page/section or template field, requirement, priority, planned implementation, acceptance test and status.
2. docs/answer-field-map.md explaining every supplied JSON field: meaning, original type/shape, required evidence and calculation/verification method. Keep unsupported values unfilled. Identify ambiguity in how the template represents unknown numeric values; do not silently treat its zero placeholders as proven zeroes or change types.
3. docs/progress.md with an elapsed-time plan, critical path, remaining work, blockers and phase checkpoints. Include rest, deployment, errors and recording. If receipt time is unavailable, state that the deadline is unknown.
4. assumptions.md and daily_log.md, recording only facts about this actual session.

Compare Python+Streamlit with Flask+simple HTML/CSS against this challenge and my environment. Recommend the smallest approach that satisfies uploads, phone UX, durable storage and Jev. Consider existing code before introducing a new stack. Identify a free deployment/storage path and verify its limits from official sources. Check whether Jev free access is obtainable early; disclose blockers without buying anything.

Explain why the live link, correct answers and unseen-file processing take priority. Extract all video/writeup/submission requirements and the scoring criteria without inventing scoring weights. Read the actual PDF rather than treating this prompt as the complete specification.

Show the roadmap and the concrete acceptance criteria. Do not build the app or analyze absent business files. Stop for my phase review.
```

## Prompt 2 — Investigate the data and client identities

```text
Execute Phase 2 only. Inspect each supplied business file fully, using scripts where appropriate. If a required file is absent, identify it and continue any useful inspection of present files; do not fabricate its contents.

Create a reproducible inventory of filenames, hashes, encoding, delimiters, actual headers, logical record counts, candidate types, missing values, duplicate records/IDs, invalid values and contradictions. Discover message boundaries rather than assuming one line is one message. Preserve raw text and source references. Treat IDs, phone numbers and pack IDs as strings where needed to preserve formatting.

Map actual source relationships. Build a proposed canonical client map with original aliases, contacts, source records, match evidence, confirmed/candidate/unresolved status and conflicts. Distinguish clients from leads-only records and third-party payers. Names, shared emails or shared phones alone must not force a merge. Explain what evidence justifies each confirmed match and what invalidates it.

Create docs/data_inventory.md, docs/identity_review.md and a source relationship diagram based on discovered fields. In docs/master-guide.html show one real client connected across its actual files, with provenance, or explain why no such example is yet verified.

Define how changed records, duplicate files, overlapping exports and snapshots differ. Do not assume absence from a new export means deletion.

Review the mapping for false merges and false splits. Update progress, assumptions and daily log. Do not proceed to dashboard code. Stop with the identity findings and unresolved questions for review.
```

## Prompt 3 — Establish the business answers with proof

```text
Execute Phase 3 only using the inspected pack and reviewed identity rules. Write reproducible analysis code and an evidence register before populating a working copy of answers.json. Preserve the original template unchanged.

Answer every Part 1 question and every supported template field:
- Real clients, count, aliases and non-client payers.
- Who owes us, amounts owed back, completed chargeable work never invoiced, and billing-tool discrepancies.
- Lost client requests, root causes and when the problem worsened.
- Client most likely to leave, evidence and a specific action this week.
- Most profitable marketing channel and what cannot be inferred.
- First three Monday actions and why they outrank alternatives.
- Unanswered leads and other fields present in the actual template.

For finances use decimal currency or integer minor units. Separate receipts from invoice allocations. Account for partial payments, credits, refunds, reversals, overpayments, unallocated cash, deposits, retainers and bundled work when present. Never offset different clients/currencies silently. Do not double count. Use 2026-10-06 as the as-of date and disclose treatment of later-dated records. Separate overdue from unpaid-but-not-due. Verify chargeability, price and invoice coverage before counting unbilled work.

For requests, compare actual message chronology, acknowledgments and production instructions. Distinguish proven contradictions from missing evidence. Support a deterioration date with comparable periods and data coverage. No recorded reply does not necessarily prove no reply ever occurred.

For profitability, define observation period, attribution, revenue/cash basis and supported costs. Do not equate collected cash with profit or missing costs with zero. Show cost-allocation assumptions and unknown acquisition costs where relevant.

Create docs/evidence.md with source references and derivations, a working answers file, and independent reconciliation checks. Validate internal totals and record identities. Clearly flag unsupported or ambiguous results. Update the master guide and logs. Stop for review before design.
```

## Prompt 4 — Design the minimum useful dashboard visually

```text
Execute Phase 4 only. Use the findings to design a small owner workflow before writing the dashboard implementation.

Create a self-contained docs/master-guide.html with rendered, readable diagrams and a phone wireframe; do not depend on an online diagram renderer for the HTML to be understandable. Keep editable Mermaid sources separately if useful.

Include:
1. Evidence relationships using actual discovered fields.
2. Upload flow: staged validation, duplicates/updates/errors, durable save, linking, recalculation and review cases.
3. Compact architecture: phone/browser, Python app, database, Jev and server-side secrets.
4. Phone home screen with one urgent action, why it matters, evidence and clear owner-controlled next step; show two secondary actions and Add new files without clutter.
5. Drill-down flows for client history, reconciled money, lost requests, unanswered leads and unresolved reviews.
6. Loading, empty, error, partial-analysis and model-unavailable states.

Use verified findings in the wireframe or visibly marked placeholders. Never invent metrics. Do not make charts or a chatbot the centerpiece without a business need. A draft button must not imply a message is sent.

Document owner action states and which state persists. Propose interfaces between ingest, store, identity, finance, requests, Jev, priorities and export; these are internal design proposals, not assumed source schemas. Explain how the UI and answers.json will use the same business results.

Give a 10-second phone-test script and acceptance checks. Time-box visual polish. Stop after presenting the design for my review; do not implement beyond a clearly labeled preview.
```

## Prompt 5 — Set up the app and reliable import foundation

```text
Execute Phase 5 only using the reviewed design. Inspect and reuse any existing project. Create a lightweight runnable application and import foundation incrementally.

Provide exact Ubuntu commands, explain each dependency, use a virtual environment, and pin the versions that actually run. Add README, .gitignore, placeholder-only secrets documentation, project modules and focused tests. Keep credentials and local generated data out of Git. Show the final folder responsibilities.

Implement the data store and schema migrations appropriate to the approved stack. Choose durable hosting-compatible persistence early; browser/session state and a disposable container filesystem cannot be the sole record of uploads or owner decisions. If choosing PostgreSQL, explain why that extra service is needed and how free limits are checked. Avoid building two database implementations unless justified.

Implement the original-file ingestion and Add new files backend using the same code path. Detect file role from verified format/schema as well as filename. Preserve original bytes/payload and provenance. Validate encoding, duplicate headers, required fields, amounts and dates. Support compatible extra fields. Set reasonable upload limits based on the pack. Return understandable file/row errors.

Make imports idempotent: file hash, stable record IDs, versioned changes and cautious duplicate handling when IDs are absent. Avoid collapsing legitimate identical-value transactions. Stage before committing; keep invalid files from corrupting accepted data. Use database constraints/transactions to handle repeated clicks and concurrent imports. Define batch partial-success behavior explicitly.

Provide an import summary: added, updated, skipped, rejected and needs-review. Persist dataset revision. Test new files, duplicate imports, changed records, malformed inputs and refresh/restart. Add only a minimal working app shell now, not decorative screens. Verify hosting feasibility with an early shell deployment where account access permits.

Report actual test output, how I run it locally and any access step I must perform. Stop for review.
```

## Prompt 6 — Implement the verified business services

```text
Execute Phase 6 only. Convert the reviewed analytical rules into reusable services used by both the app and answers export. Reuse Phase 3 code where sound rather than creating a second independent set of calculations.

Implement identity resolution, payment allocation/reconciliation, unbilled-work detection, request tracking, unanswered-lead detection, channel analysis and explainable priorities. Use actual input schemas and reviewed evidence rules. Avoid hardcoding findings for the initial clients; new records must follow the same rules automatically. Explicit reviewed alias/exception decisions may be stored with reasons and provenance.

Every finding should retain source references, known/unknown status and a dataset/rule version. Route genuine ambiguity to review. Owner decisions must persist and not disappear on recalculation; completed/dismissed recommendations should only reappear when justified by new evidence.

For this small dataset prefer a full deterministic recomputation after import when it is simpler. Measure before adding queues or incremental complexity. Publish a consistent result revision so the UI cannot combine stale and current totals.

Test actual manually verified cases plus separately marked synthetic cases: partial payment, second payment, repeat upload, refund/reversal, overpayment, third-party payer, same-name different-client, shared contacts, monthly-package coverage, unknown price, future-dated events and missing request evidence. Confirm payment-allocation invariants and independent totals.

Update the working answers through the shared export service. Report differences from Phase 3 and explain corrections. Update logs and evidence. Stop for review.
```

## Prompt 7 — Integrate Jev and measure it honestly

```text
Execute Phase 7 only. Read the current official documentation starting at https://docs.typesafe.ai. Verify SDK, authentication, supported primitives, limits and available free usage. Do not invent API endpoints or capabilities or install packages from unofficial lookalike sites.

Choose one useful scoped job supported by the docs and observed data. A likely candidate is classifying client messages as edit request, billing issue, booking, lead or other/review. Explain multi-intent handling. Jev must participate in the actual new-upload workflow, not only a separate demo. Do not rely on it to invent financial amounts, identity links or arbitrary extracted text if its documented output primitives do not support that.

Keep API keys server-side. Implement timeouts, bounded retries, cached results keyed by input/question/model version, and explicit pending/failure states. Do not hold a database transaction open while waiting for the API. A deterministic fallback, if used, must be labeled accurately and never counted as a successful Jev call.

Create a manually verified labeled dataset from actual supplied examples. Separate tuning examples from held-out evaluation. Choose a sample size supported by available data. Record actual model version, question definition, input IDs, labels, predictions, failures and usage. Compare to a simple baseline on the same held-out set. Report evaluated count, correct count, accuracy, coverage/failures, and precision/recall where relevant. Explain undefined metrics and representative errors. Do not fabricate labels, independent review or test results.

Run real integration checks if access is available. If access is blocked, preserve the implementation, mark live verification blocked and explain the exact remaining account step. Do not pay or claim the mandatory integration is complete. Update logs and guide. Stop for review.
```

## Prompt 8 — Build the final owner dashboard

```text
Execute Phase 8 only. Implement the reviewed phone-first design using the real services. Preserve existing working functionality.

Build in this order:
1. Today: one first action with reason, evidence and a meaningful owner-controlled next step, followed by two secondary actions.
2. Evidence drawer/page: original messages and financial/production records with provenance.
3. Client detail: canonical identity, aliases and connected history.
4. Money: reconciled overdue amounts, credits/refunds, unbilled work and uncertain allocations.
5. Requests/leads: missed requests, reply candidates and clear review status.
6. Add new files: validation, import progress, counts/errors and immediate refreshed findings.

Persist defer/approve/complete decisions. Keep internal UI choices separate from durable business state. In Streamlit account for reruns and invalidate derived caches by dataset revision. Uploading a file or running Jev must not send messages or mutate external financial systems. A manual-copy reminder draft is acceptable when clearly labeled; never show a fake sent confirmation.

Keep the home screen concise; put large tables and charts behind drill-downs. Show unknown as unknown, not zero. Make controls usable at narrow phone widths and avoid overflow. Cover loading, empty, failure and partial-analysis states. Preserve the fixed business date visibly where needed.

Run available interaction tests and inspect the actual rendered interface at phone and desktop sizes. Save useful screenshots as evidence. If no browser test tool is available, report that limitation and give me a short manual test. Do not call a mockup a working app. Stop with a runnable local dashboard for review.
```

## Prompt 9 — Challenge the implementation with unseen inputs

```text
Execute Phase 9 only. Review against the original requirements, then test behavior with original data and a separate synthetic fixture set that the implementation has not been tailored to. Do not mix synthetic test records into submission answers.

Test at least:
- An unseen same-format file updates the correct client and business results without code edits.
- A second payment changes balance once; reupload leaves it unchanged.
- A renamed file with valid recognized schema still works.
- Legitimate repeated transactions are not collapsed.
- Similar names with conflicting evidence remain separate.
- A new alias with strong evidence links correctly.
- A new request appears in the correct client/video workflow.
- Missing columns, invalid dates and bad amounts produce useful errors.
- Updates and overlapping snapshots follow documented semantics.
- Two imports cannot create duplicate financial events.
- Refresh and application restart preserve imports and owner choices.
- Jev failures remain visible and do not fabricate results.
- Owner approval/draft/defer controls behave as labeled.
- A phone user can identify the first action within 10 seconds.

Verify JSON structure, counts, totals and source references against the original template and independent evidence checks. Confirm no illustrative placeholder IDs survive. Check secrets are not exposed.

Create docs/test-report.md listing test, input, expected result, observed result, pass/fail/untested and evidence. Fix failures within scope and rerun affected tests. State remaining limitations honestly. Ask me to perform only real-device checks you cannot execute; automated viewport testing is not proof of a physical-phone check. Stop for review.
```

## Prompt 10 — Finalize the public deployment

```text
Execute Phase 10 only. Use the free hosting and durable storage path previously evaluated. Recheck actual account limits, project configuration and current official deployment instructions. Do not switch to a paid plan or claim a free allowance that is not available.

Prepare the production configuration and deploy within available permissions. Reuse an early deployment rather than creating unnecessary new projects. If account login or a secret is missing, tell me the exact minimal action and where to configure it securely; do not ask me to paste keys into chat.

Use a hard-to-guess available public URL and no viewer login as required for the fake challenge dataset. Keep repository visibility and app viewer access as separate decisions. Seed the original pack through the same idempotent pipeline used for uploads. Preserve data across deployment/restart. Document free-tier sleep, quota and availability limitations accurately.

Verify a fresh unauthenticated visit, phone-width behavior, new file uploads, refresh/restart, real Jev behavior and owner controls. Have me verify on a physical phone if you cannot. Do not leave synthetic acceptance data in the submission dataset. Record the actual live link inside the working answers.json.

Create deployment instructions and a monthly cost/allowance table covering hosting, persistence and Jev. State what was actually verified, and any block preventing the app from remaining live. Stop for review.
```

## Prompt 11 — Prepare and audit the final submission

```text
Execute Phase 11 only. Re-read the original submission requirements and produce a concrete submission package from the actual completed work.

Include:
1. answers.json using the provided template, exact pack ID, verified supported answers and real links.
2. The live link, also inside answers.json.
3. writeup.md or PDF, at most two rendered pages: proof for answers, system design, monthly costs, limitations, Jev job and actual measurements, next two weeks.
4. assumptions.md: important questions, assumptions, evidence and risks.
5. daily_log.md: actual daily work, changed thinking and failures.
6. A plan for a 5–10 minute working demonstration and a transcript of the actual recording once available.
7. One ZIP or shared folder with the required files and accessible links, excluding secrets and dependency folders.

For the demo show the first owner action, source evidence, money reconciliation, a genuinely new file and Jev. Prepare practice cues based only on the actual log for the three reflection questions: hardest part/how solved, initial mistake, and what the owner should stop doing. I must record the required camera-on, no-notes, uncut answers myself. Do not fabricate personal experience, a recording, video URL or transcript. If the recording is pending, mark the package pending and give the exact remaining recording task.

Check the original JSON keys/nested structure and every supported value. Do not encode unknown monetary values as proven zero; document unresolved template conventions transparently. Verify links unauthenticated, confirm the app remains live, confirm new uploads work, and reconcile the demo claims with implemented behavior. Render the writeup to verify page count.

Create docs/submission-audit.md mapped to each requirement and scoring criterion with evidence and honest gaps. Give the final package location and a concise ready/pending status. No invented score or claim that an unverified submission is complete.
```

## Resume prompt — Use if context is lost

```text
Resume this Axeom project without restarting it. Read repository instructions, docs/progress.md, docs/requirements.md, docs/evidence.md, assumptions.md, daily_log.md and relevant existing code/tests. Inspect the current Git changes and preserve my edits. Summarize completed phases, current phase, actual verification evidence, remaining blockers and remaining time if known. Use the original files as source authority. Continue only the current authorized phase, preserving phase checkpoints and shared business logic. Do not rebuild completed modules merely because this is a new conversation.
```

## Recovery prompt — Use when an implementation step fails

```text
Diagnose this failure in the current Axeom project. Reproduce it with the smallest relevant input, inspect the actual error and trace the cause before changing code. Preserve unrelated work. Make the smallest justified fix, then run the failing test and directly affected regression checks. Explain root cause, changed files, observed results and remaining limitations. Update the daily log and current phase status. Do not replace the whole application or silently weaken requirements to make the error disappear.
```

## Your manual work

You provide the original files, complete account login/secret configuration if needed, review ambiguous decisions and the first-screen design, check the app on a real phone, and record the authentic final video. The agent can implement, analyze, test, draft documentation and package the work where its tools permit. Account access and physical-device verification cannot be assumed from a prompt.
