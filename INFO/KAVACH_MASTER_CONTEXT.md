# KAVACH 6.0 — Master Architecture & System Context

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation  
> **System Name:** KAVACH 6.0 (Sovereign Security & Cyber Intelligence Platform)  
> **Problem Statement:** Smart India Hackathon (SIH) 2026 — PS 26163  
> **Platform Tagline:** *"AI Hypothesizes. Evidence Confirms."*  

---

## 1. Core Platform Architecture

```
                                  ┌────────────────────────────────────────┐
                                  │            KAVACH 6.0 CORE             │
                                  └───────────────────┬────────────────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │   WEB APPLICATION   │
                                           │  (React 19 + Vite)  │
                                           └──────────┬──────────┘
                                                      │
                                                      │ HTTP / JSON REST API
                                                      ▼
       ┌─────────────────────────────────────────────────────────────────────────────────────────┐
       │                           KAVACH SOVEREIGN BACKEND & SERVICES                           │
       │  ├── 8-Stage Assessment Orchestrator (DISCOVER -> ASSESS -> ... -> REPORT)              │
       │  ├── Dedicated World Monitor Engine (Live HTTP GET Runtime Probes & Re-Test Engine)     │
       │  ├── Evidence Engine (SHA-256 Hashing, Canonical vs Historical, Deduplication)          │
       │  ├── Risk Engine (Deterministic Mathematical CVSS Prioritization: 5.92 / 10.0)          │
       │  ├── Knowledge Engine (CWE-200 / OWASP A05:2021 Security Misconfiguration)              │
       │  ├── Ollama AI Evidence Analyst & Lexical RAG Fallback Grounding                        │
       │  ├── Audit Trail Ledger (Persistent Chronological Event History & Scoping)              │
       │  └── Forensic Export Service (Machine-Readable JSON Packages & Standalone HTML Reports) │
       └───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                   │
                                                   ▼
                                  ┌──────────────────────────────────┐
                                  │       SHARED SQLite DATABASE     │
                                  │       (kavach.db - WAL Mode)     │
                                  └──────────────────────────────────┘
```

---

## 2. Verified Active Baseline Context

- **Active Assessment**: `KAVACH-WM-20260923-A018`
- **Target URL**: `https://www.worldmonitor.app`
- **Mode**: `HYBRID` (Live HTTP probe + local repository source guard)
- **Status**: `COMPLETED`, current stage `REPORT`, progress `100%`
- **Verified Finding**: `WM-API-DOCS-A018` (*Publicly Exposed Interactive API Schema & Documentation*)
- **Evidence Proof**: `EV-WM-API-DOCS-A018-GET` (HTTP 200 OK, `application/json`, OpenAPI 3.1.0, unauthenticated public access)
- **Deterministic Priority Score**: `5.92 / 10.0` (Medium Priority)
- **Current Lifecycle State**: `CONFIRMED` technical verification, `STILL_OPEN` remediation state after live re-testing.
- **Evidence Deduplication**: 2 baseline artifacts resolve to 1 unique verified proof in executive summaries.
- **External Correlations**: 0 (`NO DIRECT LOCAL MATCH`), 1 local finding in World Situational Monitor.
- **Audit Records**: 72 events total, 25 re-test events preserved in global audit trail, stage execution logs strictly scoped.

---

## 3. Core Architectural Tenets

1. **Evidence First**: Zero ungrounded assertions. A finding cannot be marked `CONFIRMED` without an associated `EvidenceRecord` containing raw technical proof and a cryptographic SHA-256 digest.
2. **Deterministic Risk Mathematics**: Risk priority is calculated by an algebraic formula (`5.92 / 10.0`), not by stochastic LLM guessing.
3. **Bounded AI Explanations**: Local Ollama LLM (`phi3`) provides technical explanations and remediation steps strictly bounded by empirical evidence.
4. **Data Isolation**: Assessments, findings, and evidence are strictly partitioned by `assessment_id`. Real assessments never ingest demo records.
5. **Safe & Non-Destructive**: Read-only inspection; zero destructive payload execution.
