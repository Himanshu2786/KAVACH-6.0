# KAVACH 6.0 — PERMISSION SYSTEM & HOST BOUNDARIES

> **Status**: `IMPLEMENTED + TESTED`  
> **Deployment Status**: `DEPLOYMENT READY` (Point-of-use prompting, realistic browser boundaries)

---

## 1. Architectural Philosophy

The KAVACH 6.0 Permission System governs how the web application requests, interprets, and responds to browser permissions and device boundaries.

### Guiding Principles
1. **No Login-Time Permission Barrage**: KAVACH never requests permissions upon logging in. Permissions are requested strictly at point-of-use when a user triggers an action that depends on them.
2. **Transparent Explanations**: Every permission request clearly explains *why* the permission is needed and *how* KAVACH uses it.
3. **Hard Denial Handling**: If a user denies a permission, the dependent feature is cleanly blocked or falls back to an offline mode with an explicit explanation. The application never assumes a button click implies permission.
4. **Honest Host Boundaries**: A web browser cannot inspect arbitrary operating system processes, local network sockets, or physical USB controllers on the client's machine. KAVACH never fabricates telemetry or claims to scan client hardware via remote JavaScript.

---

## 2. Permission Lifecycle & State Machine

Permissions progress through a deterministic state machine:

```
                  ┌─────────────────┐
                  │  NOT_REQUESTED  │
                  └────────┬────────┘
                           │ User triggers feature
                           ▼
                  ┌─────────────────┐
                  │ PERMISSION PROMPT│
                  └──────┬───┬──────┘
         User clicks Grant│   │User clicks Deny
                         │   ▼
                         │ ┌───────────────┐
                         │ │    DENIED     │ (Feature safely blocked)
                         │ └───────────────┘
                         ▼
        Browser API Request (navigator.permissions)
            ┌────────────┼────────────┐
            ▼            ▼            ▼
      ┌───────────┐┌───────────┐┌───────────────┐
      │  GRANTED  ││BLOCKED_BY_││  UNAVAILABLE  │
      │           ││  BROWSER  ││               │
      └───────────┘└───────────┘└───────────────┘
       (Feature     (Guided browser (Environment lacks
       executes)     settings help)  supported API)
```

### State Definitions
- `NOT_REQUESTED`: Initial default state before feature execution.
- `GRANTED`: The user confirmed via the modal and the browser native API granted access.
- `DENIED`: The user explicitly declined the request. The feature halts immediately.
- `BLOCKED_BY_BROWSER`: The browser itself (or site settings / enterprise policy) blocked access. The user is guided on how to enable it in browser settings.
- `UNAVAILABLE`: The browser or connection context (e.g. non-HTTPS, or unsupported browser API) cannot provide the requested feature.

---

## 3. Supported Browser Permissions

KAVACH 6.0 supports and prompts for real browser APIs where applicable:

| Permission | Feature Area | Rationale & Usage |
| :--- | :--- | :--- |
| **Notifications** | Assessment Pipeline & World Monitor | Used to deliver alerts when background 8-stage vulnerability scans complete or high-severity threat advisories are detected. |
| **Clipboard Read/Write** | Evidence Engine & Terminal Export | Used to securely copy reproducible cURL exploit commands, evidence tokens, and terminal logs to the user's clipboard. |
| **File Picker / Upload** | Local Evidence & Posture Ingestion | Used to allow teammates to voluntarily select local configuration files or log snippets for client-side evidence grounding. |
| **Geolocation** | Threat Map / Situational Monitor | Used to provide relative telemetry context on the World Threat Map if the user desires local perspective mapping. |

---

## 4. Remote Web Deployment vs. Host-Level Features

When KAVACH is accessed remotely through a web browser:

### Realistic Browser Boundaries
Browsers operate within a strict sandboxed security model:
- Remote JavaScript **cannot** query `ps aux` or Windows Process Manager on the user's laptop.
- Remote JavaScript **cannot** scan local listening TCP/UDP ports on `127.0.0.1` or the user's home LAN without triggering CORS/private network access blocks.
- Remote JavaScript **cannot** directly enumerate physical USB hardware without explicit WebUSB connection prompts.

### Honest UI Demarcation
When a teammate opens the **Local Posture** or **Host Scanner** module in web deployment mode:
- KAVACH displays an accurate status banner:
  > **Remote Browser Notice**: Host-level telemetry (local process scanning, listening port enumeration, and kernel USB inspection) is unavailable through a standard browser sandbox. To inspect host posture, run the local KAVACH agent or provide an exported system profile.
- Under **no circumstances** does KAVACH synthesize fake process lists or pretend to scan the user's private computer.
