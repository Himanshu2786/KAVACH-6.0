# KAVACH 6.0 — Annotated Repository File Structure

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation  

---

```
📁 KAVACH 6.0/
 │
 ├── 🚀 START KAVACH 1.0 .bat          # Primary one-click launcher (Vite Frontend + FastAPI Backend)
 ├── ⚙️ START KAVACH 2.0 .bat          # Secondary dev launcher & environment initializer
 ├── 🧪 TEST_KAVACH.bat                # Automated verification script
 ├── 📄 1.0 UPDATE CONTEXT.bat         # Snapshot generation launcher (runs tools/generate_chatgpt_snapshot.py)
 ├── 📄 README.md                      # Quickstart, project overview & documentation index
 ├── 📄 CHALLENGES_TO_SOLUTIONS.md     # 32 engineering challenges & verified solutions
 ├── 📄 KAVACH_DEVELOPER_DOCUMENTATION.md # Master technical manual (All 40 subsystems)
 ├── 📄 KAVACH_BACKEND_ARCHITECTURE.md # FastAPI async architecture, routes & services
 ├── 📄 KAVACH_DEPENDENCIES.md         # Full dependency inventory & selection rationale
 ├── 📄 KAVACH_FILE_STRUCTURE.md       # Annotated repository tree (this document)
 ├── 📄 KAVACH_KNOWLEDGE_ENGINE.md     # CWE/OWASP knowledge mapping & correlation rules
 ├── 📄 KAVACH_MASTER_CONTEXT.md       # System prompt & architectural ground truth
 ├── 📄 KAVACH_MODULES.md              # Core functional modules specification
 ├── 📄 KAVACH_OLLAMA_INTEGRATION.md   # Local Ollama AI & offline fallback guide
 ├── 📄 KAVACH_RAG_ARCHITECTURE.md     # RAG vector store & lexical prompt grounding
 ├── 📄 kavach.db                      # Persistent SQLite database (WAL mode enabled)
 ├── 📄 requirements.txt               # Top-level Python dependency specification
 ├── 📄 main.py                        # Standalone Python entry point
 │
 ├── 📁 backend/                       # Core FastAPI REST Backend Engine
 │    ├── requirements.txt             # Backend-specific Python dependencies
 │    ├── app/                         # FastAPI Application Package
 │    │    ├── main.py                 # FastAPI app factory, CORS, static mounting
 │    │    ├── core/                   # Core Database & Time Utilities
 │    │    │    ├── database.py        # SQLAlchemy engine, session maker, WAL pragmas
 │    │    │    └── time.py            # IST / ISO-8601 standardized timestamp helpers
 │    │    ├── models/                 # SQLAlchemy Declarative Models
 │    │    │    └── models.py          # Assessment, Finding, EvidenceRecord, AuditEvent
 │    │    ├── schemas/                # Pydantic v2 Request/Response Contracts
 │    │    │    └── schemas.py         # AssessmentCreate, AssessmentResponse, FindingResponse
 │    │    ├── data/                   # Data Seeding & Taxonomies
 │    │    │    └── seed_data.py       # Curated CWE/OWASP taxonomy definitions
 │    │    ├── api/routes/             # REST Route Controllers
 │    │    │    ├── assessments.py     # Assessment lifecycle & stage transitions
 │    │    │    ├── findings.py        # Findings catalog & status updates
 │    │    │    ├── evidence.py        # Evidence retrieval & raw data inspection
 │    │    │    ├── audit.py           # Forensic audit event querying
 │    │    │    ├── url_check.py       # Live URL security baseline checking
 │    │    │    ├── portable.py        # Consent and local scanning endpoints
 │    │    │    └── system.py          # Health checks & Ollama ping
 │    │    ├── services/               # Isolated Business Logic Layer
 │    │    │    ├── assessment_service.py              # 8-stage pipeline orchestrator
 │    │    │    ├── world_monitor_assessment_engine.py # Dedicated World Monitor probe & re-test
 │    │    │    ├── url_scanner_service.py             # HTTP header & TLS probe
 │    │    │    ├── evidence_service.py                # SHA-256 evidence hashing & deduplication
 │    │    │    ├── risk_service.py                    # Deterministic risk prioritization
 │    │    │    ├── correlation_service.py             # CWE/OWASP knowledge mapping
 │    │    │    ├── ai_analysis_service.py             # Negative-bounded AI explanation
 │    │    │    ├── rag_service.py                     # Lexical & semantic RAG retrieval
 │    │    │    ├── remediation_service.py             # Actionable mitigation playbooks
 │    │    │    ├── audit_service.py                   # Immutable event logging
 │    │    │    ├── report_service.py                  # Deduplicated executive report generator
 │    │    │    └── forensic_export_service.py         # Standardized JSON export
 │    └── tests/                       # Comprehensive Pytest Suite (32 test files)
 │         ├── test_stage_telemetry_scoping.py        # Stage isolation & transition semantics
 │         ├── test_evidence_deduplication.py         # 2 artifacts = 1 unique proof test
 │         ├── test_audit_matrix.py                   # End-to-end audit & referential integrity
 │         ├── test_retest_workflow.py                # Live re-test & STILL_OPEN persistence
 │         ├── test_navigation_routes.py              # Route isolation tests
 │         └── ... (27 additional tests)
 │
 ├── 📁 frontend/                      # React 19 + TypeScript + Vite Web Dashboard
 │    ├── package.json                 # Node.js dependencies & test scripts
 │    ├── vite.config.ts               # Vite bundler configuration
 │    ├── tsconfig.json                # TypeScript compiler configuration
 │    ├── tests/                       # Node.js Native Test Runner Suite
 │    │    ├── stage_telemetry_scoping.test.mjs       # Frontend stage telemetry filter tests
 │    │    ├── evidence_deduplication.test.mjs        # Report proof deduplication tests
 │    │    ├── command_center_finding_semantics.test.mjs # STILL_OPEN confirmation tests
 │    │    ├── navigation_routes.test.mjs             # Route mapping separation tests
 │    │    ├── posture_risk_consistency.test.mjs      # Risk level & posture consistency tests
 │    │    └── reverification_modal.test.mjs          # Modal state persistence tests
 │    └── src/                         # Frontend Application Source Code
 │         ├── main.tsx                # React DOM root entry point
 │         ├── App.tsx                 # Router & top-level navigation setup
 │         ├── types/                  # TypeScript Data Contracts
 │         │    └── index.ts           # Assessment, Finding, EvidenceRecord interfaces
 │         ├── services/               # REST API Client
 │         │    └── api.ts             # Typed fetch client connecting to backend
 │         ├── context/                # Global Application State
 │         │    └── AppContext.tsx     # Active assessment & real-time collection state
 │         ├── pages/                  # Page-Level Views
 │         │    ├── CommandCenterPage.tsx       # Executive posture dashboard
 │         │    ├── WorldMonitorPage.tsx        # World Situational Monitor
 │         │    ├── AssessmentProgressPage.tsx  # 8-stage stepper & stage telemetry
 │         │    ├── FindingsCatalogPage.tsx     # Findings registry
 │         │    ├── EvidenceValidationPage.tsx  # Proof inspection & live re-test
 │         │    ├── RiskScoringPage.tsx         # Mathematical CVSS breakdown
 │         │    ├── RemediationPage.tsx         # Fix playbooks & diffs
 │         │    ├── SecurityReportPage.tsx      # Printable executive report
 │         │    └── AuditTrailPage.tsx          # Forensic event stream
 │         └── components/             # Reusable UI Components
 │              ├── common/            # GlassCard, Badge, WorkflowStepper, ReVerificationModal
 │              └── layout/            # Navbar, Sidebar, WorkspaceSubnav
 │
 ├── 📁 tools/                         # Maintenance & Snapshot Generators
 │    └── generate_chatgpt_snapshot.py # Generates INFO/KAVACH_COMPLETE_PROJECT.md
 │
 └── 📁 INFO/                          # Curated Architecture & Guide Documentation
      ├── FINAL_WORKING_STATUS.md      # Current verified QA status & SIH demo readiness
      ├── LIMITATIONS.md               # Honest engineering constraints & boundaries
      ├── PS_26163_COMPLIANCE.md       # Requirement-by-requirement SIH mapping
      ├── UI_CHANGELOG.md              # User interface fixes and enhancements
      ├── FEATURE_FILE_MAP.md          # Technical cross-reference map
      ├── ASSESSMENT_FLOW.md           # 17-step workflow vs 8-stage pipeline
      ├── KAVACH_WORLD_MONITOR.md      # World Monitor target empirical audit details
      ├── EVIDENCE_SYSTEM.md           # Cryptographic evidence architecture
      └── AI_SYSTEM.md                 # Local Ollama & RAG architecture
```
