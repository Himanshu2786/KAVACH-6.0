# KAVACH 6.0 — Team Web Deployment Architecture & Runbook

> **Platform Version:** KAVACH 6.0  
> **Deployment Status:** DEPLOYMENT READY (LOCALLY TESTED & VERIFIED)  
> **Target Experience:** "The same KAVACH 6.0 application experience, available to team members through a normal web browser."

---

## 1. Executive Deployment Architecture

In team web deployment, teammates access KAVACH over HTTPS using Chrome, Edge, or Firefox without requiring Python, Node.js, Git, terminal tools, or a local Ollama installation on their client devices.

```
                      +---------------------------------------+
                      |         Teammate Web Browser          |
                      |      (Chrome / Edge / Firefox)        |
                      +---------------------------------------+
                                          |
                                    HTTPS (TLS 443)
                                          |
                                          v
                      +---------------------------------------+
                      |      Reverse Proxy (Nginx / Caddy)    |
                      |  - Terminates TLS/HTTPS certificates  |
                      |  - Serves static React UI (dist/)     |
                      |  - Proxies /api/* to FastAPI (:8000)  |
                      +---------------------------------------+
                                          |
                                    Internal HTTP
                                          |
                                          v
                      +---------------------------------------+
                      |          KAVACH 6.0 Backend           |
                      |         (FastAPI Python 3.11)         |
                      |  - Server-Side Token Authentication   |
                      |  - Role-Based Access Control (RBAC)   |
                      |  - Cross-User Assessment Isolation    |
                      |  - Deterministic Activity Tracking    |
                      |  - Evidence & Risk Calculation Engines|
                      +-------------------+-------------------+
                                          |
                         +----------------+----------------+
                         |                                 |
                         v                                 v
        +---------------------------------+  +-------------------------------+
        |       Persistent Database       |  |     Private Server-Side AI    |
        |   (SQLite WAL / PostgreSQL)     |  |       (Internal Ollama)       |
        |  - Users, Sessions, Activities  |  |  - Port 11434 never exposed   |
        |  - Assessments, Findings, Evid. |  |  - Deterministic fallbacks    |
        |  - Audit Events, Feedback       |  |  - Zero secret leakage        |
        +---------------------------------+  +-------------------------------+
```

---

## 2. Key Architectural Guarantees

1. **Same Application Experience**: Authenticated teammates receive the exact same KAVACH 6.0 interface, 8-Stage pipeline, Command Center, World Situational Monitor, Findings Matrix, AI Analysis, Evidence Validation, Risk Scoring, Remediation Center, and Report Export.
2. **No Artificial User Limit**: The platform code enforces NO artificial user count cap (no 5, 10, or 20-seat limits). Maximum capacity is governed solely by the host server's CPU, RAM, and database I/O.
3. **No Artificial Usage Limit**: There are no artificial daily/monthly assessment limits, trial expirations, report quotas, or forced cooldown timers.
4. **Private Server-Side AI**: Ollama runs on an internal server port (e.g. `http://127.0.0.1:11434` or internal Docker network). Port 11434 is **never** exposed to the public internet. If the AI model is temporarily busy or unreachable, KAVACH engages its built-in deterministic lexical fallback without degrading the user workflow.
5. **Data Isolation (IDOR Protection)**: Every assessment is tagged with its creator (`created_by`). Standard team operators can only access their own assessments and shared team/demo assessments. Direct access attempts to another user's private assessments return `403 Forbidden`.

---

## 3. Environment Configuration

Configure KAVACH through environment variables (or `.env` file):

| Variable | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | Enables strict authentication enforcement on all endpoints |
| `JWT_SECRET_KEY` | *(Strong 64-char random hex)* | Secret key for signing HS256 session tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24 Hours) | Security session expiration period |
| `DATABASE_URL` | `sqlite:///./kavach.db` or `postgresql://user:pass@db:5432/kavach` | Database connection string |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Private internal AI endpoint (never public) |
| `OLLAMA_MODEL` | `llama3` or `phi3` | Configured AI inference model |
| `AI_MASK_SENSITIVE` | `true` | Sanitizes secrets, passwords, and tokens before AI inference |
| `BACKEND_CORS_ORIGINS` | `["https://kavach.yourdomain.com"]` | Authorized origin whitelist |
| `DEMO_MODE` | `false` | Sets default assessment posture to live scope |

---

## 4. Production Nginx Reverse Proxy Configuration

Below is a production-grade Nginx configuration ensuring full HTTPS termination, static asset serving, and secure API reverse-proxying:

```nginx
server {
    listen 80;
    server_name kavach.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name kavach.yourdomain.com;

    # SSL Certificates (e.g., Let's Encrypt Certbot)
    ssl_certificate /etc/letsencrypt/live/kavach.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kavach.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Client Request Size
    client_max_body_size 25M;

    # 1. Serve React Frontend Static Build
    location / {
        root /opt/kavach/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 2. Proxy API to FastAPI Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90s;
    }
}
```

---

## 5. Startup & Operational Verification

### Step 1: Initialize Database & Seed Users
```bash
python -c "from backend.app.core.database import engine, Base, migrate_schema; Base.metadata.create_all(bind=engine); migrate_schema(engine)"
```

### Step 2: Build the Frontend Bundle
```bash
cd frontend
npm install
npm run build
```

### Step 3: Launch FastAPI Production Service
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 4
```

---

## 6. Remote Security Checklist

- [x] HTTPS enforced via reverse proxy (TLS 1.2+).
- [x] Internal Ollama service bound exclusively to `127.0.0.1:11434` (never exposed to public internet).
- [x] Passwords hashed using PBKDF2-HMAC-SHA256 with 100,000 rounds and random 16-byte cryptographic salt.
- [x] JWT tokens signed using HMAC-SHA256 with server-side secret key.
- [x] Cross-user assessment protection verified against IDOR attacks.
- [x] Zero credential leakage: Passwords, tokens, and authorization keys strictly redacted from logs and AI prompts.
- [x] Public scanning safety: Mandatory authorization guard required prior to scan execution.
