# KAVACH 6.0 — Portable Windows Security Assessment Guide (USB Edition)

---

## 1. Overview & Architecture

KAVACH 6.0 introduces a standalone, portable Windows assessment engine designed to run seamlessly from any USB flash drive or local folder without installation.

```
USER INSERTS USB
      ↓
USER MANUALLY LAUNCHES KAVACH.EXE
      ↓
CONSENT / PERMISSION DASHBOARD
      ↓
USER SELECTS WHAT TO ALLOW
      ↓
KAVACH COLLECTS ONLY FROM APPROVED CATEGORIES
      ↓
DETERMINISTIC SECURITY ASSESSMENT
      ↓
REAL EVIDENCE (SHA-256 HASHED)
      ↓
VALIDATION & CWE / OWASP CORRELATION
      ↓
AI EXPLANATION & SUMMARY
      ↓
SAFE REPRODUCIBLE TERMINAL VERIFICATION
      ↓
REMEDIATION & RE-VERIFICATION
```

---

## 2. Windows Security & Non-Elevation Mandate

KAVACH operates under strict adherence to the Microsoft Windows security model:
- **No UAC Bypass**: KAVACH will never attempt stealthy or unauthorized privilege elevation.
- **No Silent Persistence**: KAVACH does not install services, schedule tasks, or register autorun keys.
- **No USB Autorun**: KAVACH executes solely when launched explicitly by the user.
- **No Process Hiding**: All inspection processes run transparently in user space.
- **No Security Software Interference**: KAVACH does not disable Windows Defender or modify firewall rules.

If a specific inspection requires administrative permissions, KAVACH transparently prompts the user through standard Windows mechanisms.

---

## 3. How to Build and Run from USB

### Building `dist/KAVACH.exe`:
Run the automated build script:
```cmd
build_portable.bat
```
This produces `dist/KAVACH.exe`.

### Running from USB:
1. Copy `KAVACH.exe` into your USB drive root (e.g. `E:\KAVACH.exe`).
2. Insert the USB drive into the target Windows audit workstation.
3. Double-click `KAVACH.exe`.
4. KAVACH automatically starts its local loopback server on `http://127.0.0.1:8000` and opens the default browser to the **Consent & Permission Dashboard**.

---

## 4. What KAVACH Scans vs. Does Not Scan

| Category | What KAVACH Scans | What KAVACH Does NOT Scan |
|---|---|---|
| **Files** | Only user-specified folders, dependency files, secret patterns, and configs. | System root, other users' private files, or encrypted volumes without permission. |
| **Processes** | Process PID, executable path, temp directory execution, unquoted paths. | Process memory injection or intrusive DLL hooks. |
| **Installed Software** | Registry uninstall keys, version identification, CVE correlation. | Third-party binary reverse engineering or binary unpacking. |
| **Startup Items** | Registry Run keys and user startup shortcuts. | Bootloader modifications or low-level firmware. |
| **Network** | Local network adapter IP addresses and listening TCP/UDP ports. | External port scanning or denial-of-service traffic. |
| **System Security** | Read-only inspection of UAC EnableLUA, Defender, and Firewall profiles. | Automatic reconfiguration or policy changes. |

---

## 5. Terminal Verification ("Verify It Yourself")

For every local finding, KAVACH provides a safe, copyable PowerShell command:
- **Registry Check**: `Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"`
- **Listening Ports**: `Get-NetTCPConnection -State Listen | Where-Object LocalAddress -eq '0.0.0.0'`
- **File Integrity**: `Get-FileHash -Path "..." -Algorithm SHA256`
- **Process Context**: `Get-Process -Id <PID> | Select-Object Id, ProcessName, Path`

All commands are strictly read-only and non-destructive.
