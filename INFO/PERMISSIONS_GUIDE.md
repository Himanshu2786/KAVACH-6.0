# KAVACH 6.0 — Consent & Permission Dashboard Guide

---

## 1. Zero-Collection Principle

> **"If permission is denied: NO COLLECTION, NO SCANNING, NO FAKE RESULTS."**

When a user unchecks any permission on the Consent Dashboard, KAVACH:
1. Skips invoking the corresponding scanner module completely.
2. Does not query the Windows Registry, filesystem, process table, or network stack for that category.
3. Outputs an honest status banner: `"Not scanned — permission not granted."`
4. Never invents simulated findings or claims zero risk.

---

## 2. Permission Categories Breakdown

### 1. Files & Selected Folders (`files`)
- **What KAVACH Accesses**: Only the directory or files explicitly specified in the audit target input.
- **Why It Is Needed**: Scans files for hardcoded API keys, exposed database passwords, debug configurations, and outdated dependency manifests.
- **Checks Enabled**: SHA-256 hash generation, secret pattern matching (AWS tokens, private keys, database URLs), configuration flaw detection.
- **If Denied**: No file reads occur.

### 2. Running Processes (`processes`)
- **What KAVACH Accesses**: Queries the running process table via standard user-space APIs (PID, executable path, process name).
- **Why It Is Needed**: Identifies binaries executing from unquoted paths or temporary/user-writable directories (`%TEMP%`).
- **Checks Enabled**: Writable temp directory execution, unquoted service paths.
- **If Denied**: Process table is not inspected.

### 3. Installed Applications (`installed_apps`)
- **What KAVACH Accesses**: Reads Windows Registry Uninstall keys (`HKLM` and `HKCU`).
- **Why It Is Needed**: Catalogs application versions to check against local offline CVE/CWE vulnerability intelligence.
- **Checks Enabled**: Version identification, known CVE correlation (`CONFIRMED MATCH`, `POSSIBLE MATCH`, `VERSION UNKNOWN`).
- **If Denied**: Software registry keys are not queried.

### 4. Startup Items (`startup_items`)
- **What KAVACH Accesses**: Inspects user and system startup folders (`Start Menu\Programs\Startup`) and Registry Run keys.
- **Why It Is Needed**: Checks for unquoted executable paths or persistence shortcuts pointing to non-existent binaries.
- **Checks Enabled**: Unquoted autorun paths, missing executable targets.
- **If Denied**: Startup folders and registry keys are not inspected.

### 5. Network Information (`network`)
- **What KAVACH Accesses**: Reads local network interface addresses and active TCP/UDP listening ports.
- **Why It Is Needed**: Detects unencrypted services bound to wildcard addresses (`0.0.0.0` or `::`).
- **Checks Enabled**: Cleartext listener detection (HTTP, Telnet, unauthenticated database ports).
- **If Denied**: Sockets and network adapters are not inspected.

### 6. System Security Configuration (`system_security`)
- **What KAVACH Accesses**: Reads the `EnableLUA` registry value for UAC, Windows Firewall profile state, and Defender status.
- **Why It Is Needed**: Verifies that basic host guardrails are enabled.
- **Checks Enabled**: UAC active state, Firewall standard profile active state.
- **If Denied**: Host security settings are not inspected.
