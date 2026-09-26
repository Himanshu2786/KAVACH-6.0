# KAVACH 6.0 — Feature-to-File Technical Map

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation  

---

## 1. Feature Map Table

| Platform Capability | Frontend File(s) | Backend Route(s) | Service Layer | Data Model(s) | Test Suite File(s) | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Command Center Dashboard** | `frontend/src/pages/CommandCenterPage.tsx` | `backend/app/api/routes/assessments.py` | `assessment_service.py`, `risk_service.py` | `Assessment`, `Finding` | `test_command_center_finding_semantics.test.mjs` | `IMPLEMENTED + TESTED LOCALLY` |
| **World Situational Monitor** | `frontend/src/pages/WorldMonitorPage.tsx` | `backend/app/api/routes/assessments.py` | `world_monitor_assessment_engine.py` | `Assessment`, `Finding` | `test_world_monitor_real_target.py` | `IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR` |
| **8-Stage Pipeline Stepper** | `frontend/src/pages/AssessmentProgressPage.tsx`, `WorkflowStepper.tsx` | `POST /assessments/{id}/advance-stage` | `assessment_service.py` | `Assessment` | `test_stage_telemetry_scoping.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **Stage Telemetry Scoping** | `frontend/src/pages/AssessmentProgressPage.tsx` | `GET /audit-trail` | `audit_service.py` | `AuditEvent` | `stage_telemetry_scoping.test.mjs` | `IMPLEMENTED + TESTED LOCALLY` |
| **Findings Catalog & Detail** | `frontend/src/pages/FindingsCatalogPage.tsx` | `backend/app/api/routes/findings.py` | `finding_service.py` | `Finding` | `test_data_isolation.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **Evidence & Deduplication** | `frontend/src/pages/EvidenceValidationPage.tsx` | `backend/app/api/routes/evidence.py` | `evidence_service.py` | `EvidenceRecord` | `test_evidence_deduplication.py` | `IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR` |
| **Live Re-Verification** | `frontend/src/components/common/ReVerificationModal.tsx` | `POST /findings/{id}/reverify` | `world_monitor_assessment_engine.py` | `EvidenceRecord`, `Finding` | `test_retest_workflow.py`, `reverification_modal.test.mjs` | `IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR` |
| **Risk Prioritization (5.92/10)**| `frontend/src/pages/RiskScoringPage.tsx` | `GET /assessments/{id}/risk-breakdown` | `risk_service.py` | `Finding` | `test_risk_prioritization_validation.py` | `IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR` |
| **Taxonomy Mapping (CWE-200)** | `frontend/src/pages/FindingsCatalogPage.tsx` | `backend/app/api/routes/findings.py` | `correlation_service.py` | `KnowledgeItem` | `test_correlation_consistency.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **Bounded AI Analysis** | `frontend/src/pages/EvidenceValidationPage.tsx` | Internal Engine | `ai_analysis_service.py`, `ollama_service.py` | `Finding` | `test_priority7_ollama_analyst.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **RAG Lexical Fallback** | `frontend/src/pages/EvidenceValidationPage.tsx` | Internal Service | `rag_service.py` | `KnowledgeItem` | `test_rag_finding_grounding.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **Remediation Playbooks** | `frontend/src/pages/RemediationPage.tsx` | `backend/app/api/routes/findings.py` | `remediation_service.py` | `Finding` | `test_audit_matrix.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **Report Generation & Export** | `frontend/src/pages/SecurityReportPage.tsx` | `GET /assessments/{id}/export` | `report_service.py`, `forensic_export_service.py` | Aggregated Models | `evidence_deduplication.test.mjs` | `IMPLEMENTED + TESTED LOCALLY` |
| **Forensic Audit Trail** | `frontend/src/pages/AuditTrailPage.tsx` | `backend/app/api/routes/audit.py` | `audit_service.py` | `AuditEvent` | `test_audit_matrix.py` | `IMPLEMENTED + TESTED LOCALLY` |
| **URL Security Check** | `frontend/src/pages/UrlSecurityCheckPage.tsx` | `POST /url-check` | `url_scanner_service.py` | `Assessment` | `test_assess_target_and_url_check.py` | `IMPLEMENTED + TESTED LOCALLY` |

---

## 2. Directory Layout Reference

```
KAVACH 6.0/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # REST controllers (assessments, findings, evidence, audit, url_check)
│   │   ├── core/              # Database engine, WAL pragmas, timezone helpers
│   │   ├── data/              # Seed fixtures (CWE/OWASP knowledge database)
│   │   ├── models/            # SQLAlchemy database models (Assessment, Finding, EvidenceRecord, AuditEvent)
│   │   ├── schemas/           # Pydantic v2 schemas
│   │   └── services/          # Business logic engines (World Monitor, Assessment, Evidence, Risk, RAG)
│   └── tests/                 # Comprehensive pytest test suite (32 test files)
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI (GlassCard, Badge, WorkflowStepper, ReVerificationModal)
│   │   ├── context/           # AppContext state manager
│   │   ├── pages/             # Route views (CommandCenter, WorldMonitor, Progress, Findings, Evidence, Reports)
│   │   ├── services/          # REST API client (api.ts)
│   │   └── types/             # TypeScript interfaces (index.ts)
│   └── tests/                 # Node.js native test runner regression suite (6 test files, 23 tests)
└── INFO/                      # Curated architecture, guide, and compliance documentation
```
