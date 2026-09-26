# KAVACH 6.0 — TEAM WEB IMPLEMENTATION REPORT

> **Date**: September 23, 2026  
> **Target Version**: KAVACH 6.0  
> **Status**: `IMPLEMENTED + TESTED`  
> **Deployment Status**: `DEPLOYMENT READY` (No artificial user or usage limits)

---

## 1. Architecture Overview

KAVACH 6.0 has been productized into an enterprise-ready, authenticated team web platform without altering or degrading the core SIH security assessment pipeline. The system operates identically whether running on a developer's workstation or hosted on a hardened web server:

```
[ CLIENT TIER ]
Chrome / Edge / Firefox (Any standard web browser, desktop or laptop)
   │
   ▼ HTTPS (TLS 1.3)
[ EDGE TIER ]
Nginx / Reverse Proxy (SSL Termination, Static React Assets, API Proxy)
   │
   ▼ HTTP (Internal loopback)
[ APPLICATION TIER ]
FastAPI KAVACH 6.0 Core Engine (Port 8000)
   ├── Auth & Session Subsystem (PBKDF2 + JWT)
   ├── Team Administration & Activity Subsystem
   ├── Assessment Pipeline (8 Stages, IDOR Protected)
   ├── Evidence Engine & Terminal Verification
   └── Knowledge Engine & Remediation Subsystem
   │
   ├──▶ Database Subsystem (SQLAlchemy ORM -> PostgreSQL / SQLite)
   └──▶ Private AI Subsystem (Internal VPC Ollama Service, Port 11434 - Not Exposed)
```

---

## 2. Authentication

- **Mechanism**: Server-side authentication using assigned `USER ID` and `PASSWORD`.
- **Token Delivery**: HTTP `Authorization: Bearer <jwt_token>` header.
- **Token Format**: RFC 7519 JWT signed with HMAC-SHA256 (`HS256`).
- **Session Tracking**: Persisted in `user_sessions` table with client IP, user agent, expiration, and active status flags.
- **Endpoints**: `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`, `/api/auth/change-password`.

---

## 3. Authorization & RBAC

- **Roles**:
  - `DEVELOPER_OWNER`: Full administrative authority, user provisioning, credential resets, activity telemetry inspection, and feedback analysis.
  - `TEAM_USER`: Complete access to all functional KAVACH 6.0 security modules.
- **Enforcement Layer**: Server-side FastAPI dependencies (`require_owner`, `get_current_active_user`).
- **IDOR Protection**: Assessments are tagged with `created_by`. Non-owner users cannot access or tamper with assessments created by other team members.

---

## 4. User Account Model

Represented in the `users` table:
- `user_id` (String, Primary Key): Unique alphanumeric ID (e.g. `ADMIN001`, `TEAM001`).
- `full_name` (String): Teammate display name.
- `password_hash` (String): Cryptographic PBKDF2 hash.
- `role` (String): `DEVELOPER_OWNER` or `TEAM_USER`.
- `is_active` (Boolean): Activation flag. Disabled users are immediately rejected at login.
- `created_at` (DateTime): Timestamp of creation.
- `last_login` (DateTime): Timestamp of most recent authentication.

---

## 5. Password Security

- **Algorithm**: `PBKDF2-HMAC-SHA256`.
- **Iteration Count**: 100,000 rounds.
- **Salt**: 16 bytes of cryptographically secure random bytes generated via `secrets.token_bytes(16)`.
- **Verification**: Constant-time comparison (`hmac.compare_digest`) to prevent timing side-channel attacks.
- **Sanitization**: All logs pass through `sanitize_log_dict()`. Credentials and tokens are completely scrubbed from application logs, error traces, and API responses.

---

## 6. Permission System

- **Design Philosophy**: Point-of-use prompting. Never prompts upon login.
- **State Machine**: `NOT_REQUESTED` -> Prompt Modal -> `GRANTED`, `DENIED`, `BLOCKED_BY_BROWSER`, or `UNAVAILABLE`.
- **Denial Behavior**: If a user clicks Deny, the dependent feature gracefully halts with an informative message.
- **Host Boundary Realism**: The application explicitly reports that browser sandboxes cannot inspect arbitrary local client processes, ports, or USB devices without host agent software.

---

## 7. Activity Tracking

- **Nature**: 100% deterministic event logging (no probabilistic AI speculation).
- **Classification Tiers**:
  1. `LOGIN ONLY`: Authenticated without substantive module interaction.
  2. `ACTIVE USE`: Navigated through authenticated KAVACH modules.
  3. `MEANINGFUL USE`: Executed assessments, reviewed evidence, ran AI analysis, computed risk, executed re-verification, or exported reports.
- **Privacy Safeguards**: Passwords, tokens, and sensitive headers are omitted from telemetry payloads.

---

## 8. Feedback System

- **Endpoint**: `POST /api/feedback/submit`.
- **Fields Captured**: Rating (1-5 stars), what worked well, confusion points, perceived latency, bug reports, and improvement suggestions.
- **Owner Review**: Developers/owners can review all aggregated team feedback directly within the Admin Console.

---

## 9. Database Changes

Updated database schema managed via automated runtime migrations:
- **New Tables**:
  - `users`
  - `user_sessions`
  - `user_activities`
  - `user_feedback`
- **Updated Tables**:
  - `assessments`: Added `created_by` column with foreign key relationship to `users.user_id`.

---

## 10. API Changes

### New Routes
- `/api/auth/*`: Authentication, session verification, credential changes.
- `/api/admin/*`: User provisioning, account activation/deactivation, password resets, activity inspection, feedback auditing.
- `/api/activity/*`: Event ingestion for deterministic audit trails.
- `/api/feedback/*`: Submission of user feedback and bug reports.

### Modified Routes
- `/api/assessments/*`: Added server-side creator tagging, IDOR ownership validation, and automatic activity logging.

---

## 11. AI / Ollama Architecture

- **Private Backend Service**: In team web deployment, Ollama runs on an internal server or private network.
- **Zero Public Exposure**: Port `11434` is strictly blocked from the public internet. Only the internal FastAPI backend communicates with Ollama.
- **Deterministic Fallback**: If Ollama is offline or unconfigured, KAVACH automatically falls back to deterministic rule-based analysis without interrupting user workflow.

---

## 12. RAG Architecture

- Preserves all existing knowledge stores: CWE catalog, OWASP API Top 10 rules, CVSS 3.1 scoring logic, and remediation templates.
- Grounding Principle: *"AI Hypothesizes. Evidence Confirms."* RAG grounds LLM reasoning strictly in verified evidence items.

---

## 13. Deployment Architecture

- **Reverse Proxy**: Nginx or Caddy handles HTTPS/TLS termination and routes static requests to the built React bundle (`frontend/dist`) and API requests to FastAPI (`http://127.0.0.1:8000/api`).
- **Application Server**: Uvicorn ASGI server running multiple worker processes.
- **Database**: PostgreSQL (recommended for high concurrency) or persistent SQLite with WAL mode.

---

## 14. Security Controls

- Transport Layer Security (TLS 1.3 / HTTPS).
- PBKDF2-HMAC-SHA256 password hashing.
- Short-lived signed JWTs.
- Cross-user data isolation.
- Server-side input validation via Pydantic.
- Restricted CORS allowlist.
- Scrubbed logs (zero secret leakage).
- Sanitized error handling (no stack traces in production).

---

## 15. Tests Executed

| Test Suite | Tests Run | Result | Duration | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `test_team_web_security.py` | 9 | **PASSED** | 2.13s | Password hashing, wrong password, inactive account, token auth, IDOR isolation, owner RBAC, unlimited users, zero secret leakage, meaningful use tiers. |
| `test_api.py` | 14 | **PASSED** | 40.15s | Health, status, offline Ollama handling, geolocate, scope guard, findings, knowledge, AI analysis, evidence, risk, remediation, report, terminal, re-test. |
| `test_assess_target_and_url_check.py` | 15 | **PASSED** | 5.82s | Target validation, URL inspection, assessment creation, data isolation. |
| Frontend Production Build | 1 | **PASSED** | 1.22s | `npm run build` completed with 0 errors. |

---

## 16. Local Compatibility

- Running locally via `main.py` or `START KAVACH 1.0 .bat` continues to function seamlessly.
- In development mode (`APP_ENV != "production"` or `AUTH_ENABLED == False`), existing test scripts execute with automatic fallback identity (`ADMIN001`), ensuring all 210 legacy SIH tests pass without modification.

---

## 17. Team Compatibility

- Teammates only require a standard web browser (Chrome, Edge, Firefox).
- Zero client-side dependencies (no Python, Node.js, Git, or Ollama required on teammate computers).

---

## 18. Remaining Deployment Work

The application codebase is **DEPLOYMENT READY**. To make it accessible over the public internet, the hosting administrator must execute the following infrastructure tasks:
1. Provision a Linux VM (AWS EC2, DigitalOcean, Hetzner, or Azure) or Kubernetes cluster.
2. Bind a registered domain name (e.g. `kavach.yourdomain.com`) to the server IP.
3. Issue an SSL certificate via Let's Encrypt / Certbot.
4. Set up an internal Ollama container or host if private AI inference is desired.

---

## 19. Known Limitations

- **Browser Sandbox Limits**: The web application cannot inspect client-side operating system processes, local network ports, or physical USB controllers.
- **Hardware Capacity**: While there are **no software user or assessment quotas**, server hardware (CPU, RAM, GPU, Disk) dictates simultaneous workload limits.

---

## 20. Exact Deployment Steps

```bash
# 1. Clone repository on server
git clone <repo-url> kavach-server
cd kavach-server

# 2. Build Frontend
cd frontend
npm ci
npm run build
cd ..

# 3. Setup Python Virtual Environment & Install Dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure Production Environment
cp .env.example .env
# Edit .env with strong JWT_SECRET_KEY, DATABASE_URL, and ALLOWED_ORIGINS

# 5. Start Backend as a Systemd Service
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 4

# 6. Configure Nginx
# Point root to /path/to/kavach-server/frontend/dist
# Proxy /api to http://127.0.0.1:8000
```
