# KAVACH — Production Deployment Guide

This guide details instructions for deploying KAVACH as a secure, public-facing online web service.

---

## 1. Production Architecture Overview

```
[ INTERNET / CLIENT BROWSERS ]
               │
               ▼ (Port 443 / HTTPS)
       [ NGINX REVERSE PROXY ]
       ├── Terminating SSL / TLS 1.3
       ├── Rate Limiting (100 req/min per IP)
       └── Strict Security Headers
               │
      ┌────────┴────────┐
      ▼ (Port 80)       ▼ (Port 8000)
[ FRONTEND STATIC ]   [ FASTAPI BACKEND API ]
  (Compiled Vite)     (Uvicorn Multi-Worker)
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
        [ DATABASE ]      [ PROBER ]     [ SERVER AI ]
       (PostgreSQL /     (Async Httpx)   (Hosted Ollama
         SQLite)                          Service)
```

---

## 2. Environment Configuration (`.env`)

Create a secure `.env` file in the root directory:

```env
# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=generate-a-cryptographically-secure-64-char-key

# Database Connection (SQLite or PostgreSQL)
DATABASE_URL=sqlite:///./kavach.db
# DATABASE_URL=postgresql://kavach_user:strong_password@localhost:5432/kavach_db

# Server-Side AI Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
AI_TIMEOUT_SECONDS=15.0

# CORS Allowed Origins
CORS_ORIGINS=["https://kavach.yourdomain.com", "https://api.kavach.yourdomain.com"]
```

---

## 3. Step-by-Step Deployment Procedure

### Step 1: Backend Setup & Dependency Installation
```bash
# From workspace root
python -m venv venv
# Linux/macOS: source venv/bin/activate
# Windows: .\venv\Scripts\activate

pip install -r backend/requirements.txt
```

### Step 2: Database Migration & Seeding
```bash
# Seed initial CWE/OWASP knowledge base and World Monitor benchmark
python -c "from backend.app.core.database import init_db; init_db()"
```

### Step 3: Frontend Compilation
```bash
cd frontend
npm install
npm run build
# Compiled assets output to: frontend/dist/
```

### Step 4: Run Production Servers
```bash
# Run FastAPI Backend with Uvicorn (4 Workers)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Serve Frontend static assets via Nginx or Caddy
```

---

## 4. Reverse Proxy Hardening (Nginx Configuration)

```nginx
server {
    listen 443 ssl http2;
    server_name kavach.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/kavach.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kavach.yourdomain.com/privkey.pem;

    # Defensive Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Frontend Static Distribution
    location / {
        root /var/www/kavach/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Routing
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 5. Health Probes & Monitoring
- Backend API Health: `GET https://kavach.yourdomain.com/api/system/health`
- Server-Side AI Status: `GET https://kavach.yourdomain.com/api/system/ollama/status`
