# KAVACH 6.0 — UI/UX Changelog & QA Verification Cycle

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation  

---

## QA & Hardening Cycle Changelog (September 2026)

This changelog records the meaningful UI/UX improvements, semantic corrections, and state synchronization fixes implemented and verified during the September 2026 end-to-end QA cycle.

### 1. Assessment Completion & Stepper State Correction
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/components/common/WorkflowStepper.tsx`, `frontend/src/pages/AssessmentProgressPage.tsx`
- **Changes**:
  - Normalized stage identifier `'COMPLETE'` to canonical 8th stage `'REPORT'`.
  - Added `assessmentCompleted` precedence guard (`status === 'COMPLETED' || progress >= 100`) so that when the pipeline finishes, all stages up to and including current render as completed with green checkmarks, resolving the issue where Stage 8 falsely rendered as `RUNNING` at 100%.

### 2. Stage Telemetry Scoping & Log Isolation
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/pages/AssessmentProgressPage.tsx`
- **Changes**:
  - Implemented strict stage telemetry filter in `stageAudits`.
  - Excluded post-assessment `RETEST_*` events from historical stage inspection logs (`ASSESS`, `VALIDATE`).
  - Excluded pipeline-level `ASSESSMENT_STAGE_ADVANCED` events from individual module stdout windows.
  - Preserved all 25 `RETEST_*` events in the Live Activity Feed and Audit Trail without data loss.

### 3. Command Center Navigation & Route Isolation
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/App.tsx`, `frontend/src/components/layout/Navbar.tsx`, `frontend/src/components/layout/Sidebar.tsx`, `frontend/src/components/common/WorkspaceSubnav.tsx`
- **Changes**:
  - Resolved route collision where clicking "Command Center" navigated to `/world-monitor`.
  - Established dedicated route `/command-center` mapping directly to `<CommandCenterPage />`.
  - Verified distinct route paths across all navigation bars, sidebar links, and browser direct URLs.

### 4. Command Center Confirmed Finding Semantics
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/pages/CommandCenterPage.tsx`
- **Changes**:
  - Decoupled technical evidence confirmation from remediation lifecycle status.
  - Updated local findings counter so findings with validated technical evidence whose remediation status is `STILL_OPEN` correctly count as confirmed findings.
  - Verified Command Center displays `LOCAL FINDINGS: 1 confirmed / 1 total` for `KAVACH-WM-20260923-A018`.

### 5. Security Posture & Risk Level Consistency
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/pages/CommandCenterPage.tsx`, `backend/app/services/report_service.py`
- **Changes**:
  - Synchronized severity threshold branching between dashboard calculations and report export calculations.
  - Medium severity findings (such as `WM-API-DOCS-A018`) with posture score <= 70 now evaluate uniformly to **`MEDIUM`** risk level and **`MODERATE RISK`** posture across Command Center, Findings Catalog, and Security Report.

### 6. Report Executive Evidence Deduplication
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/pages/SecurityReportPage.tsx`, `backend/app/services/report_service.py`
- **Changes**:
  - Executive header displays unique verified vulnerability proofs (`confirmed_evidence = 1`, `evidence_proofs = 1`) rather than raw database row count (`2`).
  - Added visual distinction badges: `Canonical Active Proof` for `EV-WM-API-DOCS-A018-GET` vs `Historical Artifact (Superseded)` for initial baseline probe.
  - Rendered explicit relationship notes explaining artifact provenance.

### 7. Evidence Validation & Re-Verification Modal Persistence
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/components/common/ReVerificationModal.tsx`, `frontend/src/pages/EvidenceValidationPage.tsx`
- **Changes**:
  - Decoupled live re-test submission from automatic modal dismissal.
  - Modal remains open in an active `RESULT` state displaying the before/after state diff, live HTTP response status, and new SHA-256 hash.
  - Added baseline artifact selector allowing auditors to toggle between canonical GET proof and historical probe artifacts.

### 8. World Situational Monitor Local Finding Counter
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/pages/WorldMonitorPage.tsx`
- **Changes**:
  - Replaced global category filter with strict `assessment_id` scoping.
  - Header banner accurately displays `Active Assessment Target: www.worldmonitor.app (1 local finding)`.

### 9. AI Grounding & RAG State Synchronization
- **Date**: 2026-09-23
- **Files Modified**: `frontend/src/pages/EvidenceValidationPage.tsx`
- **Changes**:
  - Bound AI Analysis panel to live `AppContext` state, eliminating stale hardcoded placeholder text.
  - Rendered four grounded sections: Observed Fact, Supported Interpretation, Not-Proven Boundaries, and Targeted Remediation.
