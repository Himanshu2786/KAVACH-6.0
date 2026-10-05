# KAVACH 6.0 — PROJECT FILE MANIFEST

> **Generated**: 2026-09-28 16:11:05 UTC  
> **Platform Version**: KAVACH 6.0  
> **Total Curated Source Files**: 126  
> **Total Categories**: 6  
> **Project Root**: `C:\Users\Himanshu Raj\OneDrive\Desktop\KHAALI KAVACH\KAVACH 6.0`  

---

## 1. Curated Material File Manifest
The following files are materially involved in understanding, executing, testing, and documenting the KAVACH 6.0 platform:

| Relative Path | Category | Purpose | Source of Truth | SHA-256 Prefix |
| :--- | :--- | :--- | :--- | :--- |
| `frontend/package.json` | **FRONTEND** | Frontend dependencies and build scripts | `SOURCE_OF_TRUTH` | `d4699f14b4825af7...` |
| `frontend/vite.config.ts` | **FRONTEND** | Vite build configuration and server proxy rules | `SOURCE_OF_TRUTH` | `7870a22e46b40b62...` |
| `frontend/tsconfig.json` | **FRONTEND** | TypeScript compiler options and paths | `SOURCE_OF_TRUTH` | `770b4140bbb581e2...` |
| `frontend/src/main.tsx` | **FRONTEND** | Application entry point and React root mounting | `SOURCE_OF_TRUTH` | `c89383baab814e13...` |
| `frontend/src/App.tsx` | **FRONTEND** | Top-level layout, presentation bar, and route switching | `SOURCE_OF_TRUTH` | `b979160f04d05275...` |
| `frontend/src/index.css` | **FRONTEND** | Core styling, Tailwind directives, dark theme tokens | `SOURCE_OF_TRUTH` | `c26be1b262e71989...` |
| `frontend/src/App.css` | **FRONTEND** | Component utility styles and transitions | `SOURCE_OF_TRUTH` | `6e25a776d3e8102d...` |
| `frontend/src/context/AppContext.tsx` | **FRONTEND** | Global state management: active assessment, findings, toasts, demo mode | `SOURCE_OF_TRUTH` | `f95a485a2d412d14...` |
| `frontend/src/services/api.ts` | **FRONTEND** | REST API client mapping all backend endpoints | `SOURCE_OF_TRUTH` | `009123751bcec0c7...` |
| `frontend/src/types/index.ts` | **FRONTEND** | TypeScript domain interfaces for findings, evidence, assessments | `SOURCE_OF_TRUTH` | `64183d7c3fbdacbb...` |
| `frontend/src/components/layout/Navbar.tsx` | **FRONTEND** | Top navigation bar, status indicators, and presentation dropdown | `SOURCE_OF_TRUTH` | `902c638a861180b3...` |
| `frontend/src/components/layout/DemoJourneyBar.tsx` | **FRONTEND** | SIH hackathon presentation walkthrough bar | `SOURCE_OF_TRUTH` | `535da60f36630e59...` |
| `frontend/src/components/common/Badge.tsx` | **FRONTEND** | Reusable status and severity badges | `SOURCE_OF_TRUTH` | `89beaaaab0edd429...` |
| `frontend/src/components/common/GlassCard.tsx` | **FRONTEND** | Glassmorphic panel container component | `SOURCE_OF_TRUTH` | `5d7f3365561bab76...` |
| `frontend/src/components/common/WorkflowStepper.tsx` | **FRONTEND** | 8-stage pipeline visualization stepper | `SOURCE_OF_TRUTH` | `b94ddc767f095699...` |
| `frontend/src/pages/HomePage.tsx` | **FRONTEND** | Landing view and platform overview | `SOURCE_OF_TRUTH` | `a40ebb171eb6a6e5...` |
| `frontend/src/pages/CommandCenterPage.tsx` | **FRONTEND** | Executive posture dashboard and metric cards | `SOURCE_OF_TRUTH` | `11b074f0e587bb46...` |
| `frontend/src/pages/NewAssessmentPage.tsx` | **FRONTEND** | Scope Guard wizard and assessment configuration | `SOURCE_OF_TRUTH` | `a5b5bcc5c867b115...` |
| `frontend/src/pages/DiscoveryPage.tsx` | **FRONTEND** | Attack surface mapping and cataloged assets | `SOURCE_OF_TRUTH` | `98ff56d64474dd2a...` |
| `frontend/src/pages/AssessmentProgressPage.tsx` | **FRONTEND** | 8-stage execution stepper and live audit telemetry | `SOURCE_OF_TRUTH` | `6ed886286fb34f78...` |
| `frontend/src/pages/FindingsPage.tsx` | **FRONTEND** | Findings matrix, filtering, and catalog view | `SOURCE_OF_TRUTH` | `2b9f1abf28f0552f...` |
| `frontend/src/pages/FindingDetailPage.tsx` | **FRONTEND** | Individual finding inspection and re-verification triggers | `SOURCE_OF_TRUTH` | `91dd628c87e33bfc...` |
| `frontend/src/pages/AiAnalysisPage.tsx` | **FRONTEND** | Local AI / Ollama reasoning and 7 RAG functions | `SOURCE_OF_TRUTH` | `772e47f7af5c59ee...` |
| `frontend/src/pages/KnowledgeCorrelationPage.tsx` | **FRONTEND** | CWE and OWASP Top 10 standards correlation graph | `SOURCE_OF_TRUTH` | `8b7cc19616a53ea2...` |
| `frontend/src/pages/EvidenceValidationPage.tsx` | **FRONTEND** | Cryptographic evidence ledger and verification probes | `SOURCE_OF_TRUTH` | `4418acfc928191ba...` |
| `frontend/src/pages/RiskPrioritizationPage.tsx` | **FRONTEND** | Multi-factor risk scoring and prioritization breakdown | `SOURCE_OF_TRUTH` | `6c491ccb68fbe70a...` |
| `frontend/src/pages/RemediationCenterPage.tsx` | **FRONTEND** | Remediation guidance and code patch synthesis | `SOURCE_OF_TRUTH` | `1434720406676a5b...` |
| `frontend/src/pages/SecurityReportPage.tsx` | **FRONTEND** | Executive intelligence report assembly and HTML export | `SOURCE_OF_TRUTH` | `f510d758f7e18b54...` |
| `frontend/src/pages/SystemStatusPage.tsx` | **FRONTEND** | Backend health, Ollama status, and SOC telemetry | `SOURCE_OF_TRUTH` | `81b7a7a3eff2a561...` |
| `frontend/src/pages/UrlSecurityCheckPage.tsx` | **FRONTEND** | Live domain threat check and HTTP header inspection | `SOURCE_OF_TRUTH` | `1f6aabc536d1b1a9...` |
| `frontend/src/pages/PortableAssessmentPage.tsx` | **FRONTEND** | Windows local security posture and scanner permissions | `SOURCE_OF_TRUTH` | `3c9bdd7859d77556...` |
| `frontend/src/pages/ExperienceDbPage.tsx` | **FRONTEND** | Experience DB, false-positive memory, and resolution history | `SOURCE_OF_TRUTH` | `82c5e3479ddf3e2c...` |
| `frontend/src/pages/AuditTrailPage.tsx` | **FRONTEND** | Cryptographic immutable audit event log viewer | `SOURCE_OF_TRUTH` | `f36c4488f73e0ea1...` |
| `frontend/src/pages/AssessmentHistoryPage.tsx` | **FRONTEND** | Historical assessment archive and past report retrieval | `SOURCE_OF_TRUTH` | `417a152d8dcdc89c...` |
| `frontend/src/pages/SettingsPage.tsx` | **FRONTEND** | System configuration and parameter controls | `SOURCE_OF_TRUTH` | `f7bc2ddbc5e2082a...` |
| `frontend/src/pages/GuidePage.tsx` | **FRONTEND** | Operating manual, architecture blueprints, and user guides | `SOURCE_OF_TRUTH` | `ef800d49ac5a67e7...` |
| `frontend/src/pages/TeamDeskPage.tsx` | **FRONTEND** | Analyst task assignment and collaborative triage desk | `SOURCE_OF_TRUTH` | `ac41d0aa4ae1dad1...` |
| `frontend/src/pages/TestCenterPage.tsx` | **FRONTEND** | Automated platform test runner and regression verification | `SOURCE_OF_TRUTH` | `b639979d9b655574...` |
| `backend/requirements.txt` | **BACKEND** | Python backend package requirements | `SOURCE_OF_TRUTH` | `f1cab405df8bc8b1...` |
| `backend/app/main.py` | **BACKEND** | FastAPI main application entry, CORS, lifespan, exception handlers | `SOURCE_OF_TRUTH` | `1350364f4135772d...` |
| `backend/app/api/api.py` | **BACKEND** | Master API router aggregating all 18 route modules | `SOURCE_OF_TRUTH` | `4067ba347bfe9899...` |
| `backend/app/api/routes/system.py` | **BACKEND** | System health, Ollama health, and audit query endpoints | `SOURCE_OF_TRUTH` | `f9e90e8567fec965...` |
| `backend/app/api/routes/assessments.py` | **BACKEND** | Assessment lifecycle creation and stage progression APIs | `SOURCE_OF_TRUTH` | `fd4105b8d49b7968...` |
| `backend/app/api/routes/discovery.py` | **BACKEND** | Attack surface discovery retrieval endpoints | `SOURCE_OF_TRUTH` | `46a6c43471b51108...` |
| `backend/app/api/routes/findings.py` | **BACKEND** | Finding query and status transition endpoints | `SOURCE_OF_TRUTH` | `5283b3f801b16573...` |
| `backend/app/api/routes/evidence.py` | **BACKEND** | Evidence persistence, querying, and verification endpoints | `SOURCE_OF_TRUTH` | `8d6b339a2a3e67cc...` |
| `backend/app/api/routes/risk.py` | **BACKEND** | Risk calculation and prioritization endpoints | `SOURCE_OF_TRUTH` | `be131ee72f6c6d7b...` |
| `backend/app/api/routes/remediation.py` | **BACKEND** | Remediation plan and retest verification endpoints | `SOURCE_OF_TRUTH` | `32cacaf86f182c81...` |
| `backend/app/api/routes/reports.py` | **BACKEND** | JSON and standalone printable HTML report endpoints | `SOURCE_OF_TRUTH` | `9ead9032ee155ef6...` |
| `backend/app/api/routes/ai.py` | **BACKEND** | Ollama LLM hypothesis and explanation endpoints | `SOURCE_OF_TRUTH` | `661596ea0250531c...` |
| `backend/app/api/routes/rag.py` | **BACKEND** | RAG vector store search and indexing endpoints | `SOURCE_OF_TRUTH` | `1edb592800379372...` |
| `backend/app/api/routes/knowledge.py` | **BACKEND** | CWE/OWASP knowledge correlation endpoints | `SOURCE_OF_TRUTH` | `a9711dd6a5faaff4...` |
| `backend/app/api/routes/url_check.py` | **BACKEND** | Target domain header and SSL scan endpoints | `SOURCE_OF_TRUTH` | `0d53b360f64425be...` |
| `backend/app/api/routes/world_monitor.py` | **BACKEND** | Specialized World Monitor assessment endpoints | `SOURCE_OF_TRUTH` | `f388abecdff9527c...` |
| `backend/app/api/routes/portable.py` | **BACKEND** | Windows local host scan permission and scan endpoints | `SOURCE_OF_TRUTH` | `4ba39e1a8424c33e...` |
| `backend/app/api/routes/experience.py` | **BACKEND** | Experience DB metrics and false-positive recording endpoints | `SOURCE_OF_TRUTH` | `8c395bad335e1b60...` |
| `backend/app/api/routes/team.py` | **BACKEND** | Team desk assignment and triage endpoints | `SOURCE_OF_TRUTH` | `51807d23bc5f7b99...` |
| `backend/app/api/routes/test_center.py` | **BACKEND** | Platform test suites execution endpoints | `SOURCE_OF_TRUTH` | `872af8f88cec048b...` |
| `backend/app/api/routes/forensic.py` | **BACKEND** | Immutable forensic package generation endpoints | `SOURCE_OF_TRUTH` | `5a64153e20309ba4...` |
| `backend/app/core/config.py` | **BACKEND** | Pydantic system settings and environment variables | `SOURCE_OF_TRUTH` | `655a4880bf632d79...` |
| `backend/app/core/audit.py` | **BACKEND** | Structured audit logging function | `SOURCE_OF_TRUTH` | `f3b3db52616bd268...` |
| `backend/app/core/time.py` | **BACKEND** | Standardized IST timestamp formatters | `SOURCE_OF_TRUTH` | `76728bcf78ca55a1...` |
| `backend/app/core/target_config.py` | **BACKEND** | Centralized target definition for World Monitor | `SOURCE_OF_TRUTH` | `6a5ec70594b3ebc6...` |
| `backend/app/services/assessment_service.py` | **BACKEND** | Assessment orchestration and 8-stage advance logic | `SOURCE_OF_TRUTH` | `96485861a0978916...` |
| `backend/app/services/security_module_runner.py` | **BACKEND** | Automated non-destructive probe runner for ASSESS stage | `SOURCE_OF_TRUTH` | `6682b7b7d9cc3f7a...` |
| `backend/app/services/world_monitor_assessment_engine.py` | **BACKEND** | World Monitor live runtime and static audit engine | `SOURCE_OF_TRUTH` | `f1a5afe37288157c...` |
| `backend/app/services/world_monitor_service.py` | **BACKEND** | World Monitor target preflight and inventory service | `SOURCE_OF_TRUTH` | `bdf2d8baff3f9c55...` |
| `backend/app/services/ai_analysis_service.py` | **BACKEND** | AI analysis orchestration and structured explanations | `SOURCE_OF_TRUTH` | `9a563989db49d8fe...` |
| `backend/app/services/ai_provider.py` | **BACKEND** | Ollama LLM provider interface and prompt dispatching | `SOURCE_OF_TRUTH` | `73ae10460b2e336f...` |
| `backend/app/services/ollama_service.py` | **BACKEND** | Ollama health check and process supervisor | `SOURCE_OF_TRUTH` | `c704b82f81968280...` |
| `backend/app/services/discovery_service.py` | **BACKEND** | Asset cataloging and attack surface inventory service | `SOURCE_OF_TRUTH` | `8944f637d1e25cf2...` |
| `backend/app/services/evidence_service.py` | **BACKEND** | Evidence persistence and SHA-256 calculation service | `SOURCE_OF_TRUTH` | `e36774cb5e499225...` |
| `backend/app/services/knowledge_service.py` | **BACKEND** | CWE/OWASP taxonomic mapping service | `SOURCE_OF_TRUTH` | `5661ef7ff13241f6...` |
| `backend/app/services/risk_service.py` | **BACKEND** | Deterministic multi-factor risk scoring engine | `SOURCE_OF_TRUTH` | `1ae6b5e90a332b6a...` |
| `backend/app/services/remediation_service.py` | **BACKEND** | Remediation synthesis and verification method generator | `SOURCE_OF_TRUTH` | `1c4309994fe98c9b...` |
| `backend/app/services/report_service.py` | **BACKEND** | Report data compilation and HTML renderer | `SOURCE_OF_TRUTH` | `ba93d880e440d53e...` |
| `backend/app/services/url_scanner_service.py` | **BACKEND** | Standalone URL security check and header auditor | `SOURCE_OF_TRUTH` | `0a8d0a4b50011ab1...` |
| `backend/app/services/validation_service.py` | **BACKEND** | Evidence validation probe executor | `SOURCE_OF_TRUTH` | `87d6e2018244a5aa...` |
| `backend/app/services/forensic_export_service.py` | **BACKEND** | Forensic dossier archive builder | `SOURCE_OF_TRUTH` | `93f938ff3332ad39...` |
| `backend/app/services/health_service.py` | **BACKEND** | Component health aggregator | `SOURCE_OF_TRUTH` | `1b9b56fe9bfe5517...` |
| `backend/app/rag/rag_pipeline.py` | **BACKEND** | RAG query pipeline and prompt augmentation | `SOURCE_OF_TRUTH` | `24ce49dbbbd68771...` |
| `backend/app/rag/document_loader.py` | **BACKEND** | CWE and OWASP document ingestion | `SOURCE_OF_TRUTH` | `cba63a701b13480b...` |
| `backend/app/rag/chunker.py` | **BACKEND** | Document chunking and metadata preservation | `SOURCE_OF_TRUTH` | `bf603e6ac98370f3...` |
| `backend/app/rag/embeddings.py` | **BACKEND** | Local vector embedding generator | `SOURCE_OF_TRUTH` | `99f336101cfc63d2...` |
| `backend/app/rag/vector_store.py` | **BACKEND** | In-memory vector store and cosine similarity index | `SOURCE_OF_TRUTH` | `b513dc1d951d48f1...` |
| `backend/app/rag/models.py` | **BACKEND** | Data models for RAG chunks and queries | `SOURCE_OF_TRUTH` | `c469f6ec593f62df...` |
| `backend/app/scanners/permissions_manager.py` | **BACKEND** | Local scan consent and permissions dashboard | `SOURCE_OF_TRUTH` | `5cf246c887e07852...` |
| `backend/app/scanners/file_scanner.py` | **BACKEND** | Local filesystem and secret leakage auditor | `SOURCE_OF_TRUTH` | `d89e1513b0448dc4...` |
| `backend/app/scanners/process_scanner.py` | **BACKEND** | Running process security inspector | `SOURCE_OF_TRUTH` | `8c66ea4f1b2414dd...` |
| `backend/app/scanners/software_scanner.py` | **BACKEND** | Installed software and version inventory | `SOURCE_OF_TRUTH` | `1a54a674345c5cd2...` |
| `backend/app/scanners/startup_scanner.py` | **BACKEND** | Startup entry and persistence auditor | `SOURCE_OF_TRUTH` | `d7554705eeb20d77...` |
| `backend/app/scanners/network_scanner.py` | **BACKEND** | Active network connections and listening port scanner | `SOURCE_OF_TRUTH` | `490b1ae25ed28cc2...` |
| `backend/app/scanners/system_security_scanner.py` | **BACKEND** | Windows Defender, firewall, UAC security checks | `SOURCE_OF_TRUTH` | `bda3da109913a3f2...` |
| `core/assessment_engine.py` | **BACKEND** | Core multi-domain security evaluation engine | `SOURCE_OF_TRUTH` | `f59f68cdfe1fad6b...` |
| `core/risk_engine.py` | **BACKEND** | CVSS v3.1 calculator and severity mapper | `SOURCE_OF_TRUTH` | `299c41fa06232d27...` |
| `services/storage_service.py` | **BACKEND** | Dual SQLite raw query persistence layer | `SOURCE_OF_TRUTH` | `0029dcdf4647e972...` |
| `backend/app/core/database.py` | **DATABASE** | SQLAlchemy engine, session factory, and schema migrations | `SOURCE_OF_TRUTH` | `1d93fb42398448cb...` |
| `backend/app/models/models.py` | **DATABASE** | SQLAlchemy ORM models: Assessment, Finding, EvidenceRecord, AuditEvent | `SOURCE_OF_TRUTH` | `04c64972c84e81f2...` |
| `backend/app/schemas/schemas.py` | **DATABASE** | Pydantic request and response schemas | `SOURCE_OF_TRUTH` | `108921d78aba1a52...` |
| `backend/app/data/seed_data.py` | **DATABASE** | Seed demo dataset and synthetic baseline definitions | `SOURCE_OF_TRUTH` | `0915d974f01046b6...` |
| `backend/tests/test_audit_matrix.py` | **TESTS** | Comprehensive 9-point end-to-end acceptance audit suite | `SOURCE_OF_TRUTH` | `e1de6910cce96983...` |
| `backend/tests/test_data_isolation.py` | **TESTS** | Multi-assessment data isolation and demo contamination suite | `SOURCE_OF_TRUTH` | `85fb3d94b9bd7cb9...` |
| `backend/tests/test_mandatory_modules.py` | **TESTS** | Team desk, experience DB, and test center verification suite | `SOURCE_OF_TRUTH` | `66b78cb2168d5b87...` |
| `backend/tests/test_portable_scanners.py` | **TESTS** | Windows portable security scanners and permissions suite | `SOURCE_OF_TRUTH` | `9fc9e3c76ef40ab0...` |
| `backend/tests/test_rag.py` | **TESTS** | RAG vector store, similarity ranking, and query grounding suite | `SOURCE_OF_TRUTH` | `e94a46b604f6f609...` |
| `backend/tests/test_priority6_forensics.py` | **TESTS** | 14 lifecycle audit actions and cryptographic hash chaining suite | `SOURCE_OF_TRUTH` | `e0b195f1150b3132...` |
| `backend/tests/test_priority7_ollama_analyst.py` | **TESTS** | Ollama LLM reasoning, fallback, and masking suite | `SOURCE_OF_TRUTH` | `ca1be0d336fe2ec8...` |
| `backend/tests/test_enterprise_full_demonstration.py` | **TESTS** | Complete 17-step SIH demonstration workflow suite | `SOURCE_OF_TRUTH` | `66229af5109fc05a...` |
| `backend/tests/test_three_real_detections.py` | **TESTS** | End-to-end empirical detection verification suite | `SOURCE_OF_TRUTH` | `ab3227a9965339cb...` |
| `backend/tests/test_web_desktop_parity.py` | **TESTS** | Shared database parity between Web and Desktop clients | `SOURCE_OF_TRUTH` | `b2915d0bb3495a50...` |
| `backend/tests/test_world_monitor_real_target.py` | **TESTS** | Empirical World Monitor target assessment tests | `SOURCE_OF_TRUTH` | `2a804af8fa32b6ef...` |
| `backend/tests/test_retest_workflow.py` | **TESTS** | Remediation re-verification and state-diffing suite | `SOURCE_OF_TRUTH` | `0480b8d743033e1e...` |
| `backend/tests/test_api.py` | **TESTS** | FastAPI core endpoints functional verification | `SOURCE_OF_TRUTH` | `863379df6b33200d...` |
| `test_scanner_suite.py` | **TESTS** | Root scanner integration test runner | `SOURCE_OF_TRUTH` | `8172ae73e9f3af41...` |
| `.env.example` | **CONFIG** | Safe template of system configuration and environment variables | `SOURCE_OF_TRUTH` | `37b474f4d85764e2...` |
| `requirements.txt` | **CONFIG** | Project root Python dependency manifest | `SOURCE_OF_TRUTH` | `9ce214ea783fe856...` |
| `START KAVACH 1.0 .bat` | **CONFIG** | Windows one-click launcher for frontend and backend | `SOURCE_OF_TRUTH` | `17e0ffa8eed2cdfc...` |
| `START KAVACH 2.0 .bat` | **CONFIG** | Alternative launcher with environment checks | `SOURCE_OF_TRUTH` | `ec6f6320789ac517...` |
| `TEST_KAVACH.bat` | **CONFIG** | Windows test suite runner batch script | `SOURCE_OF_TRUTH` | `6c8e7d4cf16b62fc...` |
| `KAVACH.spec` | **CONFIG** | PyInstaller specification for standalone binary bundling | `SOURCE_OF_TRUTH` | `3777379098aeb2e5...` |
| `README.md` | **DOCUMENTATION** | Repository overview and quickstart guide | `CONTEXTUAL` | `a1bf4b0511cd5031...` |
| `START_KAVACH_GUIDE.md` | **DOCUMENTATION** | Step-by-step startup guide and operating instructions | `CONTEXTUAL` | `d807cd37f3bdca4b...` |
| `KAVACH_5_VALIDATION_REPORT.md` | **DOCUMENTATION** | Historical SIH validation report | `CONTEXTUAL` | `bbe1f628b8291fea...` |
| `DEBUG_BASELINE.md` | **DOCUMENTATION** | Telemetry and baseline debugging documentation | `CONTEXTUAL` | `99ebb8c04b22b02f...` |
| `CLEANUP_CHANGELOG.md` | **DOCUMENTATION** | Changelog of repository cleanup and hardening | `CONTEXTUAL` | `222d26dec57f0902...` |
| `walkthrough.md` | **DOCUMENTATION** | Audit walkthrough and technical verification dossier | `CONTEXTUAL` | `699dee4a488493ef...` |

---

## 2. Excluded Directories & High-Volume Exclusions
The following directories are deliberately excluded from this documentation package to ensure reproducibility, avoid bloat, and prevent credential exposure:

| Directory Pattern | Reason for Exclusion |
| :--- | :--- |
| `node_modules/` | Third-party Node.js package dependencies (high-volume, generated) |
| `.venv/ & venv/` | Python virtual environment binaries and site-packages (generated) |
| `__pycache__/ & *.pyc` | Compiled Python bytecode files (generated) |
| `dist/ & build/` | Compiled frontend bundles and PyInstaller build artifacts (generated) |
| `.git/ & .github/` | Git version control internal database and logs |
| `.pytest_cache/` | Pytest execution and session cache artifacts (generated) |
| `logs/` | Runtime server execution logs and task output logs |
| `docs/user_manual/demos/*.mp4` | Large binary video screen recordings (excluded to prevent bloat) |
| `kavach.db` | Live SQLite database file containing runtime instance data (binary) |
| `.env` | Live local environment file containing runtime configuration (protects secrets) |
