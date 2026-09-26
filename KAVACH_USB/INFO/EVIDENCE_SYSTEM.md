# KAVACH — Evidence System Specification

The Evidence System is the primary unique selling proposition (USP) of KAVACH. In accordance with the project's core philosophy, security findings cannot be marked confirmed without verifiable technical evidence.

---

## 1. How Evidence Is Collected
Evidence is gathered through safe, non-destructive network probes executed by the backend prober engine (`validation_service.py`):
- **Live Probes**: When assessing an authorized live target, KAVACH issues targeted HTTP requests (`GET`, `HEAD`, `POST`) using `httpx.AsyncClient` with a strict 5-second timeout.
- **Simulated Probes (Demo Mode)**: For offline demonstrations or test environments, KAVACH executes deterministic mock probes representing authentic server traffic from the target application (World Monitor).
- **Prohibited Actions**: KAVACH never executes denial-of-service attacks, destructive SQL queries (`DROP`, `DELETE`), or remote payload uploads.

---

## 2. How Raw Results Are Stored
The raw, untruncated response from the target server is preserved in the `EvidenceRecord.raw_data` database column:
- HTTP status codes (e.g., `HTTP/1.1 200 OK` or `HTTP/1.1 500 Internal Server Error`).
- Full header sets (e.g., `Server`, `Content-Security-Policy`, `Set-Cookie`).
- Relevant response body snippets (JSON payloads, stack traces, or error strings).
- An immutable SHA-256 cryptographic hash is generated over the composite payload:
  $$\text{Integrity Hash} = \text{SHA-256}(\text{evidence\_type} \parallel \text{timestamp} \parallel \text{raw\_data})$$

---

## 3. How Evidence IDs Are Generated
Evidence IDs are generated using a deterministic prefix and cryptographically random hexadecimal identifiers:
- Format: `EVD-[8-HEX]` (e.g., `EVD-7B2A91F4`).
- Generated at creation time inside `evidence_service.py`.
- Persisted permanently and mapped directly to the parent Finding and Assessment IDs.

---

## 4. How Evidence Is Connected to Findings
The relational schema binds evidence directly to findings via foreign key:
```sql
CREATE TABLE evidence_records (
    id VARCHAR(50) PRIMARY KEY,
    finding_id VARCHAR(50) REFERENCES findings(id) ON DELETE CASCADE,
    evidence_type VARCHAR(100) NOT NULL,
    source VARCHAR(150),
    timestamp VARCHAR(50),
    description TEXT,
    raw_data TEXT,
    validation_result VARCHAR(50),
    integrity_hash VARCHAR(64),
    is_demo BOOLEAN
);
```
When an evidence record is attached, the finding's `evidence_status` automatically transitions from `NONE` to `AVAILABLE` or `VERIFIED`, and the deterministic state evaluator updates the finding's overall status.

---

## 5. How Simple Evidence Is Generated
The Simple Evidence card is written in plain, human-accessible language for executives, project managers, and junior developers:
- **What Was Found**: Clear declaration of what the scan observed (e.g., *"The server responded with tenant B's private API keys when requesting workspace 9921 using tenant A's authentication token"*).
- **Why It Matters**: Business impact, threat actor exploitation scenario, and risk to data confidentiality.
- **Where It Was Found**: Concrete endpoint, parameter, or HTTP header.
- **Confidence Rating**: Categorized as `HIGH`, `MEDIUM`, or `LOW`, based on the directness of the observed proof.

---

## 6. How AI Analysis Is Generated
AI analysis is strictly evidence-driven:
1. The backend passes the structured finding and its linked raw evidence to the AI engine (`ai_analysis_service.py`).
2. The system prompt instructs the model: *"Analyze only the provided evidence. Do not invent vulnerabilities or extrapolate facts not present in the probe response."*
3. The AI returns a structured JSON payload containing a concise summary, testable hypothesis, operational impact, and recommended validation steps.
4. In the UI, AI analysis is **strictly visually segregated** from the raw evidence, ensuring users always know what is empirical fact versus analytical interpretation.

---

## 7. How Technical Evidence Is Generated
For security engineers, penetration testers, and auditors, technical evidence provides exact protocol-level data:
- Protocol version and HTTP status line.
- Complete request/response header maps.
- Body content snippets exhibiting the flaw.
- Cryptographic SHA-256 checksum allowing external validation of evidence tamper-resistance.

---

## 8. How Terminal Verification Works
Every evidence card features a `[ VERIFY TECHNICALLY ]` action that opens the **Technical Terminal Viewer**:
1. **Identical Identifiers**: The terminal view references the exact same `Evidence ID`, `Assessment ID`, and timestamp as the simple card.
2. **Safe Verification Command**: KAVACH provides an executable, non-destructive CLI command (e.g., `curl -i -s -H "Authorization: Bearer test_token" https://target/api/v1/...`).
3. **Expected vs. Observed Results**:
   - *Expected (Secure)*: e.g., `HTTP/1.1 403 Forbidden` or presence of defensive headers.
   - *Observed (Vulnerable)*: e.g., `HTTP/1.1 200 OK` exposing private data or missing headers.
4. **Copy Action**: Engineers can click `[ COPY COMMAND ]` to run the check in their own terminal and observe the identical behavior.

---

## 9. How Remediation Is Created
Remediation guidance provides actionable, prioritized fixes:
- **Step-by-Step Code Changes**: Concrete code snippets (e.g., Python FastAPI dependencies, Nginx configuration directives).
- **Why This Fix Works**: Explains the defensive mechanism (e.g., parameterized queries neutralize SQL token boundaries).
- **How to Verify the Fix**: Outlines the post-patch testing procedure.

---

## 10. How Re-Verification Works
Once an engineering team applies a patch, they click `[ RE-RUN CHECK ]`:
1. The backend executes the identical verification probe against the updated target endpoint.
2. A new `ReVerificationRecord` is created, capturing the post-fix HTTP response and status code.
3. KAVACH performs a side-by-side comparison:
   - **Before Fix**: Status 200 / Missing headers / Stack trace.
   - **After Fix**: Status 403 Forbidden / Headers present / Standard error JSON.
4. Deterministic status assignment:
   - `RESOLVED`: The flaw is no longer observable.
   - `STILL OBSERVED`: The flaw persists unchanged.
   - `IMPROVED`: Partial mitigation detected.
   - `NEEDS REVIEW`: Ambiguous or unexpected response received.

---

## 11. Evidence Limitations
- **Passive vs. Active Scope**: Safe HTTP probes cannot detect deep asynchronous business logic flaws or memory corruption vulnerabilities.
- **WAF / Rate Limiter Interference**: Web Application Firewalls (WAFs) or Cloudflare DDoS protection may return HTTP 403 or 429, which must not be confused with application-level authorization.
- **Network Boundaries**: Private endpoints located behind internal VPNs cannot be validated unless the KAVACH backend has internal network routing.
