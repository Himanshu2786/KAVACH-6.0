# KAVACH 6.0 — TEAM WEB GUIDE
### Master Guide to Architecture, Deployment, Authentication & Team Collaboration

> **Target Version**: KAVACH 6.0 (Preserved Core Architecture)  
> **Status**: `IMPLEMENTED + TESTED`  
> **Deployment Status**: `DEPLOYMENT READY` (No artificial user or usage limits)

---

## Technical Concept Glossary (Dual-Explanation Format)

Before diving into system procedures, review these foundational concepts:

### 1. API (Application Programming Interface)
- **Simple Explanation**: A digital counter where the frontend web page orders data or asks the server to perform a task.
- **Technical Explanation**: A contract of HTTP REST endpoints (`GET`, `POST`, `PUT`, `DELETE`) exchanging JSON payloads over TCP/IP, adhering to OpenAPI specifications and validated via Pydantic models.

### 2. Authentication
- **Simple Explanation**: The digital ID check that verifies *who you are* via your User ID and password.
- **Technical Explanation**: The verification of submitted credentials against stored cryptographic hashes, issuing a signed JSON Web Token (`JWT`) upon successful validation.

### 3. Authorization
- **Simple Explanation**: The digital security badge checking *what you are allowed to see or do*.
- **Technical Explanation**: Server-side policy enforcement matching the authenticated user's role and identity against requested operations and data records (preventing Broken Object-Level Authorization).

### 4. RBAC (Role-Based Access Control)
- **Simple Explanation**: Giving team members regular keys and the system administrator master keys.
- **Technical Explanation**: An access governance model assigning permissions to distinct roles (`DEVELOPER_OWNER` vs `TEAM_USER`) enforced via FastAPI route dependencies (`require_owner`).

### 5. Session
- **Simple Explanation**: The ongoing conversation between your browser and the server while you are logged in.
- **Technical Explanation**: A database-persisted token record (`user_sessions` table) storing client IP, user agent, issuance timestamp, and expiration time.

### 6. JWT (JSON Web Token)
- **Simple Explanation**: A digitally stamped pass your browser carries so you don't have to type your password on every click.
- **Technical Explanation**: A compact, URL-safe string containing a cryptographically signed payload (`sub`, `role`, `exp`) using `HMAC-SHA256` (`HS256`) and a secret key.

### 7. Database
- **Simple Explanation**: The organized digital filing cabinet where all users, assessments, findings, and logs live permanently.
- **Technical Explanation**: A relational storage engine (SQLite for local/test, PostgreSQL for scalable team web deployment) managed via SQLAlchemy ORM.

### 8. RAG (Retrieval-Augmented Generation)
- **Simple Explanation**: A smart research assistant that looks up authoritative security rulebooks before answering questions.
- **Technical Explanation**: A retrieval pipeline searching local vector and keyword indices (CWE, OWASP, NIST) to supply relevant reference context directly to LLM prompts, preventing hallucinations.

### 9. Ollama
- **Simple Explanation**: The local or private server engine that runs the artificial intelligence brain.
- **Technical Explanation**: An open-source local LLM runner exposing an OpenAI-compatible internal HTTP API (typically port `11434`), running quantized models like `qwen2.5-coder` or `llama3`.

### 10. CWE (Common Weakness Enumeration)
- **Simple Explanation**: The universal dictionary of software vulnerabilities and security flaws.
- **Technical Explanation**: A community-developed taxonomy of software security weaknesses maintained by MITRE, serving as categorical vulnerability anchors in KAVACH findings.

### 11. OWASP (Open Worldwide Application Security Project)
- **Simple Explanation**: The world standard checklist for the most dangerous web and API security risks.
- **Technical Explanation**: A non-profit foundation providing industry-standard risk classifications (e.g., OWASP Top 10, API Security Top 10) referenced by KAVACH's knowledge engine.

### 12. Evidence
- **Simple Explanation**: The hard proof (like a screenshot, server header, or cURL command) showing a bug really exists.
- **Technical Explanation**: Deterministic, reproducible data artifacts (HTTP response bodies, TLS handshake logs, socket dumps) linked to findings, enforcing the principle: *"AI Hypothesizes. Evidence Confirms."*

### 13. Audit Trail
- **Simple Explanation**: An unchangeable logbook recording every important thing that happened in the application.
- **Technical Explanation**: An append-only chronological database log tracking user actions, timestamps, and parameters for accountability and forensic auditability.

### 14. HTTPS (Hypertext Transfer Protocol Secure)
- **Simple Explanation**: A secure tunnel that encrypts everything passing between your browser and the website.
- **Technical Explanation**: HTTP communication layered over TLS/SSL encryption, protecting data integrity, session tokens, and passwords from eavesdropping and man-in-the-middle attacks.

### 15. CORS (Cross-Origin Resource Sharing)
- **Simple Explanation**: A security rule telling browsers which outside websites are allowed to talk to your server.
- **Technical Explanation**: HTTP response headers (`Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`) validated by the browser to restrict cross-domain API calls.

### 16. CSRF (Cross-Site Request Forgery)
- **Simple Explanation**: A trick where an evil website tries to make your browser execute unauthorized commands while you are logged in.
- **Technical Explanation**: An attack mitigated in KAVACH via short-lived Bearer tokens in the `Authorization` header rather than ambient cookie authentication.

### 17. Hashing
- **Simple Explanation**: Turning a password into a unique scrambled fingerprint that cannot be turned back into the original word.
- **Technical Explanation**: A one-way mathematical function (`PBKDF2-HMAC-SHA256` with 100,000 rounds and random salt) ensuring stored credentials cannot be reversed even if the database is leaked.

---

## 25 Master Sections

### Section 1: What This Deployment Is
KAVACH 6.0 Team Web Deployment allows multiple team members to access the complete KAVACH 6.0 cyber posture platform over a standard web browser (Chrome, Edge, Firefox) without needing local development tools. It transforms the single-user developer application into an enterprise-ready, authenticated, multi-user web service.

### Section 2: What a Teammate Experiences
Teammates open the HTTPS URL in their browser, enter their assigned `USER ID` and `PASSWORD`, and immediately land on the full KAVACH 6.0 application. They have access to the Command Center, 8-Stage Assessment Pipeline, Evidence Engine, AI Analysis, Risk Scoring, Remediation, and PDF/JSON Reporting. There is no artificial "User Mode" or feature gating.

### Section 3: How Login Works
1. User enters `USER ID` and `PASSWORD` at `/login`.
2. Frontend calls `POST /api/auth/login`.
3. Backend retrieves the user, extracts salt, and computes `PBKDF2-HMAC-SHA256(100,000 rounds)`.
4. If verified, the server creates a `user_sessions` entry and returns an `HS256` signed JWT.
5. Frontend stores the token in memory and local session storage, attaching it as `Bearer <token>` to all subsequent API calls.

### Section 4: USER ID / Password System
- **ID Structure**: Human-readable, owner-assigned strings (e.g., `TEAM001`, `TEAM002`).
- **Password Strength**: Minimum 8 characters with required complexity (upper, lower, digits, symbols recommended).
- **Storage**: Never stored in plaintext; stored as `pbkdf2:sha256:100000$<salt>$<hash>`.
- **Distribution**: The developer/owner provisions the account and securely shares credentials out-of-band.

### Section 5: How Permissions Work
Permissions are requested **strictly at point-of-use**. If a user triggers a feature requiring browser notifications, clipboard access, or file upload:
1. KAVACH intercepts the action and displays an informative modal.
2. The modal states *which feature* requires permission, *why* it is needed, and *what KAVACH uses it for*.
3. The user makes an informed choice: [ Grant Permission ] or [ Deny ].

### Section 6: What Happens When Permission is Denied
- If the user clicks **Deny**, the feature gracefully halts.
- A polite banner explains: *"Permission was declined. Feature execution halted."*
- The application never crashes, never locks the user out, and never assumes permission was granted.

### Section 7: Team Member Activity Tracking
KAVACH records deterministic event logs to provide diagnostic clarity into product usage:
- **Tiers**: `LOGIN ONLY`, `ACTIVE USE`, `MEANINGFUL USE`.
- **Events**: Page views, assessment creation, finding inspection, AI hypothesis generation, risk analysis, re-verification, and report exports.
- **Safety**: Passwords, tokens, and sensitive headers are scrubbed via `sanitize_log_dict()`.

### Section 8: Owner Activity Dashboard
Exclusively available to `DEVELOPER_OWNER` accounts at `/admin`:
- **Team Overview Table**: Lists all users, last active time, sessions count, assessments created, reports exported, and deterministic usage tier.
- **Activity Timeline**: Chronological, searchable feed of user actions with timestamp, event type, and outcome.
- **Feedback Inspector**: Consolidated view of team ratings, bug reports, and suggestions.

### Section 9: Data Isolation & IDOR Protection
- Every assessment record contains a `created_by` attribute.
- When an assessment is requested (`GET /api/assessments/{id}`), the server checks:
  - Is the caller `DEVELOPER_OWNER`? (Granted).
  - Is the caller the original creator (`created_by == current_user.user_id`)? (Granted).
  - Otherwise, return `403 Forbidden` or `404 Not Found`.
- Team users cannot view or manipulate other team members' private assessments.

### Section 10: AI / Ollama Architecture
- **Local Mode**: Developer runs Ollama on `127.0.0.1:11434`.
- **Team Web Deployment**: Ollama runs on a private internal backend server or private container network.
- **Security Boundary**: Port `11434` is **never exposed to the public internet**. Only the internal FastAPI backend communicates with Ollama.
- **Offline Fallback**: If Ollama is offline or busy, KAVACH automatically falls back to deterministic rule-based analysis without degrading the UI.

### Section 11: RAG Architecture
- Preserves the existing knowledge base: CWE dictionary, OWASP API Top 10 rules, CVSS 3.1 scoring formulas, and verified remediation templates.
- When an assessment finding is analyzed, the RAG engine queries local embeddings/indices to ground the prompt in verifiable facts before querying the LLM.

### Section 12: Database Architecture
- **Local Mode**: Default SQLite (`kavach.db`).
- **Team Web Deployment**: PostgreSQL or multi-process SQLite with WAL (Write-Ahead Logging) enabled.
- **Entity Model**:
  - `users`: Credentials, role, activation state.
  - `user_sessions`: Active JWT sessions and client IP/agent.
  - `user_activities`: Deterministic event logs.
  - `user_feedback`: User ratings, bug reports, and suggestions.
  - `assessments`: Security scan jobs tagged with `created_by`.
  - `findings`, `evidence_items`, `audit_events`: Core security pipeline entities.

### Section 13: Local vs. Team Web Architecture
```
[ LOCAL DEVELOPER DEPLOYMENT ]
Developer Laptop
  Browser -> localhost:5173 (Vite) -> localhost:8000 (FastAPI) -> kavach.db -> 127.0.0.1:11434 (Ollama)

[ TEAM WEB DEPLOYMENT ]
Teammates (Chrome / Edge / Firefox)
  HTTPS kavach.domain.com (Reverse Proxy: Nginx / Caddy)
    ├── Static Web Assets (React / Vite Build)
    └── Reverse Proxy to Backend -> FastAPI (Port 8000 internal)
          ├── PostgreSQL or kavach.db (Persistent Storage)
          └── Internal Network Only -> Private Ollama Host (11434 internal)
```

### Section 14: Security Controls
- Transport Layer Security (TLS 1.3 / HTTPS).
- PBKDF2-HMAC-SHA256 password hashing.
- Short-lived signed JWTs.
- Cross-user data isolation.
- Server-side input validation via Pydantic.
- Restricted CORS allowlist.
- Scrubbed logs (zero secret leakage).
- Sanitized error handling (no stack traces in production).

### Section 15: Deployment Architecture
A recommended production container or VM stack:
1. **Nginx / Cloudflare**: Handles HTTPS, SSL termination, and static frontend assets.
2. **FastAPI Application Server**: Runs `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`.
3. **Database Server**: PostgreSQL instance or managed DB.
4. **AI Host**: Dedicated GPU/CPU instance running Ollama on an internal VPC network.

### Section 16: Environment Variables
Create a production `.env` file based on `.env.example`:
```env
APP_ENV=production
DEBUG=false
AUTH_ENABLED=true
JWT_SECRET_KEY=generate-a-strong-random-64-char-string
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=postgresql://kavach_user:password@localhost:5432/kavach_db
OLLAMA_BASE_URL=http://internal-ollama-host:11434
ALLOWED_ORIGINS=https://kavach.yourdomain.com
```

### Section 17: How to Deploy
1. **Build Frontend**:
   ```bash
   cd frontend
   npm ci
   npm run build
   ```
2. **Install Backend Dependencies**:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```
3. **Configure Nginx**:
   Serve `frontend/dist` on port 443; reverse proxy `/api` to `127.0.0.1:8000`.
4. **Start Backend**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   ```

### Section 18: How a Teammate Starts Using KAVACH
1. Teammate receives the HTTPS link and their credentials from the owner.
2. Opens Chrome, Edge, or Firefox.
3. Visits `https://kavach.yourdomain.com`.
4. Enters `USER ID` and `PASSWORD`.
5. Explores the Command Center or launches a new assessment.

### Section 19: How to Create Accounts
As the `DEVELOPER_OWNER`:
1. Log in with `ADMIN001`.
2. Click **Admin Console** in the top navigation.
3. In the **Team Accounts** tab, fill out:
   - User ID (e.g. `TEAM005`)
   - Full Name (e.g. `Jane Doe`)
   - Initial Password
4. Click **Create Team Account**.
5. Privately deliver credentials to the teammate.

### Section 20: How to Reset Accounts & Passwords
1. Open **Admin Console** -> **Team Accounts**.
2. Locate the team member in the table.
3. Click **Reset Password**, enter the new temporary password, and confirm.
4. If an account needs suspension, click **Deactivate**. The user cannot log in until re-activated.

### Section 21: How to Inspect Activity
1. Open **Admin Console** -> **Activity Timeline**.
2. Filter by user or event type.
3. Verify deterministic actions (e.g. `ASSESSMENT_STARTED`, `REPORT_EXPORTED`).
4. Switch to **Usage Analytics** to view each teammate's deterministic usage tier.

### Section 22: Troubleshooting Common Issues
- **"Network Error / Unable to reach server"**: Verify backend is running and Nginx is proxying `/api` correctly.
- **"Invalid credentials"**: Confirm `USER ID` casing and password accuracy. Check if account is active in Admin Console.
- **"AI Analysis showing offline fallback"**: Check internal Ollama server connectivity (`curl http://internal-ollama-host:11434/api/tags`).
- **"CORS Blocked"**: Ensure `ALLOWED_ORIGINS` in `.env` matches the exact browser URL.

### Section 23: Browser Limitations
A remote browser cannot:
- Inspect client operating system processes (`ps`, `tasklist`).
- Scan client hardware USB devices directly.
- Port scan private LAN addresses without browser security blocks.
KAVACH honestly communicates these constraints on host posture pages.

### Section 24: Infrastructure Limitations
While KAVACH imposes **no artificial user or usage quotas**, real servers have physical limits:
- Server CPU / RAM dictates how many assessments can run concurrently.
- GPU capacity limits simultaneous Ollama AI inference calls.
- Disk capacity dictates how many evidence payloads and PDF reports can be stored.

### Section 25: Known Limitations
- Background task queues (e.g. Celery/Redis) can be added for massive concurrent scanning jobs.
- Single-node SQLite should be migrated to PostgreSQL for teams exceeding 50 concurrent active users.
