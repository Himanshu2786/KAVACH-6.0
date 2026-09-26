# KAVACH 6.0: The 3 Real Security Detections

This document records the exact **Expected vs. Actual results**, **Cryptographic Evidence IDs**, and **End-to-End Lifecycle Status** for the 3 Real Security Detections in KAVACH 6.0.

---

## Detection 1: Web Security (Missing Observable Security Configuration)

### 1. Workflow
```
Target URL (http://127.0.0.1:8000)
    ↓
Safe HTTP & TLS Probing (UrlScannerService)
    ↓
Real Header & Handshake Observation
    ↓
Cryptographic SHA-256 Evidence Hashing
    ↓
Deterministic Rule Finding (FIND-WEB-001)
    ↓
Simple Explanation & Technical Evidence
    ↓
Actionable Remediation Guidance
    ↓
Differential Re-verification
```

### 2. Forensic Execution Record
- **Target:** `http://127.0.0.1:8000`
- **Scanner:** `UrlScannerService` (Async HTTP/TLS non-destructive probe)
- **Rule ID:** `WEB-HTTPS-REQUIRED` & `WEB-HEADER-HSTS`
- **CWE / OWASP:** CWE-319 / A02:2021-Cryptographic Failures
- **Evidence ID:** `EVD-WEB-001`
- **Integrity Hash (SHA-256):** `1f8d8359daea6b50d97f90a1b00b00d29002ac61b0588a7bb73d36c0ee04107d`
- **Expected:** Website accepts HTTPS connections on port 443 with HSTS and CSP headers.
- **Actual:** Connection refused on port 443; Strict-Transport-Security and Content-Security-Policy headers omitted.
- **Simple Explanation:** Plaintext HTTP connection does not enforce encrypted HTTPS transport, leaving user sessions vulnerable to network interception.
- **Technical Evidence:** Target: `https://127.0.0.1`, Protocol: `TCP / TLS:443`, Observed: `Connection refused / handshake failure`.
- **Terminal Verification:** `curl -I -v https://127.0.0.1`
- **Remediation:** Bind port 443 with a valid TLS certificate and configure reverse proxy (Nginx) with `return 301 https://$host$request_uri;`.
- **Re-verification Result:** Passed via `POST /api/url-check/re-verify`.
- **Status:** **WORKING (CONFIRMED)**

---

## Detection 2: Network Exposure (Listening Network Service Assessment)

### 1. Workflow
```
Operating System Network Table Inspection (psutil)
    ↓
Active TCP Listening Socket Identification
    ↓
Process Association & PID Resolution
    ↓
Cryptographic SHA-256 Socket Evidence Hashing
    ↓
Non-Vulnerability Calibration ("Service Exposure Detected")
    ↓
Risk Context Rationale (Needs Review)
    ↓
Remediation Guidance
```

### 2. Forensic Execution Record
- **Target:** `127.0.0.1:8000` (Localhost listener)
- **Scanner:** `NetworkScanner` (OS kernel socket reader)
- **Process Associated:** `python.exe` (PID: verified via OS)
- **Rule ID:** `NET-SERVICE-EXPOSURE-CALIBRATED`
- **CWE / OWASP:** CWE-200 / A05:2021-Security Misconfiguration
- **Evidence ID:** `EVD-NET-001`
- **Integrity Hash (SHA-256):** `197cf70868f18cb6c7fa82f42a1ef24a15a815a5105260195c80efcebf5a5c68`
- **Expected:** Calibrated assessment reporting that an open port is not automatically a vulnerability.
- **Actual:** Title generated: `"Service Exposure Detected: Application Development Listener (Port 8000)"`, Status: `"NEEDS REVIEW"`.
- **Simple Explanation:** An active network listening service was detected on port 8000. A listening port does not automatically mean a vulnerability exists; it indicates an active service waiting for inbound connections.
- **Technical Evidence:** Protocol: `TCP`, Local Address: `127.0.0.1`, Port: `8000`, Connection State: `LISTEN`, Process: `python.exe`.
- **Terminal Verification:** `Get-NetTCPConnection -State Listen -LocalPort 8000 | Select-Object LocalAddress, LocalPort, OwningProcess`
- **Remediation:** If the service is intended for local development only, bind exclusively to loopback (`127.0.0.1`) and enforce host-based firewall filters.
- **Status:** **WORKING (CONFIRMED EXPOSURE / NEEDS REVIEW)**

---

## Detection 3: Suspicious File Indicator (Deceptive Double Extension)

### 1. Workflow
```
File System Observation (User-Authorized Directory)
    ↓
File Metadata Extraction (os.stat, size, timestamps)
    ↓
Cryptographic SHA-256 Hash Computation
    ↓
Double Extension Pattern Match (*.pdf.exe)
    ↓
Finding Generation (FIND-FILE-001)
    ↓
Simple Explanation & Technical Evidence
    ↓
Remediation & PowerShell Verification
```

### 2. Forensic Execution Record
- **Target:** `demo/training_samples/suspicious_invoice.pdf.exe`
- **Scanner:** `FileScanner` (Static metadata and indicator analyzer)
- **Rule ID:** `FILE-SUSPICIOUS-DOUBLE-EXTENSION`
- **CWE / OWASP:** CWE-1007 / A08:2021-Software and Data Integrity Failures
- **Evidence ID:** `EVD-FILE-001`
- **Integrity Hash (SHA-256):** `01b22e1b12b509f6d4d1681283626ea14b5ea6b39d1b643a6d96a7aa8021c3b2`
- **Expected:** Detection of deceptive double extension masquerading an executable as a document.
- **Actual:** Title generated: `"Suspicious File Indicator: Double Extension Detected (suspicious_invoice.pdf.exe)"`, Severity: `HIGH`, Status: `CONFIRMED`.
- **Simple Explanation:** A file with a deceptive double extension (`.pdf.exe`) was detected. Standard file browsers often hide the final extension, leading users to believe they are opening a safe document when they are running arbitrary code.
- **Technical Evidence:** File Path: `demo/training_samples/suspicious_invoice.pdf.exe`, File Size: `218 bytes`, Disguised: `.pdf`, Executable: `.exe`, SHA-256 verified.
- **Terminal Verification:** `Get-Item -Path "demo/training_samples/suspicious_invoice.pdf.exe" | Select-Object Name, Extension, Length, LastWriteTime`
- **Remediation:** Delete or quarantine the disguised file. Ensure "File name extensions" is enabled in Windows Explorer settings.
- **Status:** **WORKING (CONFIRMED)**

---

## Test Verification Summary
All 3 detections are covered by automated unit tests in `backend/tests/test_three_real_detections.py` and pass 100% of test assertions.
