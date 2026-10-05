# KAVACH 6.0 — CHALLENGES → SOLUTIONS

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation & verified QA audit records  
> **Platform Tagline:** *"AI Hypothesizes. Evidence Confirms."*  

---

## Document Purpose

This document provides a comprehensive, transparent record of the major engineering challenges encountered during the development, hardening, and quality assurance of KAVACH 6.0, alongside their root causes, architectural solutions, and empirical verification.

Every challenge is documented using both a simple explanation for non-technical stakeholders and an exact technical explanation for core developers.

---

## Table of Challenges

1. [Completed Assessment Displayed as RUNNING](#challenge-1--completed-assessment-displayed-as-running)
2. [Real Assessment Contaminated by Demo Finding Data](#challenge-2--real-assessment-contaminated-by-demo-finding-data)
3. [World Monitor Latest-Assessment Selection Returned Wrong Assessment Type](#challenge-3--world-monitor-latest-assessment-selection-returned-wrong-assessment-type)
4. [ASSESS TARGET Did Not Use Dedicated World Monitor Empirical Route](#challenge-4--assess-target-did-not-use-dedicated-world-monitor-empirical-route)
5. [Evidence Existed on Finding but Did Not Persist/Retrieve Correctly](#challenge-5--evidence-existed-on-finding-but-did-not-persistretrieve-correctly)
6. [Risk API Failed Because Null Fields Violated Response Schema](#challenge-6--risk-api-failed-because-null-fields-violated-response-schema)
7. [Re-Verification Modal Disappeared After Execution](#challenge-7--re-verification-modal-disappeared-after-execution)
8. [Re-Test Result Did Not Persist Correctly After Reload/Restart](#challenge-8--re-test-result-did-not-persist-correctly-after-reloadrestart)
9. [Audit Trail Needed Complete Re-Test Lifecycle Events](#challenge-9--audit-trail-needed-complete-re-test-lifecycle-events)
10. [Report Evidence Aggregation Showed Incorrect Confirmed Evidence Counts](#challenge-10--report-evidence-aggregation-showed-incorrect-confirmed-evidence-counts)
11. [Report Narrative Used Generic Text Unrelated to Actual Finding](#challenge-11--report-narrative-used-generic-text-unrelated-to-actual-finding)
12. [Report Remediation Was Generic and Mismatched to Finding](#challenge-12--report-remediation-was-generic-and-mismatched-to-finding)
13. [Cross-Assessment Finding Contamination (A5B2/CB52 Style Issue)](#challenge-13--cross-assessment-finding-contamination-a5b2cb52-style-issue)
14. [Risk Evidence-Strength Semantics Were Conflated with Finding Status](#challenge-14--risk-evidence-strength-semantics-were-conflated-with-finding-status)
15. [Unverified Source-Code Finding Was Incorrectly Promoted Without Source Provenance](#challenge-15--unverified-source-code-finding-was-incorrectly-promoted-without-source-provenance)
16. [CWE-200 Was Missing from Knowledge Correlation](#challenge-16--cwe-200-was-missing-from-knowledge-correlation)
17. [OWASP Mapping Differed Across Modules](#challenge-17--owasp-mapping-differed-across-modules)
18. [RAG Retrieved Irrelevant Clickjacking/Security-Header Knowledge for CWE-200](#challenge-18--rag-retrieved-irrelevant-clickjackingsecurity-header-knowledge-for-cwe-200)
19. [AI Explanation Overclaimed Impact Beyond Empirical Evidence](#challenge-19--ai-explanation-overclaimed-impact-beyond-empirical-evidence)
20. [CVE/NVD Displayed an Unverified/Unrelated Score](#challenge-20--cvenvd-displayed-an-unverifiedunrelated-score)
21. [Priority Score Used Inconsistent /10 vs /100 Presentation](#challenge-21--priority-score-used-inconsistent-10-vs-100-presentation)
22. [Evidence Probe Used HEAD While Actual OpenAPI Validation Required GET](#challenge-22--evidence-probe-used-head-while-actual-openapi-validation-required-get)
23. [Technical Evidence Did Not Explicitly Record OpenAPI Version/Schema Detection](#challenge-23--technical-evidence-did-not-explicitly-record-openapi-versionschema-detection)
24. [Evidence Validation AI Panel Used Stale Generic AI Text Instead of Canonical RAG Output](#challenge-24--evidence-validation-ai-panel-used-stale-generic-ai-text-instead-of-canonical-rag-output)
25. [Assessment-Level Audit Event Incorrectly Used Assessment ID as finding_id](#challenge-25--assessment-level-audit-event-incorrectly-used-assessment-id-as-finding_id)
26. [Global Advisory Correlation Used Shared CWE as an Overly Strong Matching Signal](#challenge-26--global-advisory-correlation-used-shared-cwe-as-an-overly-strong-matching-signal)
27. [World Situational Monitor Displayed Incorrect Local Finding Count](#challenge-27--world-situational-monitor-displayed-incorrect-local-finding-count)
28. [Command Center Navigation Opened the Wrong Module](#challenge-28--command-center-navigation-opened-the-wrong-module)
29. [Command Center Confirmed-Finding Count Treated STILL_OPEN as Not-Confirmed](#challenge-29--command-center-confirmed-finding-count-treated-still_open-as-not-confirmed)
30. [Command Center Risk/Posture Labels Differed from Report](#challenge-30--command-center-riskposture-labels-differed-from-report)
31. [Stage Telemetry Leaked RETEST_* Events into Historical Stage Logs](#challenge-31--stage-telemetry-leaked-retest_-events-into-historical-stage-logs)
32. [Stage Lifecycle Contained an Incorrect COMPLETE → REPORT Transition](#challenge-32--stage-lifecycle-contained-an-incorrect-complete--report-transition)

---

## Challenge 1 — Completed Assessment Displayed as RUNNING

### Simple Explanation
Even though a security scan finished all its checks and reached 100%, the user interface still showed a spinner saying the scan was "RUNNING".

### Technical Problem
In the frontend workflow stepper and status badges, the component evaluated the assessment's completion solely based on the current stage index being greater than the total number of stages, ignoring the backend `status: "COMPLETED"` field.

### Symptoms
Assessment `KAVACH-WM-20260923-A018` had `status = "COMPLETED"` and `progress = 100%`, but the status badge displayed a spinning amber `RUNNING` badge and stage 8 showed as active instead of done.

### Root Cause
`WorkflowStepper.tsx` compared `currentIndex > idx` to decide if a stage was completed. When `currentIndex === 7` (`REPORT`), `isCompleted` evaluated to `false` for the final stage, leaving it visually in-progress.

### Solution
Added `assessmentCompleted` boolean check (`status === 'COMPLETED' || progress >= 100`). When true, every stage up to and including the current stage is marked completed (`currentIndex >= idx`).

### Technical Implementation
- Modified `frontend/src/components/common/WorkflowStepper.tsx`.
- Modified `frontend/src/pages/AssessmentProgressPage.tsx` lines 57-60.

### Verification
Inspected `AssessmentProgressPage.tsx` with active assessment `KAVACH-WM-20260923-A018`. All 8 stage badges show green checkmarks and status badge displays green `COMPLETED`.

### Before
`isCompleted = currentIndex > idx` → Stage 8 remained `RUNNING` at 100%.

### After
`isCompleted = assessmentCompleted ? currentIndex >= idx : currentIndex > idx` → All stages render `COMPLETED`.

### Lesson
UI state machines must give terminal backend states (`COMPLETED`, `FAILED`) precedence over intermediate positional stepper arithmetic.

### Evidence
Frontend test `frontend/tests/stage_telemetry_scoping.test.mjs` verifies terminal state handling.

---

## Challenge 2 — Real Assessment Contaminated by Demo Finding Data

### Simple Explanation
When a user ran a real live scan against an authorized website, findings from demo simulation targets appeared in the findings catalog alongside real observations.

### Technical Problem
Database queries in `findings.py` did not strictly enforce the `assessment_id` filter across all list and aggregation endpoints, allowing demo findings seeded with `is_demo=True` to leak into active views.

### Symptoms
The Findings Catalog for `KAVACH-WM-20260923-A018` listed generic SQL injection and XSS demo items that had no relation to `www.worldmonitor.app`.

### Root Cause
Omission of strict `filter(Finding.assessment_id == assessment_id)` in fallback branches of `findings.py` and `AppContext.tsx`.

### Solution
Enforced assessment-scoped filtering across all finding queries and ensured `seed_demo_discovery` only executes for explicitly marked demo assessments.

### Technical Implementation
- Updated `backend/app/api/routes/findings.py`.
- Updated `backend/app/services/finding_service.py`.
- Updated `backend/tests/test_data_isolation.py`.

### Verification
Ran `python -m pytest backend/tests/test_data_isolation.py`. Proved zero demo records returned for live assessments.

### Before
Real assessment query returned `[Real Finding, Demo SQLi, Demo XSS]`.

### After
Real assessment query returns exclusively `['WM-API-DOCS-A018']`.

### Lesson
Multi-tenant and multi-mode applications must treat `assessment_id` as an immutable foreign key boundary on every read path.

### Evidence
`backend/tests/test_data_isolation.py` PASSED in automated test suite.

---

## Challenge 3 — World Monitor Latest-Assessment Selection Returned Wrong Assessment Type

### Simple Explanation
When opening the World Monitor view, the system selected an old URL security check instead of the full comprehensive World Monitor hybrid assessment.

### Technical Problem
The endpoint `GET /assessments` returned records sorted by timestamp alone without filtering by `assessment_type` or target hostname, causing a lighter URL Check (`assessment_type="URL_CHECK"`) to override the hybrid assessment (`KAVACH-WM-20260923-A018`).

### Symptoms
World Monitor page displayed target baseline headers rather than the OpenAPI schema detection and deep runtime analysis.

### Root Cause
`AppContext.tsx` selected `assessments[0]` without checking if the assessment was a dedicated `WORLD_MONITOR` assessment or targeted `worldmonitor.app`.

### Solution
Updated assessment resolution logic to prioritize dedicated World Monitor assessments for the World Monitor target, sorting by started timestamp within that specific scope.

### Technical Implementation
- Modified `backend/app/api/routes/assessments.py`.
- Updated `frontend/src/context/AppContext.tsx`.
- Added regression test `backend/tests/test_world_monitor_active_selection.py`.

### Verification
Verified `GET /assessments` returns `KAVACH-WM-20260923-A018` as the active World Monitor assessment.

### Before
Generic URL Check assessment selected as active target.

### After
`KAVACH-WM-20260923-A018` consistently resolved as active assessment.

### Lesson
Context selectors must filter by domain capability/target before applying recency sorting.

### Evidence
`test_world_monitor_active_selection.py` passed in backend test matrix.

---

## Challenge 4 — ASSESS TARGET Did Not Use Dedicated World Monitor Empirical Route

### Simple Explanation
Clicking "Assess Target" for `worldmonitor.app` ran the generic port scanner instead of the specialized engine that knows how to test its specific microservices and OpenAPI endpoints safely.

### Technical Problem
`POST /assessments` routed all targets through `assessment_service.create_assessment`, which launched generic demo-seeded modules rather than `world_monitor_assessment_engine.run_assessment()`.

### Symptoms
Scans against `https://www.worldmonitor.app` failed to execute empirical OpenAPI probes and instead ran synthetic checks.

### Root Cause
Target URL inspection was missing from the `POST /assessments` route handler.

### Solution
Added `is_world_monitor_target(target_url)` check in `backend/app/api/routes/assessments.py`. When detected on non-demo requests, execution is delegated directly to `world_monitor_assessment_engine`.

### Technical Implementation
- Modified `backend/app/api/routes/assessments.py` lines 77-88.
- Utilized `urlparse` to identify `worldmonitor.app` and `www.worldmonitor.app`.

### Verification
Verified via `test_assess_target_and_url_check.py`.

### Before
World Monitor was scanned with generic baseline scanner.

### After
World Monitor triggers dedicated empirical assessment engine.

### Lesson
High-value or specialized targets require deterministic engine dispatch based on validated target host matching.

### Evidence
`backend/tests/test_assess_target_and_url_check.py` PASSED.

---

## Challenge 5 — Evidence Existed on Finding but Did Not Persist/Retrieve Correctly

### Simple Explanation
A vulnerability was confirmed with proof, but when refreshing the browser, the Evidence tab showed an empty list.

### Technical Problem
The `EvidenceRecord` table stored evidence rows, but the `GET /findings/{id}/evidence` endpoint queried by an un-indexed string column without foreign key cascade, and frontend `api.ts` used an inconsistent parameter name (`findingId` vs `finding_id`).

### Symptoms
Finding details panel showed "Evidence Confirmed: 1", but the evidence preview card displayed "No technical evidence records found".

### Root Cause
Parameter mismatch in `frontend/src/services/api.ts` and missing relational back-population in `backend/app/models/models.py`.

### Solution
Normalized API query parameter to `finding_id`, added foreign key relationship in SQLAlchemy `Finding.evidence_records`, and added defensive fallback queries.

### Technical Implementation
- Modified `backend/app/models/models.py`.
- Modified `backend/app/api/routes/evidence.py`.
- Modified `frontend/src/services/api.ts`.

### Verification
Reloaded `EvidenceValidationPage.tsx`. All baseline evidence records (`EV-WM-API-DOCS-A018`, `EV-WM-API-DOCS-A018-GET`) retrieved and rendered immediately.

### Before
Empty array returned on page reload.

### After
Evidence records retrieved reliably on initial load and navigation.

### Lesson
API parameter names must be strictly typed across frontend TypeScript interfaces and backend Pydantic schemas.

### Evidence
`backend/tests/test_evidence_deduplication.py` passed.

---

## Challenge 6 — Risk API Failed Because Null Fields Violated Response Schema

### Simple Explanation
Opening the Risk Scoring page crashed with an HTTP 500 error because an internal calculation did not provide an optional explanation string.

### Technical Problem
FastAPI returned `ResponseValidationError` because `RiskScoreResponse` schema required string fields (`threat_actor_profile`, `business_impact_narrative`) that were `None` in the database.

### Symptoms
HTTP 500 Internal Server Error on `GET /assessments/{id}/risk-breakdown`.

### Root Cause
Pydantic v2 model had non-optional type annotations (`str` instead of `Optional[str] = None`).

### Solution
Updated `schemas.py` to make all narrative and context fields `Optional[str] = ""` with safe defaults.

### Technical Implementation
- Modified `backend/app/schemas/schemas.py`.
- Added defensive dictionary `.get(key, "")` in `risk_service.py`.

### Verification
Querying `GET /assessments/KAVACH-WM-20260923-A018/risk-breakdown` returned HTTP 200 with complete JSON payload.

### Before
FastAPI threw 500 error on null fields.

### After
FastAPI returns valid response with populated scores and safe empty string fallbacks.

### Lesson
Schema contracts must always declare optional fields as nullable when data sources are dynamically computed.

### Evidence
`backend/tests/test_risk_prioritization_validation.py` PASSED.

---

## Challenge 7 — Re-Verification Modal Disappeared After Execution

### Simple Explanation
When a developer clicked "Run Live Re-Verification" inside the modal popup, the popup instantly closed before they could see whether the fix succeeded or failed.

### Technical Problem
The submit button handler triggered a full page state reload via `refreshData()`, which caused the parent React component to re-mount and reset `isModalOpen` to `false`.

### Symptoms
User clicked "Execute Re-Test", screen flashed, modal closed, and user had to manually navigate back to inspect if the finding changed.

### Root Cause
Unconditional `onClose()` called inside the execution `try` block before the re-test result was rendered to state.

### Solution
Decoupled re-test execution from modal visibility. The modal remains open in an active "Result" state displaying the state diff, raw probe output, and new SHA-256 hash until explicitly dismissed by the user.

### Technical Implementation
- Modified `frontend/src/components/common/ReVerificationModal.tsx`.
- Added `retestState: 'IDLE' | 'EXECUTING' | 'RESULT' | 'ERROR'`.

### Verification
Ran frontend test `frontend/tests/reverification_modal.test.mjs`.

### Before
Modal closed instantly on button click.

### After
Modal stays open, shows progress indicator, then displays before/after comparison diff.

### Lesson
Long-running or critical verification actions must display their results within the initiating context before closing.

### Evidence
`reverification_modal.test.mjs` PASSED (2/2 scenarios).

---

## Challenge 8 — Re-Test Result Did Not Persist Correctly After Reload/Restart

### Simple Explanation
After running a live re-test and proving a vulnerability was STILL_OPEN, refreshing the browser reverted the finding's status back to its initial state.

### Technical Problem
The re-verification engine generated an in-memory diff and updated React state, but failed to commit the updated status and new evidence record to the SQLite database within a database transaction.

### Symptoms
Finding showed `STILL_OPEN` immediately after re-test, but showed `CONFIRMED` upon pressing F5.

### Root Cause
Missing `db.commit()` in the re-verification service after creating the after-fix `EvidenceRecord`.

### Solution
Enforced atomic transaction in `world_monitor_assessment_engine.py`: writes the `EVD-AFT-*` evidence record, updates `Finding.status = "STILL_OPEN"`, logs the `RETEST_*` audit events, and executes `db.commit()`.

### Technical Implementation
- Modified `backend/app/services/world_monitor_assessment_engine.py` in `reverify_finding()`.

### Verification
Executed live re-test, restarted backend service, queried database directly: status remained `STILL_OPEN` with 5 persistent after-fix evidence records.

### Before
Status reverted to initial state on backend reload.

### After
Status and after-fix evidence records persist permanently across restarts.

### Lesson
State machine transitions must be backed by transactional database commits before returning HTTP 200.

### Evidence
`test_retest_workflow.py::test_retest_unpatched_target_returns_still_open` PASSED.

---

## Challenge 9 — Audit Trail Needed Complete Re-Test Lifecycle Events

### Simple Explanation
The security audit log showed that a scan took place, but had no record of when someone re-tested a finding or what evidence was captured during the re-test.

### Technical Problem
The re-test method executed live network requests but did not invoke `log_audit_event()`, leaving the audit log incomplete for regulatory and forensic compliance.

### Symptoms
Audit Trail jumped from `ASSESSMENT_COMPLETED` directly to report generation with zero records of re-testing activities.

### Root Cause
Re-verification service had no dependency on `log_audit_event`.

### Solution
Added 5 granular audit events to the re-test lifecycle:
1. `RETEST_STARTED`
2. `RETEST_OBSERVATION_CAPTURED`
3. `RETEST_EVIDENCE_CREATED`
4. `RETEST_STATE_COMPARISON`
5. `RETEST_UNRESOLVED` (or `RETEST_RESOLVED`)

### Technical Implementation
- Updated `backend/app/services/world_monitor_assessment_engine.py`.
- Logged SHA-256 hashes and timestamp in audit event description.

### Verification
Queried audit log for A018: identified all 25 re-test events in chronological sequence.

### Before
Zero re-test records in audit log.

### After
Complete chronological lifecycle captured for every re-test execution.

### Lesson
Forensic compliance requires that every state-changing verification action emits immutable audit events.

### Evidence
`test_retest_workflow.py::test_audit_trail_generation_sequence` PASSED.

---

## Challenge 10 — Report Evidence Aggregation Showed Incorrect Confirmed Evidence Counts

### Simple Explanation
An assessment had only 1 confirmed vulnerability, but the executive summary in the security report said "Confirmed Evidence: 2", confusing the reader into thinking there were 2 vulnerabilities.

### Technical Problem
The report generator counted the raw number of rows in `EvidenceRecord` for the assessment instead of counting unique confirmed findings or deduplicating historical artifacts.

### Symptoms
Report executive header displayed:
- Total Findings: 1
- Evidence Confirmed: 2
- Evidence Proofs: 2

### Root Cause
SQL query `SELECT COUNT(*) FROM evidence WHERE validation_result = 'CONFIRMED'` returned 2 because one finding had both `EV-WM-API-DOCS-A018` (original probe) and `EV-WM-API-DOCS-A018-GET` (canonical proof).

### Solution
Introduced evidence lifecycle distinction (`is_canonical` / `lifecycle_status`). The executive metric now aggregates unique active proofs: `confirmed_evidence = len(confirmed_findings)`. Historical and after-fix records are displayed in technical appendices without inflating executive counts.

### Technical Implementation
- Modified `backend/app/services/report_service.py` lines 42-65.
- Updated `frontend/src/pages/SecurityReportPage.tsx`.

### Verification
Generated report for A018:
- Total Findings: 1
- Evidence Confirmed: 1
- Evidence Proofs: 1
- Technical Evidence Captured: 2

### Before
Executive summary displayed 2 confirmed evidence proofs for 1 finding.

### After
Executive summary displays 1 unique confirmed proof; technical section details both artifacts.

### Lesson
Executive metrics must measure unique confirmed risk proofs, not raw database table rows.

### Evidence
`backend/tests/test_evidence_deduplication.py` PASSED (5/5 tests).

---

## Challenge 11 — Report Narrative Used Generic Text Unrelated to Actual Finding

### Simple Explanation
The executive narrative on the exported PDF/HTML report talked about generic cross-site scripting and SQL injection even though the only finding was an exposed API schema.

### Technical Problem
`_generate_executive_narrative()` used hardcoded static placeholder paragraphs when findings count was less than 3, rather than dynamically synthesizing the narrative from the actual finding categories in scope.

### Symptoms
Report for World Monitor contained boilerplate warnings about web application input validation.

### Root Cause
Static boilerplate text in `report_service.py` fallback branches.

### Solution
Replaced boilerplate with dynamic narrative generator that checks finding title, affected component, and category to construct an accurate target-specific narrative.

### Technical Implementation
- Updated `backend/app/services/report_service.py` `_build_dynamic_summary()`.
- Added specific clause for interactive API documentation endpoints (`/openapi.json`, Swagger UI).

### Verification
Inspected generated HTML report: narrative explicitly describes the unauthenticated exposure of OpenAPI documentation at `/openapi.json`.

### Before
Generic boilerplate about SQL injection and XSS.

### After
Accurate narrative describing OpenAPI schema exposure and reconnaissance implications.

### Lesson
Automated report narratives must strictly reflect the actual validated findings in scope.

### Evidence
`test_evidence_deduplication.py::test_html_report_deduplication_and_badges` PASSED.

---

## Challenge 12 — Report Remediation Was Generic and Mismatched to Finding

### Simple Explanation
The remediation section of the report advised developers to "sanitize user input" for an API documentation exposure, which does not solve the problem.

### Technical Problem
The remediation resolver defaulted to generic OWASP Top 10 recommendations whenever a finding lacked a custom remediation playbook.

### Symptoms
Remediation advice recommended parameter binding and escaping instead of disabling Swagger UI in production.

### Root Cause
Missing specific remediation rules for `CWE-200` in `report_service.py`.

### Solution
Added tailored, actionable remediation guidance for `CWE-200 / API Exposure`:
1. Restrict interactive documentation endpoints (`/docs`, `/redoc`, `/openapi.json`) to internal networks or authenticated administrators.
2. Disable automatic schema generation in production frameworks (e.g. FastAPI `docs_url=None, redoc_url=None, openapi_url=None`).
3. Deploy reverse proxy / WAF rules blocking public access to schema paths.

### Technical Implementation
- Modified `backend/app/services/report_service.py`.
- Updated `backend/app/data/seed_data.py`.

### Verification
Inspected remediation section of A018 report: contains framework-specific configuration snippets for securing OpenAPI documentation.

### Before
Generic input sanitation recommendations.

### After
Targeted, actionable instructions on disabling/authenticating API documentation.

### Lesson
Remediation guidance must be strictly correlated to the specific weakness (CWE) and component affected.

### Evidence
Report export verification in `backend/tests/test_audit_matrix.py`.

---

## Challenge 13 — Cross-Assessment Finding Contamination (A5B2/CB52 Style Issue)

### Simple Explanation
Findings from an earlier assessment run (e.g. CB52) unexpectedly showed up when viewing the results of a completely new assessment (A018).

### Technical Problem
The frontend store stored findings in a global array and appended newly fetched findings without clearing previously cached findings when switching assessments.

### Symptoms
Switching from assessment `CB52` to `A018` showed findings from both assessments combined.

### Root Cause
`AppContext.tsx` did not reset the `findings` state array upon `activeAssessment` change.

### Solution
Added an immediate state flush `setFindings([])` inside `setActiveAssessment()` and ensured all API queries include `?assessment_id={id}`.

### Technical Implementation
- Modified `frontend/src/context/AppContext.tsx`.
- Added assertion in `backend/tests/test_data_isolation.py`.

### Verification
Switched between multiple assessments in the UI: findings count accurately reflects only the selected assessment.

### Before
Findings from previous assessments accumulated in memory.

### After
Findings strictly scoped to currently selected active assessment.

### Lesson
Client-side state stores must flush target-scoped collections when changing active target contexts.

### Evidence
`backend/tests/test_data_isolation.py` PASSED.

---

## Challenge 14 — Risk Evidence-Strength Semantics Were Conflated with Finding Status

### Simple Explanation
The risk calculation dropped its confidence score to "UNVERIFIED" because a finding was still open after a re-test, even though the evidence proving the finding was 100% verified.

### Technical Problem
The scoring algorithm used `finding.status` to determine the evidence confidence multiplier. When `status` transitioned from `CONFIRMED` to `STILL_OPEN`, the multiplier fell back to a lower default weight.

### Symptoms
Priority score dropped from `5.92` to `3.20` after a re-test failed to resolve the issue.

### Root Cause
Conflation of finding remediation lifecycle state (`STILL_OPEN`) with technical evidence verification state (`VERIFIED`).

### Solution
Decoupled evidence strength from remediation status. Evidence strength is derived from `EvidenceRecord.validation_result` (`CONFIRMED` → weight 1.0). Remediation status (`STILL_OPEN`) does not degrade mathematical evidence confidence.

### Technical Implementation
- Modified `backend/app/services/risk_service.py`.
- Ensured `STILL_OPEN` findings retain `evidence_strength = "VERIFIED"` and weight `1.0`.

### Verification
Ran `test_risk_prioritization_validation.py`. A018 maintains stable score of `5.92 / 10.0` before and after re-testing.

### Before
Re-test execution degraded risk score.

### After
Risk score remains mathematically stable regardless of re-test lifecycle transitions.

### Lesson
Evidence verification strength (proof of existence) and remediation status (proof of fix) are orthogonal dimensions.

### Evidence
`backend/tests/test_risk_prioritization_validation.py` PASSED.

---

## Challenge 15 — Unverified Source-Code Finding Was Incorrectly Promoted Without Source Provenance

### Simple Explanation
A scanner claimed to have found a source-code vulnerability in a file, even though the user had only provided a website URL and no source code repository was attached.

### Technical Problem
The scanner executed a static pattern match against client-side bundled JavaScript and promoted it as a backend source-code vulnerability without verifying whether a local source repository was configured.

### Symptoms
Finding catalog listed "Hardcoded Secrets in Source Code" on a purely black-box URL assessment.

### Root Cause
Missing source provenance validation before promoting static AST/regex observations to confirmed findings.

### Solution
Implemented a strict source provenance gate in `world_monitor_assessment_engine.py`: if `source_repo_path` is not configured or does not exist, source-level checks are marked `SOURCE_NOT_CONFIGURED` and cannot generate confirmed findings.

### Technical Implementation
- Modified `backend/app/services/world_monitor_assessment_engine.py` lines 200-215.
- Added `evidence_status = "REQUIRES_SOURCE_VALIDATION"`.

### Verification
Ran A018 black-box assessment: source analysis gracefully reported "Source Not Configured", generating 0 ungrounded source findings.

### Before
Black-box scan generated unverified source-code findings.

### After
Only findings backed by direct empirical network evidence (`/openapi.json`) are promoted to confirmed findings.

### Lesson
Never assert source-level vulnerabilities without verified access to the source code repository.

### Evidence
`backend/tests/test_world_monitor_real_target.py` PASSED.

---

## Challenge 16 — CWE-200 Was Missing from Knowledge Correlation

### Simple Explanation
The system identified an information disclosure issue, but could not map it to an official Common Weakness Enumeration ID in the taxonomy database.

### Technical Problem
The local taxonomy database seeded in `seed_data.py` contained CWE-89 (SQLi) and CWE-79 (XSS), but lacked `CWE-200` (*Exposure of Sensitive Information to an Unauthorized Actor*).

### Symptoms
Taxonomy mapping card showed `CWE: UNMAPPED` and failed to link to OWASP documentation.

### Root Cause
Incomplete taxonomy seed data in `backend/app/data/seed_data.py`.

### Solution
Added comprehensive `CWE-200` taxonomy record to `seed_data.py`, including description, related OWASP mappings, and remediation guidance.

### Technical Implementation
- Modified `backend/app/data/seed_data.py` lines 61-75.
- Linked `CWE-200` to `OWASP-A05:2021 - Security Misconfiguration`.

### Verification
Queried taxonomy API for `CWE-200`: returned complete metadata and OWASP cross-reference.

### Before
`CWE: UNMAPPED` displayed on finding.

### After
`CWE-200` accurately mapped and linked to OWASP A05:2021.

### Lesson
Taxonomy engines must comprehensively cover information disclosure and configuration weaknesses, not just injection flaws.

### Evidence
`backend/tests/test_correlation_consistency.py` PASSED.

---

## Challenge 17 — OWASP Mapping Differed Across Modules

### Simple Explanation
One screen said the vulnerability belonged to "OWASP A01: Broken Access Control", while another screen said it belonged to "OWASP A05: Security Misconfiguration".

### Technical Problem
Different pages used independent hardcoded strings for OWASP category lookups instead of querying the central knowledge engine.

### Symptoms
Command Center showed A01; Evidence page showed A05; Report showed A01.

### Root Cause
Duplicated and desynchronized static mappings in frontend components.

### Solution
Established `CWE-200` → `OWASP A05:2021 - Security Misconfiguration` as the canonical mapping across all backend services and frontend components.

### Technical Implementation
- Updated `backend/app/services/correlation_service.py`.
- Synchronized `frontend/src/pages/FindingsCatalogPage.tsx`, `CommandCenterPage.tsx`, `SecurityReportPage.tsx`.

### Verification
Ran frontend regression test `frontend/tests/stage_telemetry_scoping.test.mjs`. Verified A05:2021 appears consistently across all views.

### Before
Inconsistent OWASP categories displayed across different views.

### After
Uniform `A05:2021 - Security Misconfiguration` displayed everywhere.

### Lesson
All taxonomy mappings must flow from a single source of truth in the knowledge engine.

### Evidence
`backend/tests/test_correlation_consistency.py` PASSED.

---

## Challenge 18 — RAG Retrieved Irrelevant Clickjacking/Security-Header Knowledge for CWE-200

### Simple Explanation
When generating AI explanations for the exposed API documentation, the AI started talking about missing clickjacking headers (`X-Frame-Options`) instead of API security.

### Technical Problem
The RAG retrieval query used generic target tags ("web application", "http") instead of the specific finding title and CWE identifier, causing the lexical search to return high-frequency security header documents.

### Symptoms
AI Analysis card contained advice on configuring CSP and X-Frame-Options for an OpenAPI schema finding.

### Root Cause
Unweighted query string construction in `backend/app/services/rag_service.py`.

### Solution
Refined RAG query construction to prioritize specific finding attributes: `f"{finding.title} {finding.cwe_id} API schema exposure documentation endpoint"`.

### Technical Implementation
- Modified `backend/app/services/rag_service.py` in `retrieve_context()`.
- Added query weighting for API security knowledge base articles.

### Verification
Verified retrieved RAG context for `WM-API-DOCS-A018`: top documents returned are OpenAPI security and API endpoint protection guides.

### Before
Retrieved documents focused on clickjacking and HSTS headers.

### After
Retrieved documents focus strictly on API documentation security and information disclosure.

### Lesson
RAG retrieval queries must be narrowly anchored by specific vulnerability identifiers (CWE/title) rather than generic platform metadata.

### Evidence
`backend/tests/test_rag_finding_grounding.py` PASSED.

---

## Challenge 19 — AI Explanation Overclaimed Impact Beyond Empirical Evidence

### Simple Explanation
The AI generated a report claiming that attackers could use the exposed API schema to "modify database records and take over the server", which was completely untrue and unsupported by evidence.

### Technical Problem
The LLM prompt lacked negative bounding constraints, allowing the model to extrapolate theoretical worst-case scenarios rather than reporting only what was empirically proven.

### Symptoms
AI report claimed "Critical Remote Code Execution and Data Compromise Possible" on a Medium-severity documentation exposure.

### Root Cause
Unconstrained prompt template in `ai_analysis_service.py`.

### Solution
Implemented four strict AI prompt grounding boundaries:
1. State only observed facts proven by HTTP responses.
2. Clearly distinguish supported interpretation from theoretical risk.
3. Explicitly state what is **NOT proven** (no backend compromise, no data extraction, no privilege escalation).
4. Restrict remediation to the specific affected endpoint.

### Technical Implementation
- Modified `backend/app/services/ai_analysis_service.py`.
- Added validation check to reject ungrounded impact claims.

### Verification
Inspected AI analysis output for A018: explicitly notes that finding represents reconnaissance value and endpoint discovery, with zero claims of system compromise.

### Before
AI hallucinated remote code execution and database takeover.

### After
AI output bounded strictly by empirical evidence: describes reconnaissance risk without exaggerating impact.

### Lesson
AI in security platforms must be strictly constrained by negative bounding prompts to prevent speculative fearmongering.

### Evidence
`backend/tests/test_priority7_ollama_analyst.py` PASSED.

---

## Challenge 20 — CVE/NVD Displayed an Unverified/Unrelated Score

### Simple Explanation
The finding card showed a Common Vulnerabilities and Exposures (CVE) identifier with a 9.8 Critical score, even though no CVE exists for having public documentation.

### Technical Problem
When a finding lacked a specific CVE, the UI fell back to displaying the highest CVE found in the global external advisory database, creating false attribution.

### Symptoms
Finding `WM-API-DOCS-A018` displayed `CVE-2023-XXXX CVSS 9.8` in its header card.

### Root Cause
Frontend fallback expression `finding.cve_id || advisories[0]?.cve_id`.

### Solution
Removed fallback. If a finding does not map to an authoritative CVE in the NVD database, it explicitly displays `CVE: Not Identified` and `NVD CVSS: Not Available`.

### Technical Implementation
- Modified `frontend/src/pages/FindingsCatalogPage.tsx`.
- Modified `frontend/src/components/common/FindingDetailModal.tsx`.
- Updated `backend/app/services/world_monitor_assessment_engine.py`.

### Verification
Verified finding card for A018: cleanly displays `CVE: Not Identified`, `NVD CVSS: N/A`, and relies exclusively on its deterministic priority score of `5.92 / 10.0`.

### Before
Unrelated global CVE displayed on local finding.

### After
Honest representation: `CVE: Not Identified`, preventing false attribution.

### Lesson
Never display an external vulnerability identifier unless verified by exact component version matching.

### Evidence
`backend/tests/test_cve_nvd_provenance_and_scale.py` PASSED.

---

## Challenge 21 — Priority Score Used Inconsistent /10 vs /100 Presentation

### Simple Explanation
One card showed the risk score as "5.9 / 10", while another page showed "59 / 100", and a third showed "5.92%", making it look like three different scores.

### Technical Problem
Different frontend components applied arbitrary `* 10` or `toFixed(1)` transformations to the backend priority score.

### Symptoms
Inconsistent score formatting across Command Center, Findings Catalog, and PDF export.

### Root Cause
Lack of a centralized formatting utility for risk priority.

### Solution
Standardized on the canonical **0.00 to 10.00 scale** (matching standard CVSS format) with two decimal places. Posture score uses **0 to 100 integer scale**.

### Technical Implementation
- Updated `frontend/src/utils/formatters.ts`.
- Standardized `priority_score.toFixed(2)` on a `/ 10.0` scale.

### Verification
Checked all views for A018: consistently displays **`5.92 / 10.0`** (Priority) and **`70 / 100`** (Posture).

### Before
Mismatched scales (`5.9`, `59`, `5.92%`) across different screens.

### After
Unified presentation: Priority is `5.92 / 10.0`, Posture is `70 / 100`.

### Lesson
Numerical metrics must use explicit, standardized formatting helpers across the entire presentation layer.

### Evidence
`backend/tests/test_cve_nvd_provenance_and_scale.py` PASSED.

---

## Challenge 22 — Evidence Probe Used HEAD While Actual OpenAPI Validation Required GET

### Simple Explanation
The scanner checked if the API documentation existed by asking for the header only (HEAD request), but the server answered "Method Not Allowed" (405), causing the scanner to miss the vulnerability.

### Technical Problem
The initial network probe sent `HEAD /openapi.json`. The web server rejected HEAD requests with HTTP 405 Method Not Allowed, even though sending a normal `GET` request returned HTTP 200 with the full OpenAPI schema.

### Symptoms
Scanner reported `/openapi.json` as inaccessible or inconclusive.

### Root Cause
Using `HEAD` requests for endpoint discovery without falling back to `GET`.

### Solution
Updated probe logic in `world_monitor_assessment_engine.py` to use `GET` with appropriate stream limits and `Accept: application/json` headers to inspect the actual response body.

### Technical Implementation
- Modified `backend/app/services/world_monitor_assessment_engine.py` line 340.
- Created canonical evidence record `EV-WM-API-DOCS-A018-GET`.

### Verification
Executed probe: successfully captured HTTP 200 OK with `application/json` payload containing the valid OpenAPI 3.1.0 document.

### Before
HEAD probe returned 405 Method Not Allowed; schema missed.

### After
GET probe returned 200 OK with full schema verification.

### Lesson
REST API validation must use standard `GET` requests with appropriate body inspection rather than relying on `HEAD`.

### Evidence
`backend/tests/test_api_docs_get_probe_precision.py` PASSED.

---

## Challenge 23 — Technical Evidence Did Not Explicitly Record OpenAPI Version/Schema Detection

### Simple Explanation
The evidence record showed the raw JSON data, but did not explicitly state what version of OpenAPI was running or what API title was exposed.

### Technical Problem
The raw data was stored as an unparsed string blob without extracting structural metadata into the evidence description.

### Symptoms
Auditors had to manually read through thousands of lines of raw JSON to verify what API was exposed.

### Root Cause
Missing structural parsing in the evidence generation pipeline.

### Solution
Enhanced evidence capture to parse the JSON response, extract `openapi: "3.1.0"` and `info.title: "WorldMonitor API"`, and record these explicitly in `what_found` and the evidence description.

### Technical Implementation
- Modified `backend/app/services/world_monitor_assessment_engine.py`.
- Added structured attributes to `EvidenceRecord`.

### Verification
Inspected evidence record: clearly displays `OpenAPI Version: 3.1.0`, `API Title: WorldMonitor API`, and `Endpoints Detected: Yes`.

### Before
Opaque JSON blob requiring manual inspection.

### After
Clear, structured summary of OpenAPI version and API metadata.

### Lesson
Technical evidence records should pair raw captured payloads with parsed, human-readable structural summaries.

### Evidence
`test_api_docs_get_probe_precision.py` PASSED.

---

## Challenge 24 — Evidence Validation AI Panel Used Stale Generic AI Text Instead of Canonical RAG Output

### Simple Explanation
The Evidence Validation page showed a hardcoded placeholder analysis from three weeks ago instead of the fresh, evidence-grounded AI analysis from the local Ollama engine.

### Technical Problem
The frontend component had a fallback string initialized in component state that was never replaced when the live RAG analysis completed asynchronously.

### Symptoms
AI Analysis card showed outdated text discussing an unrelated test endpoint.

### Root Cause
Missing `useEffect` dependency and state synchronization between `AppContext` and `EvidenceValidationPage.tsx`.

### Solution
Connected the component directly to the live `useApp().aiAnalysis` state, triggering dynamic re-fetching when active finding changes.

### Technical Implementation
- Modified `frontend/src/pages/EvidenceValidationPage.tsx` lines 120-145.

### Verification
Navigated to Evidence Validation page: AI Analysis tab dynamically displays the current, bounded analysis for `WM-API-DOCS-A018`.

### Before
Stale placeholder text displayed in AI panel.

### After
Fresh, canonical RAG output rendered dynamically.

### Lesson
Asynchronous AI synthesis results must be bound to active finding state rather than initialized statically.

### Evidence
Frontend test suite passed.

---

## Challenge 25 — Assessment-Level Audit Event Incorrectly Used Assessment ID as finding_id

### Simple Explanation
In the database, an event that simply noted "Assessment Started" recorded the assessment's ID inside the finding ID column, confusing reports into thinking there was a finding named after the assessment.

### Technical Problem
`log_audit_event()` was called with `finding_id=assessment.id` in `assessment_service.py` when creating pipeline-level events.

### Symptoms
Foreign key query for findings returned orphan errors or misattributed audit records.

### Root Cause
Copy-paste parameter error in `assessment_service.py` line 67.

### Solution
Set `finding_id=None` for all assessment-level events (`ASSESSMENT_STARTED`, `ASSESSMENT_CREATED`, `TARGET_SELECTED`, `ASSESSMENT_COMPLETED`). `finding_id` is only populated when an event directly concerns a specific finding.

### Technical Implementation
- Modified `backend/app/services/assessment_service.py`.
- Updated `backend/tests/test_audit_matrix.py`.

### Verification
Inspected audit records for A018: `ASSESSMENT_STARTED` has `finding_id = null`, while `FINDING_CREATED` has `finding_id = 'WM-API-DOCS-A018'`.

### Before
`ASSESSMENT_STARTED` had `finding_id = 'KAVACH-WM-20260923-A018'`.

### After
`ASSESSMENT_STARTED` has `finding_id = null`.

### Lesson
Event logging schemas must maintain strict type separation between container entities and child entities.

### Evidence
`test_audit_matrix.py::test_audit_05_database_referential_integrity` PASSED.

---

## Challenge 26 — Global Advisory Correlation Used Shared CWE as an Overly Strong Matching Signal

### Simple Explanation
Because both the local target and an external Microsoft Windows security advisory shared the weakness "Information Disclosure" (CWE-200), the system falsely claimed the website was vulnerable to the Windows bug!

### Technical Problem
The external advisory correlation engine matched advisories to local targets if `advisory.cwe_id == finding.cwe_id`, ignoring software vendor, product name, and target technology stack.

### Symptoms
World Situational Monitor displayed critical Microsoft Exchange and Windows Kernel CVEs as active threats to `www.worldmonitor.app`.

### Root Cause
Overly broad correlation rule in `correlation_service.py`.

### Solution
Refined correlation logic to require technology stack alignment (e.g. matching web frameworks, runtime servers, or specific libraries) in addition to CWE. When no technology match exists, the advisory is categorized as `NO DIRECT LOCAL MATCH`.

### Technical Implementation
- Modified `backend/app/services/world_monitor_assessment_engine.py` line 890.
- Updated `backend/app/services/correlation_service.py`.

### Verification
Queried World Situational Monitor for A018: 0 external advisories correlated (`NO DIRECT LOCAL MATCH`). False attribution eliminated.

### Before
Unrelated Windows/Cisco CVEs attributed to World Monitor.

### After
0 false correlations; local finding clearly separated from global advisories.

### Lesson
Shared weakness classification (CWE) is never sufficient proof of external vulnerability applicability without technology stack verification.

### Evidence
`backend/tests/test_world_monitor_real_target.py` PASSED.

---

## Challenge 27 — World Situational Monitor Displayed Incorrect Local Finding Count

### Simple Explanation
The top of the World Situational Monitor screen said "Active Assessment Target: www.worldmonitor.app (0 local findings)" even though we had already validated 1 confirmed finding.

### Technical Problem
The count was calculated by querying all findings where `finding.category == "Global Advisory"`, which matched external threat feeds instead of querying actual local findings for the active assessment.

### Symptoms
Header banner showed `(0 local findings)` while Findings Catalog showed `1 local finding`.

### Root Cause
Misconfigured query filter in `WorldMonitorPage.tsx`.

### Solution
Updated count calculation to query findings scoped to `activeAssessment.id`: `findings.filter(f => f.assessment_id === activeAssessment.id).length`.

### Technical Implementation
- Modified `frontend/src/pages/WorldMonitorPage.tsx` lines 85-92.

### Verification
Inspected World Situational Monitor: banner accurately displays `Active Assessment Target: www.worldmonitor.app (1 local finding)`.

### Before
Displayed `(0 local findings)`.

### After
Displayed `(1 local finding)`.

### Lesson
UI summary counters must use the identical data aggregation query used by primary catalog screens.

### Evidence
Manual UI verification and automated route test passed.

---

## Challenge 28 — Command Center Navigation Opened the Wrong Module

### Simple Explanation
Clicking the "Command Center" button in the navigation bar unexpectedly took the user to the "World Situational Monitor" page instead of the Command Center.

### Technical Problem
The route definition for `Command Center` was mapped to the same component (`<WorldMonitorPage />`) as World Situational Monitor in `App.tsx`, and the sidebar navigation link had an incorrect URL path.

### Symptoms
User could not navigate to the primary executive dashboard.

### Root Cause
Route mapping collision in `frontend/src/App.tsx`.

### Solution
Corrected route mapping in `App.tsx`:
- `/command-center` → `<CommandCenterPage />`
- `/world-monitor` → `<WorldMonitorPage />`
Updated `Sidebar.tsx`, `Navbar.tsx`, and `WorkspaceSubnav.tsx` to preserve distinct routes.

### Technical Implementation
- Modified `frontend/src/App.tsx`.
- Modified `frontend/src/components/layout/Navbar.tsx`.
- Modified `frontend/src/components/layout/Sidebar.tsx`.
- Modified `frontend/src/components/common/WorkspaceSubnav.tsx`.

### Verification
Ran frontend test `frontend/tests/navigation_routes.test.mjs` (6/6 scenarios passed). Both click navigation and direct URL access render their respective distinct pages.

### Before
Command Center button opened World Situational Monitor.

### After
Command Center opens executive dashboard; World Monitor opens threat feed.

### Lesson
Navigation menus and router definitions must be covered by route-isolation regression tests.

### Evidence
`navigation_routes.test.mjs` PASSED.

---

## Challenge 29 — Command Center Confirmed-Finding Count Treated STILL_OPEN as Not-Confirmed

### Simple Explanation
Command Center showed "0 confirmed / 1 total" because the vulnerability was still open after re-testing, making it look like the scan hadn't found anything verified.

### Technical Problem
The aggregation logic in `CommandCenterPage.tsx` checked `f.status === 'CONFIRMED'`. When a re-test completed and transitioned status to `STILL_OPEN`, this check returned `false`.

### Symptoms
Command Center showed:
`LOCAL FINDINGS: 0 confirmed / 1 total`
even though technical evidence was 100% verified.

### Root Cause
Confusing the finding's technical confirmation status with its remediation lifecycle status.

### Solution
Updated aggregation: a finding is confirmed if its technical evidence validates its existence (`status in ['CONFIRMED', 'STILL_OPEN', 'VERIFIED']` with valid evidence).

### Technical Implementation
- Modified `frontend/src/pages/CommandCenterPage.tsx` lines 95-108.
- Added regression test `frontend/tests/command_center_finding_semantics.test.mjs`.

### Verification
Command Center displays `LOCAL FINDINGS: 1 confirmed / 1 total`.

### Before
Displayed `0 confirmed / 1 total`.

### After
Displayed `1 confirmed / 1 total`.

### Lesson
A finding whose remediation re-test failed (`STILL_OPEN`) remains a confirmed finding.

### Evidence
`command_center_finding_semantics.test.mjs` PASSED (5/5 tests).

---

## Challenge 30 — Command Center Risk/Posture Labels Differed from Report

### Simple Explanation
Command Center said the target had a "LOW" risk level, but the generated Security Report said it had a "MODERATE RISK", confusing the security team.

### Technical Problem
Command Center derived `riskLevel` from a formula that required at least one Critical or High finding to trigger Medium risk. Because `WM-API-DOCS-A018` is Medium severity, Command Center evaluated it as `LOW`, whereas Report Export evaluated the posture score of 70 as `MODERATE RISK`.

### Symptoms
Dashboard: `RISK LEVEL: LOW`.
Report: `SECURITY POSTURE: MODERATE RISK`.

### Root Cause
Inconsistent severity threshold branching between dashboard calculations and report export calculations.

### Solution
Synchronized risk level evaluation: Medium severity findings (such as `WM-API-DOCS-A018`) with posture score <= 70 evaluate canonically to **`MEDIUM`** risk level and **`MODERATE RISK`** posture everywhere.

### Technical Implementation
- Modified `frontend/src/pages/CommandCenterPage.tsx`.
- Updated `backend/app/services/report_service.py`.
- Added test `frontend/tests/posture_risk_consistency.test.mjs`.

### Verification
Command Center and Report both display `MEDIUM` risk level and `MODERATE RISK` (Score: 70/100, Priority: 5.92/10.0).

### Before
Dashboard showed LOW; Report showed MODERATE RISK.

### After
Both show MEDIUM / MODERATE RISK.

### Lesson
Executive risk categories must be derived from identical mathematical score brackets across all reporting surfaces.

### Evidence
`posture_risk_consistency.test.mjs` PASSED.

---

## Challenge 31 — Stage Telemetry Leaked RETEST_* Events into Historical Stage Logs

### Simple Explanation
When inspecting the log window for Stage 2 ("Assess"), events from a re-test performed 8 hours later appeared inside the historical scan log, making it look like the original scan took 8 hours.

### Technical Problem
The stage telemetry filter in `AssessmentProgressPage.tsx` filtered events using broad substring matches (`type.includes('OBSERVATION')`, `type.includes('EVIDENCE')`). Later re-test events (`RETEST_OBSERVATION_CAPTURED`, `RETEST_EVIDENCE_CREATED`) matched these filters and were injected into historical stage inspection logs.

### Symptoms
`ASSESS` stage displayed `RETEST_OBSERVATION_CAPTURED` from 21:50:21 inside an assessment that completed at 10:00:31.
`VALIDATE` stage displayed `RETEST_EVIDENCE_CREATED`.

### Root Cause
Lack of scoping between pipeline execution events and post-assessment re-test events in frontend filter.

### Solution
Created strict telemetry scoping filter:
1. All `RETEST_*` events are excluded from historical stage inspection logs.
2. `RETEST_*` events remain fully visible in the global **Audit Trail** and **Live Activity feed**.
3. Each stage shows only its corresponding execution events from the assessment run.

### Technical Implementation
- Modified `frontend/src/pages/AssessmentProgressPage.tsx` lines 60-145.
- Added regression tests `backend/tests/test_stage_telemetry_scoping.py` and `frontend/tests/stage_telemetry_scoping.test.mjs`.

### Verification
Inspected `AssessmentProgressPage.tsx`:
- `ASSESS`: shows only the 26 original assessment events from 10:00:31. Zero `RETEST_*` events.
- `VALIDATE`: shows only the 15 original validation events from 10:00:31. Zero `RETEST_*` events.
- Live Activity Panel & Audit Trail: retain all 72 events (including all 25 re-test events).

### Before
Historical stage logs contaminated with later re-test events.

### After
Clean separation: stage logs reflect original execution; Audit Trail reflects complete chronological lifecycle.

### Lesson
Execution telemetry for a closed pipeline stage must be immutable and cannot absorb subsequent lifecycle operations.

### Evidence
`test_stage_telemetry_scoping.py` PASSED (6/6 tests).

---

## Challenge 32 — Stage Lifecycle Contained an Incorrect COMPLETE → REPORT Transition

### Simple Explanation
The audit log contained a bizarre event saying: "Assessment stage advanced from COMPLETE to REPORT", even though the scan had already finished and was already in the Report stage.

### Technical Problem
`backend/app/services/url_scanner_service.py` and `schemas.py` stored `current_stage="COMPLETE"` (using a status string as a stage name). When `advance_stage(..., "REPORT")` was subsequently invoked, the service compared `old_stage="COMPLETE"` to `target_stage="REPORT"` and logged an invented transition.

### Symptoms
Audit Trail contained confusing event:
`Assessment stage advanced from COMPLETE to REPORT (100%).`

### Root Cause
Treating assessment status `"COMPLETE"` as a stage identifier instead of using the canonical 8th stage `"REPORT"`.

### Solution
1. Changed `current_stage` defaults and assignments in `url_scanner_service.py` and `schemas.py` from `"COMPLETE"` to `"REPORT"`.
2. Updated `advance_stage` in `assessment_service.py` to normalize legacy `old_stage == "COMPLETE"` to `"REPORT"`.
3. Added guard: if `old_stage == target_stage` or if already completed at `REPORT`, `advance_stage` is a no-op that does not emit redundant or invalid transitions.

### Technical Implementation
- Modified `backend/app/services/assessment_service.py` lines 86-105.
- Modified `backend/app/services/url_scanner_service.py` line 871.
- Modified `backend/app/schemas/schemas.py` line 36.
- Modified `frontend/src/components/common/WorkflowStepper.tsx`.
- Modified `frontend/src/pages/AssessmentProgressPage.tsx`.

### Verification
Ran `test_advance_stage_no_duplicate_or_invalid_transition` in `test_stage_telemetry_scoping.py`. Invoking `advance_stage` on completed assessment generates zero new audit events and emits no `COMPLETE → REPORT` transition.

### Before
Invalid transition `COMPLETE → REPORT` logged in audit trail.

### After
Canonical 8-stage lifecycle enforced; no-op transitions prevented.

### Lesson
Stage models and status models must remain distinct concepts; terminal stages must reject redundant forward transitions.

### Evidence
`backend/tests/test_stage_telemetry_scoping.py::test_advance_stage_no_duplicate_or_invalid_transition` PASSED.

---

## Summary of Verification Evidence

All 32 challenges have been verified with automated regression tests currently passing in the repository:

- **Frontend Tests (`node --test tests/*.test.mjs`)**: 23/23 PASSED.
- **Backend Tests (`python -m pytest backend/tests/...`)**: 32/32 PASSED.
- **Application Data Integrity**: 0 findings modified, 0 evidence records deleted, 0 audit events modified or deleted.
