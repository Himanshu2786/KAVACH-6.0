# KAVACH — Feature-to-File Map

This document maps all platform capabilities to their exact implementation files across the frontend and backend codebases.

---

## 1. Feature Map Table

| Platform Capability | Frontend File(s) | Backend File(s) | Database Model(s) |
|---|---|---|---|
| **Public Landing Page & CTA** | `frontend/src/pages/HomePage.tsx` | `backend/app/api/routes/assessments.py` | `Assessment` |
| **Authorization Confirmation** | `frontend/src/components/common/AuthorizationModal.tsx` | `backend/app/api/routes/assessments.py` | `Assessment.authorization_confirmed` |
| **Assessment Lifecycle & Progress** | `frontend/src/pages/AssessmentProgressPage.tsx`, `frontend/src/pages/NewAssessmentPage.tsx` | `backend/app/services/assessment_service.py`, `backend/app/api/routes/assessments.py` | `Assessment` |
| **Discovery & Attack Surface** | `frontend/src/pages/DiscoveryPage.tsx` | `backend/app/services/discovery_service.py` | `DiscoveryItem` |
| **Findings Catalog & Detail** | `frontend/src/pages/FindingsPage.tsx`, `frontend/src/pages/FindingDetailPage.tsx` | `backend/app/api/routes/findings.py` | `Finding` |
| **Verifiable Evidence & SHA-256** | `frontend/src/pages/EvidenceValidationPage.tsx` | `backend/app/services/evidence_service.py`, `backend/app/api/routes/evidence.py` | `EvidenceRecord` |
| **Technical Terminal Verification** | `frontend/src/components/common/TechnicalTerminalViewer.tsx` | `backend/app/services/validation_service.py`, `backend/app/api/routes/evidence.py` | `EvidenceRecord` |
| **Re-Verification (Before/After)** | `frontend/src/components/common/ReVerificationModal.tsx` | `backend/app/services/validation_service.py`, `backend/app/api/routes/evidence.py` | `ReVerificationRecord`, `Finding` |
| **Server-Side AI Analysis** | `frontend/src/pages/AiAnalysisPage.tsx` | `backend/app/services/ai_provider.py`, `backend/app/services/ai_analysis_service.py` | `Finding.ai_*` |
| **Remediation Playbooks** | `frontend/src/pages/RemediationCenterPage.tsx` | `backend/app/services/remediation_service.py` | `Finding.recommended_remediation` |
| **Knowledge Base (CWE / OWASP)** | `frontend/src/pages/KnowledgeCorrelationPage.tsx` | `backend/app/services/knowledge_service.py` | `KnowledgeRecord` |
| **Executive & Compliance Reports** | `frontend/src/pages/SecurityReportPage.tsx` | `backend/app/services/report_service.py`, `backend/app/api/routes/reports.py` | Aggregated Models |
| **Tamper-Evident Audit Trails** | `frontend/src/pages/AssessmentHistoryPage.tsx` | `backend/app/core/audit.py`, `backend/app/api/routes/system.py` | `AuditEvent` |
| **System & SOC Telemetry** | `frontend/src/pages/SystemStatusPage.tsx` | `backend/app/services/health_service.py`, `backend/app/api/routes/system.py` | `SystemSetting` |

---

## 2. Directory Layout Reference

```
KAVACH 6.0/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # REST routers (assessments, findings, evidence, system, reports)
│   │   ├── core/              # Config, database engine, audit logger
│   │   ├── data/              # Seed fixtures (World Monitor 7 categories)
│   │   ├── models/            # SQLAlchemy database schemas
│   │   ├── schemas/           # Pydantic validation models
│   │   └── services/          # Business logic engines (AI, Evidence, Validation, Risk, Discovery)
│   └── tests/                 # Automated test suite
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI (Cards, Modals, Terminal, TopHeader, Sidebar)
│   │   ├── context/           # AppContext state manager
│   │   ├── pages/             # Route views (HomePage, CommandCenter, Evidence, Terminal, Reports)
│   │   ├── services/          # Axios API client
│   │   └── types/             # TypeScript definitions
└── INFO/                      # 10 Master Architectural Documentation Files
```
