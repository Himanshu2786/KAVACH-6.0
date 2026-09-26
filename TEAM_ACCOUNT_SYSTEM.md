# KAVACH 6.0 — TEAM ACCOUNT SYSTEM

> **Status**: `IMPLEMENTED + TESTED`  
> **Deployment Status**: `DEPLOYMENT READY` (No artificial user quotas enforced)

---

## 1. Overview & Architectural Principles

The KAVACH 6.0 Team Account System provides robust, production-grade, application-level authentication and role-based access control (RBAC) to enable team collaboration over the web while preserving identical access to KAVACH 6.0 security modules.

### Key Tenets
1. **Identical Experience**: Authenticated teammates access the full KAVACH 6.0 interface. No simplified "User Mode" or stripped-down dashboards.
2. **Owner-Managed Credentials**: The developer/owner provisions `USER ID`s (e.g. `TEAM001`, `TEAM002`) and sets initial passwords. These are distributed out-of-band to teammates.
3. **No Artificial User Quota**: KAVACH enforces **no artificial user cap** (no 5, 10, or 20 user paywalls or subscription limits). System scaling is dictated purely by underlying host infrastructure (CPU, RAM, DB).
4. **No Artificial Usage-Time Limits**: No daily, weekly, or monthly assessment throttles, report generation quotas, or trial countdown timers.
5. **Zero Secret Leakage**: Passwords are never stored in plaintext, never logged to stdout, never written to audit trails, and never returned in API payloads or AI prompts.

---

## 2. Credentials & Password Security

### Password Hashing Specification
- **Algorithm**: `PBKDF2` (Password-Based Key Derivation Function 2)
- **Hash Function**: `HMAC-SHA256`
- **Salt**: 16 bytes of cryptographically secure pseudorandom data generated via `secrets.token_bytes(16)`.
- **Iteration Count**: `100,000` iterations.
- **Storage Format**: `pbkdf2:sha256:100000$<salt_hex>$<hash_hex>`
- **Verification**: `hmac.compare_digest` (constant-time verification to prevent timing attacks).

### Sanitization & Logging Safeguards
All backend logging endpoints pass through `sanitize_log_dict()`. Keys containing sensitive terms (`password`, `token`, `secret`, `authorization`, `api_key`, `credentials`) are scrubbed before reaching disk logs or monitoring consoles.

---

## 3. Session & Token Management

- **Format**: JSON Web Tokens (`JWT` / RFC 7519) signed via `HS256`.
- **Expiry**: Default 1,440 minutes (24 hours), configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **Session Tracking**: Active sessions are persisted in the `user_sessions` database table, recording `session_token`, `ip_address`, `user_agent`, `created_at`, `expires_at`, and `is_active`.
- **Revocation**: Calling `/api/auth/logout` terminates the session in the database and revokes client-side tokens.

---

## 4. Role-Based Access Control (RBAC)

KAVACH 6.0 defines two primary roles:

| Role | Identifiers | Permissions & Capabilities |
| :--- | :--- | :--- |
| **DEVELOPER / OWNER** | `DEVELOPER_OWNER`, `admin` | Full system access: User creation, account activation/deactivation, password resets, activity inspection, feedback audit, system health, and all assessment/security modules. |
| **TEAM USER** | `TEAM_USER` | Access to the complete KAVACH 6.0 application: Command Center, System Health, Scope Guard, Discovery, 8-Stage Pipeline, Findings, AI Analysis, Knowledge Correlation, Evidence Validation, Risk Scoring, Remediation, Re-Verification, World Situational Monitor, Report/JSON Export, and Feedback. |

*Note: Frontend controls hide administration tabs for team users, but the backend strictly enforces RBAC at the API layer. Direct API requests from non-owners to `/api/admin/*` receive an immediate `403 Forbidden` response.*

---

## 5. Seeded Test Accounts

The following default accounts are seeded automatically on database initialization for validation and team testing:

| User ID | Role | Initial Password | Role Title / Assignment | Status |
| :--- | :--- | :--- | :--- | :--- |
| `ADMIN001` | `DEVELOPER_OWNER` | `Admin@Kavach2026!` | Security Lead & System Owner | Active |
| `TEAM001` | `TEAM_USER` | `Team@Kavach2026!` | Lead SecOps Analyst | Active |
| `TEAM002` | `TEAM_USER` | `Team@Kavach2026!` | AppSec Specialist | Active |
| `TEAM003` | `TEAM_USER` | `Team@Kavach2026!` | Remediation Engineer | Active |
| `TEAM004` | `TEAM_USER` | `Team@Kavach2026!` | Compliance Auditor | Active |
| `TEAM005` | `TEAM_USER` | `Team@Kavach2026!` | Threat Intelligence Analyst | Active |
| `TEAM006` | `TEAM_USER` | `Team@Kavach2026!` | Penetration Tester | Active |
| `TEAM007` | `TEAM_USER` | `Team@Kavach2026!` | Cloud Security Engineer | Active |
| `TEAM008` | `TEAM_USER` | `Team@Kavach2026!` | Forensics & Incident Responder | Active |
| `TEAM009` | `TEAM_USER` | `Team@Kavach2026!` | DevSecOps Engineer | Active |
| `TEAM010` | `TEAM_USER` | `Team@Kavach2026!` | Security Operations Analyst | Active |

---

## 6. Account Lifecycle Management API

### Authentication Endpoints
- `POST /api/auth/login`: Authenticates `user_id` and `password`. Returns JWT token, user object, and creates a session.
- `POST /api/auth/logout`: Invalidates the active session.
- `GET /api/auth/me`: Returns identity and role of current authenticated caller.
- `POST /api/auth/change-password`: Allows an authenticated user to change their password upon supplying their current password.

### Owner Administration Endpoints (Restricted to `DEVELOPER_OWNER`)
- `GET /api/admin/users`: Lists all provisioned accounts, their status, role, and last login.
- `POST /api/admin/users`: Creates a new team member with assigned `user_id`, initial password, and full name.
- `PUT /api/admin/users/{user_id}/status`: Activates or deactivates a user account.
- `POST /api/admin/users/{user_id}/reset-password`: Resets a team member's password.
