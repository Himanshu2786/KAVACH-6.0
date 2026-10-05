# KAVACH — Website Architecture Specification

## 1. High-Level Architectural Flow

```
+-------------------------------------------------------------------------+
|                              USER BROWSER                               |
|                (Desktop / Tablet / Mobile - No Setup Required)          |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTPS / WSS
                                    v
+-------------------------------------------------------------------------+
|                           KAVACH FRONTEND                               |
|      (React 18 + Vite SPA, Tailwind CSS v4, Glassmorphic Cyber-UI)      |
|                                                                         |
|  - Landing Page (Hero, 9-Step Flow, Instant URL Scanner CTA)            |
|  - Legal Authorization Modal Gatekeeper                                 |
|  - Simple Evidence Cards + Interactive Technical Terminal Viewers       |
|  - Re-Verification Modals (Before vs. After Comparison)                 |
+-------------------------------------------------------------------------+
                                    |
                                    | REST API Calls (Axios)
                                    v
+-------------------------------------------------------------------------+
|                            BACKEND API                                  |
|                 (FastAPI Asynchronous Engine on Port 8000)              |
|                                                                         |
|  - Input Validation & Target Normalization                              |
|  - Deterministic Finding State Machine                                  |
|  - Non-Destructive Probe Orchestrator                                   |
|  - Cryptographic SHA-256 Evidence Hasher                               |
|  - Server-Side AI Provider Adapter (Ollama + Rule-Based Intelligence)   |
|  - Re-Verification & Diff Engine                                        |
+-------------------------------------------------------------------------+
             |                              |                        |
             v                              v                        v
+-------------------------+    +-----------------------+    +------------------+
|   RELATIONAL DATABASE   |    |    EVIDENCE ENGINE    |    |  SERVER-SIDE AI  |
|     (SQLite / PG)       |    | (Raw Httpx Probes &   |    | (Hosted Ollama / |
|                         |    |  SHA-256 Hashes)      |    |  Fallback Rule   |
| - Assessments           |    |                       |    |  Security Engine)|
| - Findings & Evidence   |    |                       |    +------------------+
| - Re-Verifications      |    |                       |
| - Tamper-Evident Audit  |    |                       |
+-------------------------+    +-----------------------+
```

---

## 2. Frontend Layer (React 18 + Vite)

### 2.1 Technology Stack
- **Framework**: React 18 with TypeScript.
- **Build Engine**: Vite 6 (`@tailwindcss/vite`).
- **Icons**: Lucide React.
- **State Management**: React Context (`AppContext.tsx`) with zero external boilerplate.
- **Styling**: Glassmorphism with modern CSS custom properties, deep cyber-dark background (`#070b14`), cyan/violet accents, high-contrast readable typography.

### 2.2 User Journey Routes
1. **Public Landing (`/`)**:
   - High-impact Hero: *"Know What Is Wrong. Know Why. Verify It Yourself."*
   - Main CTA: Primary target input box with instant validation.
   - Interactive 9-Step Assessment Visual Flow.
   - Features Grid & Enterprise Security Audit Standard alignment.
2. **Authorization Gate Modal**:
   - Triggered upon entering a target URL.
   - Requires explicit legal checkboxes: Ownership / Authorized Assessment Scope.
3. **Command Center (`/command-center`)**:
   - Real-time assessment progress bar, stage indicator, and category status.
4. **Evidence & Terminal Inspector (`/evidence`)**:
   - Simple view: What was found, why it matters, where it was found, AI analysis, confidence.
   - Technical view: Terminal command (`curl`), expected result, observed result, identical Evidence ID.
   - Re-Verification action: Re-test finding and review diff.
5. **Executive & Compliance Reports (`/report`)**:
   - Print-friendly audit reports with verifiable hashes.

---

## 3. Backend Layer (FastAPI 0.115+)

### 3.1 Asynchronous Execution
- Assessment tasks run asynchronously. Endpoints return status IDs (`ASM-XXXX`) immediately, allowing the frontend to poll progress without blocking HTTP connections.
- Health probes, evidence generation, and AI explanations are served via isolated endpoints.

### 3.2 Security Controls
- **Input Sanitization**: Strict Pydantic models reject invalid URLs, malformed JSON, and oversized headers.
- **Safe Probes Only**: Probing engine uses bounded timeouts (5s) and strictly non-destructive methods (GET, HEAD, test query reflection). Destructive exploits (DROP TABLE, remote file upload, buffer overflows) are strictly prohibited.
- **Credential Protection**: Database connection strings, API tokens, and AI endpoints reside exclusively in environment variables and are never sent to the client.

---

## 4. AI Provider Architecture (Server-Side)

Online visitors do **not** need Ollama or Python installed locally:
1. When the client requests AI analysis (`/api/findings/{id}/analyze`), the request hits the backend.
2. The backend queries its configured server-side AI provider (Ollama instance running on the host or cloud container).
3. If Ollama is offline or times out, the backend immediately invokes the **Deterministic Rule-Based Intelligence Engine**, returning structured explanations, impact statements, and remediation playbooks without failing or hanging.
