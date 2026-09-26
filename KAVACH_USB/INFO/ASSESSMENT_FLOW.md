# KAVACH — Assessment Flow & Workflow Specification

The KAVACH user experience is modeled after modern, high-trust security intelligence platforms, balancing simple inputs with rigorous technical validation.

---

## 1. The 9-Step Assessment Workflow

```
① ENTER TARGET
      │  (User inputs URL on Landing Page hero)
      ▼
② CONFIRM AUTHORIZATION
      │  (Scope confirmation modal verifies authorization)
      ▼
③ RUN SECURITY ASSESSMENT
      │  (Asynchronous job launched across 7 SIH categories)
      ▼
④ REVIEW FINDINGS
      │  (Prioritized findings displayed with clear status)
      ▼
⑤ VIEW EVIDENCE
      │  (Simple & technical evidence cards with SHA-256 hash)
      ▼
⑥ VERIFY EVIDENCE
      │  (User executes safe curl command in Technical Terminal)
      ▼
⑦ FIX ISSUE
      │  (Engineering team implements recommended code patch)
      ▼
⑧ RE-VERIFY
      │  (Re-run check compares Before Fix vs. After Fix)
      ▼
⑨ GENERATE REPORT
         (Export audit-ready executive & technical compliance report)
```

---

## 2. Detailed Step-by-Step Breakdown

### Step 1: Target Ingestion
- User enters target URL (e.g., `https://www.worldmonitor.app`) into the prominent landing page input box.
- URL validation checks format, schema (`http://` or `https://`), and network accessibility.

### Step 2: Legal Authorization Gatekeeper
- Before any active probe is dispatched, the **Authorization Modal** appears:
  - Checkbox 1: *"I own this application OR I have explicit authorization to assess this target."*
  - Checkbox 2: *"I understand that KAVACH must only be used on authorized systems."*
- Bypassing or declining authorization aborts the scan immediately.

### Step 3: Asynchronous Assessment Dispatch
- The backend creates an `Assessment` record with status `QUEUED` and returns an assessment identifier (`ASM-XXXX`).
- The frontend initiates lightweight polling against `/api/assessments/{id}/progress`.
- Modules execute sequentially across the 7 SIH categories:
  1. Authentication
  2. Authorization & Access Control
  3. Input Validation & Data Handling
  4. API Security
  5. Client-Side Security
  6. Secure Communication
  7. Data Storage & Privacy

### Step 4: Findings Presentation
- Findings are rendered with explicit, non-sensationalist statuses:
  - `POTENTIAL`: Initial hypothesis identified during discovery.
  - `EVIDENCE AVAILABLE`: Raw probe data collected.
  - `CONFIRMED`: Technical proof verified.
  - `UNCONFIRMED`: Defensive mechanisms successfully repelled the probe.
  - `REQUIRES MANUAL REVIEW`: Inconclusive output requiring human judgment.

### Step 5 & 6: Simple & Technical Verification
- The user reviews what was found, why it matters, and where it was found.
- The user clicks `[ VERIFY TECHNICALLY ]` to view the safe verification procedure with the identical `Evidence ID`.
- The user executes the provided command to confirm findings independently.

### Step 7 & 8: Remediation & Re-Verification
- Engineering implements the fix based on the remediation playbook.
- Clicking `[ RE-RUN CHECK ]` executes the post-patch probe.
- Results are compared side-by-side: Before vs. After.
- Status updates deterministically to `RESOLVED` or `STILL OBSERVED`.

### Step 9: Report Generation
- Comprehensive audit report generated with executive summary, methodology, findings table, raw evidence, SHA-256 integrity hashes, and re-verification diffs.
