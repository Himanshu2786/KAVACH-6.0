# KAVACH 6.0 — Evidence Engine & Cryptographic Proof Specification

KAVACH Version: 5.0  
Documentation Status: CURRENT  
Last Updated: 2026-09-23  
Source of Truth: Current repository implementation (`backend/app/services/evidence_service.py`, `backend/app/services/validation_service.py`, `backend/app/services/reverification_service.py`, `backend/app/db/models.py`)

---

## 1. Overview & Core Philosophy

### Simple Explanation
In a court of law, a prosecutor cannot just say "the suspect is guilty" without presenting fingerprint or video evidence. Similarly, KAVACH never marks a security vulnerability as "confirmed" just because a scanner flagged it or an AI guessed it. KAVACH executes safe, non-destructive network probes, records the exact server response (like the exact HTTP headers and data returned), freezes it with a tamper-proof cryptographic fingerprint (SHA-256), and saves it as immutable evidence.

### Technical Explanation
The Evidence Engine is KAVACH's foundational integrity pillar. Findings in KAVACH strictly adhere to an evidence-grounded state machine:
$$\textbf{Raw Network Probe} \longrightarrow \textbf{Cryptographic Hashing (SHA-256)} \longrightarrow \textbf{Evidence Record Creation} \longrightarrow \textbf{Finding Confirmation}$$

No finding can transition to `CONFIRMED` without an associated, cryptographically sealed `EvidenceRecord` possessing:
1. `validation_result = "CONFIRMED"`
2. A populated `raw_data` protocol transcript.
3. An immutable `integrity_hash`.
4. A deterministic reproduction command.

---

## 2. Complete Evidence Lifecycle

The lifecycle of evidence follows a strict unidirectional progression across assessment and remediation phases:

```
[ BASELINE EVIDENCE ]
       │ (Initial scan probe captures server response)
       ▼
[ CANONICAL PROOF ]  ◀── (Identified as primary active empirical evidence)
       │
       ├─► [ HISTORICAL ARTIFACTS ] (Retained in DB & audit trail; excluded from active counts)
       ▼
[ REMEDIATION PATCH APPLIED ]
       ▼
[ RETEST EVIDENCE ]  (Re-verification probe captures post-patch state)
       ▼
[ STATE COMPARISON ] (Side-by-side diff: Before vs. After)
       ▼
  ┌────┴──────────────┐
  ▼                   ▼
[ RESOLVED ]      [ STILL_OPEN ]
```

### Clarification of Semantics: CONFIRMED vs. STILL_OPEN
A critical point of confusion in legacy scanners is conflating confirmation with remediation status. KAVACH enforces clear semantic separation:
- **`CONFIRMED` (Confirmation State):** The initial or canonical technical evidence proved that the vulnerability existed on the target.
- **`STILL_OPEN` (Remediation Lifecycle State):** A subsequent post-remediation re-test was executed, but the endpoint still exhibited the vulnerable behavior (e.g., HTTP 200 with OpenAPI schema), proving that the flaw has not yet been resolved.
- **Rule:** A finding marked `STILL_OPEN` remains **`CONFIRMED`** in its historical evidence proof. It is never downgraded to "unconfirmed" or "unverified".

---

## 3. Evidence Deduplication & Aggregation Rules

### The Problem
During comprehensive scanning, multiple probes may inspect the same endpoint (e.g., an initial HEAD probe followed by a detailed GET body probe). Creating multiple evidence records for one underlying flaw can artificially inflate executive metrics, making 1 finding appear as 2 or more confirmed vulnerabilities.

### The KAVACH Deduplication Rule
1. **Database & Audit Preservation:** All captured artifacts remain permanently stored in the database (`evidence_records` table) and logged in the immutable audit trail.
2. **Canonical Proof Identification:** The most accurate, specific, and active probe is designated as the **Canonical Proof**.
   - For `WM-API-DOCS-A018`:
     - Historical baseline artifact: `EV-WM-API-DOCS-A018` (original probe artifact)
     - Canonical active proof: `EV-WM-API-DOCS-A018-GET` (GET-based empirical validation proving OpenAPI 3.1 schema)
3. **Executive Metric Aggregation:** Executive dashboards, summary scorecards, and high-level reports count **UNIQUE ACTIVE PROOFS** (1 unique proof per confirmed finding).
4. **Technical Detail View:** Technical tabs, audit event viewers, and forensic JSON exports display all artifacts, clearly designating canonical versus historical items.

| Finding ID | Artifacts Stored | Canonical Proof | Executive Evidence Count | Technical Detail Count |
| :--- | :--- | :--- | :--- | :--- |
| `WM-API-DOCS-A018` | 2 baseline (`EV-WM-API-DOCS-A018`, `EV-WM-API-DOCS-A018-GET`) + 5 re-test (`EVD-AFT-*`) | `EV-WM-API-DOCS-A018-GET` | **1 Unique Confirmed Proof** | 7 Total Artifacts |

---

## 4. Cryptographic Integrity Hashing

Every evidence record generates an immutable SHA-256 cryptographic hash over its core technical tuple:
$$\text{Integrity Hash} = \text{SHA-256}(\text{evidence\_type} \parallel \text{timestamp} \parallel \text{raw\_data})$$

```python
# Implemented in backend/app/services/evidence_service.py
payload = f"{evidence_type}:{timestamp}:{raw_data}".encode("utf-8")
integrity_hash = hashlib.sha256(payload).hexdigest()
```

This prevents post-scan tampering or evidence fabrication. If any byte in `raw_data` is modified, the hash verification fails.

---

## 5. Dual-Layer Evidence Presentation

### A. Simple Evidence View (Executive / PM / Junior Dev)
- **What Was Found:** Clear plain-English summary (e.g., *"The target web application publicly exposes its complete interactive OpenAPI documentation without requiring authentication"*).
- **Why It Matters:** Explains reconnaissance risks (attackers can map all endpoints, input parameters, and schemas).
- **Where It Was Found:** Exact URI: `https://www.worldmonitor.app/openapi.json`.
- **Confidence Rating:** `HIGH` (Direct empirical protocol observation).

### B. Technical Evidence View (Security Engineer / Auditor)
- **Protocol Transcript:** Complete HTTP status line, response headers, and JSON body sample.
  ```http
  HTTP/1.1 200 OK
  date: Wed, 23 Sep 2026 12:45:00 GMT
  content-type: application/json; charset=utf-8
  cache-control: public, max-age=3600
  
  {"openapi":"3.1.0","info":{"title":"WorldMonitor API","version":"1.0.0"},"paths":{...}}
  ```
- **Probe Command:** Exact safe GET command:
  ```bash
  curl -i -s -X GET "https://www.worldmonitor.app/openapi.json"
  ```
- **Cryptographic Hash:** SHA-256 digest displayed with copy action.
- **Schema Validation:** Explicitly records OpenAPI version `3.1.0` and API title `WorldMonitor API`.

---

## 6. Re-Verification & Evidence Comparison

When re-running a check (`reverification_service.py`):
1. The exact same HTTP probe is dispatched against the endpoint.
2. A new `ReVerificationRecord` is created with its own timestamp, response transcript, and hash.
3. KAVACH executes a structured comparison:
   - **Before:** Status `HTTP 200 OK`, body contains `{"openapi":"3.1.0"}`.
   - **After:** If status is `HTTP 401 Unauthorized` or `HTTP 404 Not Found` $\rightarrow$ transitions to `RESOLVED`.
   - **After (Current A018 State):** Status remains `HTTP 200 OK`, schema remains exposed $\rightarrow$ transitions to `STILL_OPEN`.
4. Audit trail records `RETEST_STARTED`, `RETEST_OBSERVATION_CAPTURED`, `RETEST_EVIDENCE_CREATED`, `RETEST_STATE_COMPARISON`, and `RETEST_UNRESOLVED`.

---

## 7. Verification Status Matrix

| Component | Status | Empirical Reference |
| :--- | :--- | :--- |
| **Evidence Capture (Live GET)** | IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR | `EV-WM-API-DOCS-A018-GET` / HTTP 200 / OpenAPI 3.1.0 |
| **SHA-256 Integrity Sealing** | IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR | Generated and verified across all evidence rows |
| **Deduplication Logic** | IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR | 2 baseline artifacts aggregated to 1 unique proof |
| **Re-Test Persistence** | IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR | 5 re-test records persisted across server restarts |
| **Lifecycle State Separation** | IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR | CONFIRMED confirmation state + STILL_OPEN lifecycle |
