# KAVACH 6.0 — Safe Demo Lab Guide
**Non-Malicious Training Samples for SIH Hackathon Evaluation**

---

## 1. Safety Policy: Zero Malware

> **IMPORTANT**: KAVACH NEVER USES REAL MALWARE.  
> All demo samples are intentionally vulnerable, synthetic, non-malicious training artifacts designed exclusively for assessment verification.

Located under:
```
demo/training_samples/
├── demo_insecure_config.json
├── demo_api_keys.env
└── vulnerable_dependencies.txt
```

Every sample file contains a clear header label:
`KAVACH DEMO / TRAINING ARTIFACT - SAFE INTENTIONALLY VULNERABLE SYNTHETIC SAMPLE`

---

## 2. Walkthrough of Demo Artifacts

### 1. `demo_insecure_config.json`
- **Flaw**: Contains `"debug": true`, `"allow_insecure_transport": true`, and `"cors_allow_origins": ["*"]`.
- **Finding Generated**: `Insecure Application Configuration Flags Enabled` (CWE-16, A05:2021 Security Misconfiguration).
- **Evidence**: Verbatim JSON extract with cryptographic SHA-256 hash.
- **Terminal Verification**:
  ```powershell
  Get-Content -Path "demo/training_samples/demo_insecure_config.json" | ConvertFrom-Json | Select-Object debug, allow_insecure_transport
  ```

### 2. `demo_api_keys.env`
- **Flaw**: Contains synthetic dummy credentials (`AWS_ACCESS_KEY_ID=AKIA...`, `DATABASE_URL=postgres://...`).
- **Finding Generated**: `Exposed Secret Pattern: AWS Access Key ID` (CWE-798, A07:2021 Identification and Authentication Failures).
- **Evidence**: Verbatim string snippet, location, line count, and SHA-256 hash.
- **Terminal Verification**:
  ```powershell
  Get-Content -Path "demo/training_samples/demo_api_keys.env" | Select-String -Pattern "AKIA"
  ```

### 3. `vulnerable_dependencies.txt`
- **Flaw**: Outdated library package list (`urllib3==1.26.4`, `requests==2.25.1`, `pyyaml==5.3.1`).
- **Finding Generated**: Known CVE correlation matching CVE-2023-40217 and related package advisories.
- **Status Classification**: `CONFIRMED MATCH` (because exact version string is present).

---

## 3. Demonstration Script for SIH Judges

1. Open KAVACH and select **Portable (USB)** from the top navigation.
2. Show the **Consent & Permission Dashboard**:
   - Demonstrate unchecking "Files & Selected Folders".
   - Run scan $\rightarrow$ point out that KAVACH refuses to scan files and honestly reports `"Not scanned — permission not granted."`
3. Re-enable "Files & Selected Folders" and click **Use Safe Demo Lab Path**.
4. Click **Run Portable Assessment**:
   - Show instantaneous capture of authentic SHA-256 hashes.
   - Show the distinction between `DEMO DATA` and `REAL EVIDENCE`.
   - Show the safe PowerShell command. Click `[ Copy Command ]` and execute it in PowerShell to prove the output matches the Observed Result verbatim.
5. Emphasize the core USP:
   $$\text{Find} \longrightarrow \text{Prove} \longrightarrow \text{Understand} \longrightarrow \text{Verify} \longrightarrow \text{Fix}$$
