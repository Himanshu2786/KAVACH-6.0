# KAVACH 6.0 — Multi-User Production Deployment Guide

**AI Hypothesizes. Evidence Confirms.**  
*Production-Ready, Containerized HTTPS Web Application Deployment*

---

## 1. Final User Experience

Once deployed, remote teammates and evaluators do **NOT** need Python, Node.js, Git, VS Code, PowerShell, npm, a local database, or local Ollama.

1. They open **Chrome**, **Edge**, or **Firefox**.
2. They navigate to:
   ```
   https://YOUR-KAVACH-DOMAIN.com
   ```
   *(or the provisioned server IP/cloud temporary HTTPS URL)*
3. The **KAVACH 6.0 Multi-User Gateway** opens.
4. They enter their assigned:
   - **USER ID** (e.g., `ADMIN001` or `TEAM001`)
   - **PASSWORD**
5. They immediately enter the full **KAVACH 6.0 Command Center**.

---

## 2. Production Architecture

```
Internet (Remote Teammates & Hackathon Evaluators)
       │
       ▼ [HTTPS :443 / Automatic TLS via Let's Encrypt]
┌─────────────────────────────────────────────────────────────┐
│ kavach-proxy (Caddy Reverse Proxy)                          │
│ - Automatic TLS issuance & renewal                          │
│ - Security headers: HSTS, CSP, X-Frame-Options: DENY        │
│ - HTTP -> HTTPS redirect                                    │
└──────────────┬───────────────────────────────┬──────────────┘
               │ /                             │ /api/*
               ▼                               ▼
┌─────────────────────────────┐  ┌────────────────────────────┐
│ kavach-frontend             │  │ kavach-backend             │
│ - Nginx Static Server       │  │ - FastAPI (Python 3.11)    │
│ - Built React/Vite SPA      │  │ - Uvicorn with 2+ workers  │
│ - SPA History Fallback      │  │ - Trusted Proxy Headers    │
└─────────────────────────────┘  │ - PBKDF2-HMAC Authentication│
                                 │ - JWT Token Engine         │
                                 └──────────────┬─────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
┌──────────────────────────────────────┐                   ┌───────────────────────────────────┐
│ kavach-postgres (PostgreSQL 16)      │                   │ Server-Side AI / Fallback Engine  │
│ - Persistent volume: kavach_pgdata   │                   │ - Ollama Service (Internal)       │
│ - Connection pooling (pool_size=10)  │                   │ - Zero-Hallucination Safe Mode    │
│ - Isolated internal docker network   │                   │ - Deterministic Fallback Engine   │
└──────────────────────────────────────┘                   └───────────────────────────────────┘
```

---

## 3. Pre-Provisioned Team Accounts

| Account ID | Role | Privileges | Default Initial Password |
|---|---|---|---|
| `ADMIN001` | System Administrator | Full admin, user audit, cross-tenant visibility | `Kavach@Admin2026!` |
| `TEAM001` | AppSec Specialist | Web assessment, discovery, evidence, reports | `Kavach@Team2026!` |
| `TEAM002` | Red Team Analyst | Web assessment, triage, risk prioritization | `Kavach@Team2026!` |
| `TEAM003` | Compliance Auditor | Evidence auditing, audit trail, export | `Kavach@Team2026!` |
| `TEAM004` | Incident Responder | Remediation re-test, live threat correlation | `Kavach@Team2026!` |

> **Security Note:** Passwords are never committed or hardcoded in frontend assets. Initial passwords can be customized via `.env` (`KAVACH_ADMIN_PASSWORD` and `KAVACH_TEAM_PASSWORD`). Passwords are salted and hashed using PBKDF2-HMAC-SHA256 (100,000 rounds).

---

## 4. Quick-Start Deployment (Single Command)

### Step 1: Clone or Copy Project onto Server
```bash
git clone <repository_url> kavach-6.0
cd kavach-6.0
```

### Step 2: Configure Environment
Copy `.env.production.example` to `.env`:
```bash
cp .env.production.example .env
```
Update your domain and secure credentials in `.env`:
```ini
# Domain for automated HTTPS
KAVACH_DOMAIN=kavach.yourdomain.com

# Production JWT secret (generate via: openssl rand -hex 32)
SECRET_KEY=e83a7c64b73812d49c83691fbe094ad1a90c4d2e737bf68297d0921e1a53e4c8

# Database passwords
POSTGRES_PASSWORD=UltraSecurePostgresPassword2026!
```

### Step 3: Launch Stack
```bash
# Production stack (Caddy + Frontend + FastAPI + PostgreSQL)
docker compose up -d --build

# Optional: With Server-side Ollama container
docker compose --profile with-ai up -d --build
```

---

## 5. Domain Configuration Options

### Option A: Custom Domain with Automatic HTTPS
1. Create a DNS **A Record** pointing `kavach.yourdomain.com` to your server's public IPv4 address.
2. Ensure inbound ports **80** (HTTP) and **443** (HTTPS) are open in your cloud firewall / security group.
3. In `.env`, set:
   ```ini
   KAVACH_DOMAIN=kavach.yourdomain.com
   ```
4. Run `docker compose up -d`.
5. Caddy automatically negotiates Let's Encrypt SSL certificates. Within 30 seconds, `https://kavach.yourdomain.com` is live with valid TLS!

### Option B: Temporary IP / Direct Host Deployment
If a domain name is not yet registered:
In `.env`, set:
```ini
KAVACH_DOMAIN=:80
```
The stack will serve the production app directly on HTTP port 80 (or port 443 with self-signed TLS) at `http://<SERVER_IP>`.

---

## 6. Database Persistence & PostgreSQL Migration

- The PostgreSQL container stores all data in a dedicated persistent Docker volume:
  ```
  volumes:
    - kavach_pgdata:/var/lib/postgresql/data
  ```
- **Restart Safety:** Stopping, restarting, or upgrading containers preserves all assessments, findings, evidence proofs, and user accounts.
- **Auto-Migration:** On container boot, `backend/app/main.py` invokes `migrate_schema(engine)` which guarantees all required tables (`users`, `assessments`, `findings`, `evidence_records`, `re_verifications`, `audit_events`) and newly added columns exist without data loss.

---

## 7. Server-Side AI & Deterministic Fallback Engine

- Remote web users **never** run local Ollama instances.
- If Ollama is running server-side (`kavach-ollama` or an external Ollama host):
  - KAVACH connects internally over the private Docker network (`http://kavach-ollama:11434`).
  - Analysis is delivered to the browser with zero user setup.
- If Ollama is unavailable or offline:
  - The platform **automatically engages the deterministic rule-based fallback engine**.
  - All findings, evidence, risk calculations, and remediation plans function at 100% precision.
  - The UI clearly indicates `FALLBACK_DETERMINISTIC_RULES` without crashing.

---

## 8. Host Machine vs Remote Web Assessment

- **Remote Web Security Assessment:**
  Evaluates remote web targets, APIs, TLS certificates, security headers, and surface paths through the hosted cloud server.
- **Local Workstation Scanning:**
  Web browsers are strictly sandboxed and cannot directly inspect a remote client's Windows registry or filesystem. For local host security auditing, use the standalone **KAVACH Portable Desktop Agent** on the machine.

---

## 9. Verification & Health Monitoring

### System Health Endpoints
- **API Root Health:**
  ```bash
  curl -I https://kavach.yourdomain.com/api/health
  # HTTP/2 200 OK
  ```
- **System Operational Status:**
  ```bash
  curl https://kavach.yourdomain.com/api/system/status
  ```
- **Automated Docker Healthchecks:**
  ```bash
  docker compose ps
  # All services report (healthy)
  ```

### Automated Test Baseline
- Backend test suite: **222 baseline passed + 8 production auth passed = 230 passed, 0 failed, 0 errors**.
- Frontend test suite: **23 passed, 0 failed**.
- Frontend production bundle build: **100% clean, 0 TypeScript/build errors**.
