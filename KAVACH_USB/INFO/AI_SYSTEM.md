# KAVACH — AI System Specification

## 1. Architectural Philosophy: AI as an Assistant, Not an Oracle

In KAVACH, AI is strictly auxiliary to the security engine. The security engine and safe probes discover objective facts; the AI engine explains, translates, and contextualizes those facts for humans.

$$\textbf{Security Engine Finds Facts} \longrightarrow \textbf{Evidence Proves Facts} \longrightarrow \textbf{AI Explains Facts} \longrightarrow \textbf{User Verifies Facts}$$

### Strict Prohibitions
- AI **must never** invent vulnerabilities.
- AI **must never** generate fake terminal logs or fabricated HTTP responses.
- AI **must never** mark a finding confirmed without supporting technical evidence.
- AI **must never** replace the deterministic security state machine.

---

## 2. Server-Side AI Architecture for Online Users

When KAVACH is hosted publicly (e.g., `https://kavach-security.app`):
1. **Zero Client-Side Burden**: The end user accesses KAVACH solely via their standard web browser (Chrome, Firefox, Safari, Edge) on desktop, laptop, or mobile devices.
2. **No Local Tool Installation**: Online users are **never** required to:
   - Install Python or virtual environments.
   - Run local `.bat` or `.sh` startup scripts.
   - Install Ollama or download multi-gigabyte GGUF models.
   - Run a local model server.
3. **Backend-Mediated AI Pipeline**:
   ```
   [User Web Browser] 
          |
          | HTTP POST /api/findings/{id}/analyze
          v
   [KAVACH FastAPI Backend]
          |
          | Checks AI Provider
          +---> [Server-Side Ollama Instance / Hosted LLM API]
          |           |
          |     (If Unreachable or Slow)
          v           v
   [Deterministic Rule-Based Security Intelligence Engine]
          |
          | Returns Normalized JSON Payload
          v
   [Clean Structured UI Presentation with Strict Visual Separation]
   ```

---

## 3. Strict Visual Separation of Facts vs. AI Analysis

To prevent ambiguity, KAVACH enforces a rigid visual separation between objective empirical evidence and AI interpretations:

```
+-------------------------------------------------------------------------+
| [FACT FROM EVIDENCE]                                                    |
| The HTTP GET response returned status 200 OK with sensitive API keys.   |
+-------------------------------------------------------------------------+
| [AI-ASSISTED ANALYSIS]                                                  |
| This indicates a potential Insecure Direct Object Reference (IDOR)      |
| allowing horizontal tenant traversal.                                   |
+-------------------------------------------------------------------------+
| [RECOMMENDED ACTION]                                                    |
| Enforce server-side tenancy binding in query: .filter(owner_id == user)  |
+-------------------------------------------------------------------------+
```

---

## 4. Graceful Degradation (Zero Single Point of Failure)

If the server-side Ollama model is offline, overloaded, or times out:
1. The backend automatically switches to the **Rule-Based Security Intelligence Engine**.
2. The UI clearly displays an indicator: `Analysis Mode: Rule-Based Fallback Engine`.
3. Finding evidence, technical verification procedures, terminal commands, and remediation steps continue to display seamlessly.
4. The platform **never crashes or freezes** due to AI unavailability.
