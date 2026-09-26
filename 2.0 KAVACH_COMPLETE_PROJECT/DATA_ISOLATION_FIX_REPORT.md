# KAVACH 6.0 — Assessment Data Isolation, Demo Contamination & Consistency Fix Report

## 1. Observed Issues

1. **Demo Contamination in Real Assessment Queries**:
   - For real assessment `ASM-F8CFA2EB` (`target_url = "https://www.worldmonitor.app"`, `status = "COMPLETED"`, `is_demo = false`, `total_findings = 0`), `GET /api/findings?assessment_id=ASM-F8CFA2EB` returned `[]`.
   - However, calling `GET /api/findings` returned seeded demo records (e.g. `KAV-2026-001`, `assessment_id = "ASM-DEMO-001"`), contaminating the real assessment workflow.
2. **Hardcoded ID Prefix in World Monitor Endpoint**:
   - `GET /api/assessments/world-monitor/latest` was reliant on a fallback query filtering by `Assessment.id.like("KAVACH-WM-%")`, which was incompatible with empirical World Monitor assessments assigned runtime IDs such as `ASM-F8CFA2EB`.
3. **Context Mixing Between URL Security Check and Full Security Assessment**:
   - In the Findings and Evidence UI, URL security check runs (e.g. `ASM-URL-20260922-2E03BE`) were shown as the active assessment even when the user was working on a full security assessment (`ASM-F8CFA2EB`).
4. **Context Loss on Refresh & Missing UI Scoping**:
   - Reloading the browser dropped the active assessment context.
   - Finding detail, evidence, and audit logs lacked strict cross-assessment ownership validation.

---

## 2. Root Causes Found

1. **`backend/app/api/routes/findings.py`**:
   - In `list_findings`, when no `assessment_id` was provided and no active real assessment had findings, the endpoint fell back to querying demo assessment IDs (`Assessment.is_demo == True`), leaking demo data into real workflows.
2. **`backend/app/api/routes/assessments.py`**:
   - `get_latest_world_monitor_assessment` included a legacy fallback query: `Assessment.id.like("KAVACH-WM-%")`. If no candidate matched an un-normalized string comparison, it defaulted to this synthetic prefix rather than respecting normalized target identity.
3. **`frontend/src/pages/FindingsPage.tsx`**:
   - Data source resolution checked `hasUrlData = Boolean(urlResult && urlResult.findings && urlResult.findings.length >= 0)`. Because `length >= 0` is always true, `sourceMode` was forced to `'url'`, overriding the active full assessment and showing `ASM-URL-*`.
4. **`frontend/src/context/AppContext.tsx`**:
   - `activeAssessment` was held only in React memory and not persisted to `localStorage`, causing loss of context on browser refresh.
   - `selectedFindingId` defaulted to the hardcoded demo finding `"KAV-2026-001"`.
   - `isDemoMode` defaulted to `true`, causing demo state flags across child components.
5. **`frontend/src/pages/FindingDetailPage.tsx`**:
   - Opened findings directly by finding ID without verifying `finding.assessment_id === activeAssessment.id`.
6. **`frontend/src/pages/EvidenceValidationPage.tsx`**:
   - Rendered URL scan evidence as the primary view even when a full assessment was active, blurring the boundary between URL checks and full assessments.
7. **`frontend/src/pages/AuditTrailPage.tsx`**:
   - Queried global audit events without scoping by default to `activeAssessment.id`.

---

## 3. Files Changed

| Component | File Path | Nature of Modification |
| :--- | :--- | :--- |
| **Backend API** | `backend/app/api/routes/findings.py` | Scoped `list_findings` strictly to active real assessment; returned `[]` when real assessment has 0 findings; removed demo fallback in real mode. |
| **Backend API** | `backend/app/api/routes/evidence.py` | Added cross-validation (`Finding.assessment_id == assessment_id`); scoped default evidence query to active real assessment. |
| **Backend API** | `backend/app/api/routes/assessments.py` | Added `normalize_target_url` helper; removed legacy `KAVACH-WM-%` fallback; identified latest real assessment strictly via target identity. |
| **Frontend API** | `frontend/src/services/api.ts` | Supported `is_demo` parameter in `getFindings`; supported `assessment_id` in `getEvidence`. |
| **Frontend State**| `frontend/src/context/AppContext.tsx` | Persisted `activeAssessment.id` in `localStorage`; synchronized `isDemoMode` with assessment `is_demo`; cleared default demo finding ID. |
| **Frontend UI** | `frontend/src/pages/FindingsPage.tsx` | Enforced `activeAssessment` priority; added Active Assessment Banner; added context switcher between Full Assessment and URL Check; added clean empty state for 0 findings. |
| **Frontend UI** | `frontend/src/pages/AssessmentHistoryPage.tsx` | Displayed exact status, stage, demo/real badge, and correct confirmed/total finding counts; clicking sets active context. |
| **Frontend UI** | `frontend/src/pages/FindingDetailPage.tsx` | Enforced `finding.assessment_id === activeAssessment.id` guard; displays isolation warning on cross-assessment finding access. |
| **Frontend UI** | `frontend/src/pages/EvidenceValidationPage.tsx` | Scoped evidence to `activeAssessment.id`; added source switcher between Full Assessment and URL Check; clean empty state for 0 findings. |
| **Frontend UI** | `frontend/src/pages/AuditTrailPage.tsx` | Passed `assessment_id: activeAssessment.id` by default with toggle to view All Events. |
| **Automated Tests**| `backend/tests/test_data_isolation.py` | Added tests for zero-fallback, demo isolation, target identity, URL check isolation, cross-assessment isolation, report isolation, and real `ASM-F8CFA2EB` validation. |
| **Automated Tests**| `backend/tests/test_api.py` | Updated `test_findings_retrieval` to query demo findings explicitly (`?is_demo=true`). |
| **Automated Tests**| `backend/tests/test_ollama_integration.py` | Updated AI finding explanation tests to query demo findings explicitly (`?is_demo=true`). |

---

## 4. API Behavior Before vs. After

| Endpoint | Behavior Before | Behavior After |
| :--- | :--- | :--- |
| `GET /api/findings?assessment_id=ASM-F8CFA2EB` | Returned `[]` (correct). | Returns `[]` (correct, strictly preserved). |
| `GET /api/findings` | Returned demo findings (`KAV-2026-001`, `ASM-DEMO-001`) even during real assessment workflows. | Scoped strictly to active real assessment. If active real assessment has 0 findings or none exists, returns `[]`. Never returns demo data. |
| `GET /api/findings?is_demo=true` | Returned mixed or demo findings. | Explicitly returns only demo findings (`is_demo == True`). |
| `GET /api/evidence?finding_id=FND&assessment_id=ASM` | Ignored `assessment_id` if `finding_id` was supplied. | Validates finding belongs to `assessment_id`; returns `[]` on mismatch. |
| `GET /api/assessments/world-monitor/latest` | Queried `id.like("KAVACH-WM-%")` as fallback. | Identifies latest assessment by target identity (`is_world_monitor_target(target_url)`) and `is_demo == false`. No ID prefix required. |

---

## 5. Frontend Behavior Before vs. After

| View / Action | Behavior Before | Behavior After |
| :--- | :--- | :--- |
| **Findings Page Data Source** | Forced to URL Check if any URL check was run (`hasUrlData` evaluated to true). | Defaults strictly to `activeAssessment.id`. URL check is kept in an isolated tab/toggle. |
| **Empty Real Assessment (0 Findings)** | Displayed generic "No findings match current filters" or fell back to demo findings. | Displays clean empty state: "No findings generated for this assessment. Assessment ASM-F8CFA2EB targeting https://www.worldmonitor.app has zero security vulnerabilities recorded." |
| **Browser Refresh** | `activeAssessment` was lost; defaulted to first assessment or reset state. | `activeAssessment` is restored from `localStorage.getItem('kavach_active_assessment_id')`. |
| **Assessment History Card** | Missing status badge, missing demo/real badge; hardcoded finding count fallbacks (`?? 3`, `?? 5`). | Displays exact status (`COMPLETED`/`RUNNING`), stage, real/demo badge, and actual finding counts (`${confirmed ?? 0} / ${total ?? 0}`). |
| **Finding Detail Inspection** | Displayed any finding regardless of active assessment. | Verifies `finding.assessment_id === activeAssessment.id`. Displays isolation warning if finding belongs to another assessment. |
| **Evidence Page** | Displayed URL Run ID (`ASM-URL-*`) and URL evidence even when a full assessment was selected. | Scoped to active assessment. Displays active assessment banner and zero-finding empty state when findings count is 0. URL Check evidence is in a separate toggle. |
| **Audit Trail** | Queried global audit ledger. | Scoped to `activeAssessment.id` by default with toggle to view All Events. |

---

## 6. Demo & URL Check Isolation Guarantees

1. **Demo Isolation**:
   - Seeded demo records (`ASM-DEMO-001`, `KAV-2026-001`, etc.) are only accessible when `is_demo=true` is explicitly requested or when the UI is explicitly in Demo mode.
   - For real assessments (`is_demo=false`), all scoped queries strictly filter out demo findings, demo evidence, demo risks, and demo audit logs.
2. **URL Check Isolation**:
   - `urlAssessmentState` is maintained as a separate branch in `AppContext`.
   - A URL check run ID (`ASM-URL-*`) never overwrites `activeAssessment` and is never presented as a Full Security Assessment.

---

## 7. Automated Test Suite Results

1. **`backend/tests/test_data_isolation.py`** (9 tests, 100% PASSED):
   - `test_isolation_test_a_real_assessment_zero_findings`: PASSED
   - `test_isolation_test_b_and_c_demo_findings_do_not_contaminate_real`: PASSED
   - `test_isolation_test_d_world_monitor_latest_without_id_prefix`: PASSED
   - `test_isolation_test_e_url_check_isolation`: PASSED
   - `test_isolation_test_f_cross_assessment_isolation_a_and_b`: PASSED
   - `test_isolation_test_g_report_isolation`: PASSED
   - `test_isolation_evidence_isolation`: PASSED
   - `test_isolation_test_j_no_active_assessment_or_empty_real`: PASSED
   - `test_isolation_real_asm_f8cfa2eb_validation`: PASSED
2. **Targeted Regression Suite** (`test_api.py`, `test_ollama_integration.py`, `test_data_isolation.py`):
   - 30 passed in 161s.
3. **Frontend Production Build** (`npm run build`):
   - `tsc -b && vite build`: PASSED (0 errors).

---

## 8. Real-World Assessment `ASM-F8CFA2EB` Validation

Direct test query verification:
- `GET /api/assessments/ASM-F8CFA2EB` -> `status_code = 200`, `status = "COMPLETED"`, `progress = 100`, `current_stage = "REPORT"`, `is_demo = False`.
- `GET /api/findings?assessment_id=ASM-F8CFA2EB` -> `status_code = 200`, returns `[]`.
- `GET /api/assessments/world-monitor/latest` -> `status_code = 200`, returns latest real World Monitor assessment by normalized target URL, without requiring `KAVACH-WM-*` prefix.
- Zero synthetic vulnerabilities exist or were created for World Monitor.
