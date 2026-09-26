# KAVACH 6.0 — TEAM ACTIVITY TRACKING & USAGE ANALYTICS

> **Status**: `IMPLEMENTED + TESTED`  
> **Deployment Status**: `DEPLOYMENT READY` (Deterministic tracking, privacy-conscious)

---

## 1. Objective & Purpose

The KAVACH 6.0 Activity Tracking system provides the developer/owner with clear, deterministic visibility into how team members utilize the application. It replaces opaque or speculative analytics with verifiable, event-driven evidence.

**Key Mandate**:
Activity tracking exists for diagnostic, audit, and team engagement insights. It is **never** used to impose artificial usage restrictions, quotas, or cooldowns.

---

## 2. Deterministic Usage Classification

Rather than simply recording logins or using probabilistic AI heuristics, KAVACH classifies team member participation into three deterministic usage tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USAGE TIER CLASSIFICATION                       │
├───────────────────┬────────────────────────────────────────────────────┤
│ 1. LOGIN ONLY     │ Authenticated into KAVACH but performed no         │
│                   │ product interactions beyond session initiation.    │
├───────────────────┼────────────────────────────────────────────────────┤
│ 2. ACTIVE USE     │ Navigated to and opened authenticated KAVACH 6.0   │
│                   │ functional modules (e.g. Command Center, History,  │
│                   │ System Health, World Situational Monitor).         │
├───────────────────┼────────────────────────────────────────────────────┤
│ 3. MEANINGFUL USE │ Executed core security operations:                 │
│                   │ - Initiated an 8-Stage Assessment                  │
│                   │ - Validated Evidence or reviewed Findings          │
│                   │ - Executed AI Hypothesis / RAG Analysis            │
│                   │ - Ran Risk Prioritization & Remediation Engine     │
│                   │ - Executed Terminal/Network Re-Verification        │
│                   │ - Exported Executive PDF or JSON Reports           │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

## 3. Deterministic Event Schema

Activity events are stored in the `user_activities` table with the following structured schema:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Auto-incrementing primary key. |
| `user_id` | String | Unique teammate identifier (e.g. `TEAM001`). |
| `event_type` | String | Standardized event enum string (see below). |
| `module` | String | Subsystem (e.g. `assessments`, `evidence`, `reporting`). |
| `status` | String | Execution outcome (`SUCCESS`, `FAILED`, `DENIED`). |
| `details` | String (JSON) | Sanitized event parameters (resource IDs, execution flags). |
| `timestamp` | DateTime | UTC timestamp of event occurrence. |

### Supported Event Types
- **Session**: `LOGIN`, `LOGOUT`, `SESSION_CREATED`, `SESSION_EXPIRED`
- **Navigation**: `PAGE_VIEWED`, `MODULE_OPENED`, `WORLD_MONITOR_VIEWED`
- **Assessment Lifecycle**: `ASSESSMENT_STARTED`, `ASSESSMENT_COMPLETED`
- **Security Engineering**: `FINDING_VIEWED`, `EVIDENCE_VIEWED`, `AI_ANALYSIS_EXECUTED`, `RISK_VIEWED`, `REMEDIATION_VIEWED`, `RETEST_EXECUTED`
- **Reporting**: `REPORT_VIEWED`, `REPORT_EXPORTED`, `JSON_EXPORTED`
- **Governance & Permissions**: `PERMISSION_REQUESTED`, `PERMISSION_GRANTED`, `PERMISSION_DENIED`, `FEEDBACK_SUBMITTED`, `ERROR_OCCURRED`

---

## 4. Privacy & Security Boundaries

1. **No Sensitive Data Logging**: Password strings, session tokens, CSRF tokens, authorization headers, and raw proprietary source files are strictly forbidden from event details.
2. **Sanitized Payload Ingestion**: The `/api/activity/log` endpoint runs incoming metadata through server-side sanitization filters.
3. **Data Isolation**: Team members can only view their own activity history. Only the developer/owner can view the cross-team activity timeline and analytics dashboard.

---

## 5. Owner Activity Dashboard

Accessible exclusively to `DEVELOPER_OWNER` accounts via the `/admin` route or the top navigation bar:

### Summary Table
Aggregates activity metrics across all provisioned teammates:
- **User ID & Full Name**
- **Last Active Timestamp**
- **Total Sessions**
- **Assessments Created**
- **Reports Exported**
- **Deterministic Usage Level** (`LOGIN ONLY`, `ACTIVE USE`, `MEANINGFUL USE`)

### Live Timeline View
Displays an chronological stream of actions with instant filtering:
```
TEAM001 | 09:30 UTC | LOGIN (SUCCESS)
TEAM001 | 09:35 UTC | MODULE_OPENED (Command Center)
TEAM001 | 09:41 UTC | ASSESSMENT_STARTED (Target: api.internal.org)
TEAM001 | 09:43 UTC | FINDING_VIEWED (Finding: KAV-SQLI-001)
TEAM001 | 09:47 UTC | AI_ANALYSIS_EXECUTED (Hypothesis generation)
TEAM001 | 09:52 UTC | RISK_VIEWED (CVSS 8.4)
TEAM001 | 10:01 UTC | REPORT_EXPORTED (PDF)
TEAM001 | 10:04 UTC | LOGOUT
```
