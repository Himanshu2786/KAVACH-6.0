"""
KAVACH 6.0 Desktop - Defensive Rule Engine.
Implements non-destructive inspection rules for secrets, double extensions, insecure configurations, and suspicious scripts.
"""

import re
import json
import os
from typing import List, Dict, Any, Optional
from core.scanner.scan_result import FileObservation

def mask_secret(value: str) -> str:
    """Redacts secret strings to prevent plaintext credential exposure in logs or UI."""
    if not value or len(value) <= 6:
        return "******"
    return value[:4] + "*" * (len(value) - 4)

# Regex Patterns for Exposed Credentials / Secrets
SECRET_PATTERNS = [
    {
        "id": "RULE-SEC-001",
        "name": "Hardcoded AWS Access Key ID",
        "regex": re.compile(r"(?i)(?:aws_access_key_id|aws_key)\s*[:=]\s*['\"]?(AKIA[0-9A-Z]{16})['\"]?"),
        "severity": "CRITICAL",
        "category": "Credential & Secret Exposure",
        "cwe_id": "CWE-798",
        "owasp_id": "A07:2021-Identification and Authentication Failures",
        "desc": "Plaintext AWS Access Key ID detected in configuration file or script.",
        "rem": "Remove hardcoded credentials and load keys securely using IAM Roles or AWS Secrets Manager."
    },
    {
        "id": "RULE-SEC-002",
        "name": "Hardcoded AWS Secret Access Key",
        "regex": re.compile(r"(?i)(?:aws_secret_access_key|aws_secret)\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?"),
        "severity": "CRITICAL",
        "category": "Credential & Secret Exposure",
        "cwe_id": "CWE-798",
        "owasp_id": "A07:2021-Identification and Authentication Failures",
        "desc": "Plaintext AWS Secret Access Key detected in local repository file.",
        "rem": "Rotate the exposed secret key immediately in the AWS console and remove from local file."
    },
    {
        "id": "RULE-SEC-003",
        "name": "Plaintext Production Database Password",
        "regex": re.compile(r"(?i)(?:prod_db_password|database_password|db_pass)\s*[:=]\s*['\"]?([^\r\n'\"]{6,})['\"]?"),
        "severity": "HIGH",
        "category": "Credential & Secret Exposure",
        "cwe_id": "CWE-256",
        "owasp_id": "A02:2021-Cryptographic Failures",
        "desc": "Plaintext production database password stored in local configuration fixture.",
        "rem": "Store database passwords in encrypted secret vaults and reference via environment variables."
    },
    {
        "id": "RULE-SEC-004",
        "name": "High-Entropy API Secret Token",
        "regex": re.compile(r"(?i)(?:api_secret|jwt_secret|stripe_secret_key|private_key)\s*[:=]\s*['\"]?([^\r\n'\"]{16,})['\"]?"),
        "severity": "HIGH",
        "category": "Credential & Secret Exposure",
        "cwe_id": "CWE-798",
        "owasp_id": "A07:2021-Identification and Authentication Failures",
        "desc": "High-entropy API token or signing key detected in unencrypted configuration file.",
        "rem": "Migrate secrets into secure secret storage and exclude config files from version control."
    }
]

# Dangerous Double Extensions (e.g., invoice.pdf.exe)
SUSPICIOUS_DOUBLE_EXTENSIONS = [
    ".pdf.exe", ".pdf.vbs", ".pdf.bat", ".pdf.cmd", ".docx.exe", ".docx.vbs",
    ".xlsx.exe", ".xlsx.bat", ".jpg.exe", ".png.exe", ".zip.exe", ".txt.vbs"
]

class RuleEngine:
    @staticmethod
    def inspect_filename_and_metadata(file_path: str, file_name: str, file_size: int, sha256: str) -> List[FileObservation]:
        """Analyzes file naming patterns and extensions without opening content."""
        observations = []
        name_lower = file_name.lower()
        
        # 1. Double Extension Check
        for ext in SUSPICIOUS_DOUBLE_EXTENSIONS:
            if name_lower.endswith(ext):
                observations.append(FileObservation(
                    rule_id="RULE-FILE-DOUBLE-EXT",
                    rule_name="Suspicious Disguised Double Extension",
                    category="File Masquerading & Execution Risk",
                    severity="HIGH",
                    description=f"File '{file_name}' utilizes a disguised double extension ({ext}) commonly employed in social engineering to disguise executables as documents.",
                    remediation="Verify the true file type and origin. Do not execute untrusted files with deceptive extensions.",
                    cwe_id="CWE-434",
                    owasp_id="A04:2021-Insecure Design",
                    file_path=file_path,
                    file_name=file_name,
                    file_size=file_size,
                    sha256=sha256,
                    redacted_snippet=f"Filename: {file_name} -> Disguised executable suffix: {ext}",
                    command=f'Get-Item -Path "{file_name}" | Select-Object Name, Extension, Length',
                    expected_output="Single legitimate document extension.",
                    observed_output=f"Deceptive double extension detected: {file_name}"
                ))
                break
                
        return observations

    @staticmethod
    def inspect_file_content(file_path: str, file_name: str, file_size: int, sha256: str) -> List[FileObservation]:
        """Performs safe static inspection of text-based files."""
        observations = []
        # Skip very large files (>10MB) for regex scans to ensure responsive performance
        if file_size > 10 * 1024 * 1024:
            return observations

        # Read safely as text
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return observations

        # 1. Check Secret Patterns
        for line_num, line in enumerate(lines, 1):
            for pat in SECRET_PATTERNS:
                match = pat["regex"].search(line)
                if match:
                    raw_val = match.group(1) if match.groups() else match.group(0)
                    masked_val = mask_secret(raw_val)
                    clean_line = line.replace(raw_val, masked_val).strip()
                    
                    cmd = f'Select-String -Path "{file_name}" -Pattern "{pat["name"].split()[-1]}"'
                    observations.append(FileObservation(
                        rule_id=pat["id"],
                        rule_name=pat["name"],
                        category=pat["category"],
                        severity=pat["severity"],
                        description=pat["desc"],
                        remediation=pat["rem"],
                        cwe_id=pat["cwe_id"],
                        owasp_id=pat["owasp_id"],
                        file_path=file_path,
                        file_name=file_name,
                        file_size=file_size,
                        sha256=sha256,
                        line_number=line_num,
                        redacted_snippet=f"Line {line_num}: {clean_line}",
                        command=cmd,
                        expected_output="No plaintext secret patterns present in file.",
                        observed_output=f"Line {line_num}: Pattern matched with value [{masked_val}]"
                    ))

        # 2. Check Insecure JSON Configuration (e.g. debug=true, root_login=true)
        if file_name.lower().endswith(".json") and file_size < 500 * 1024:
            try:
                content = "".join(lines)
                data = json.loads(content)
                if isinstance(data, dict):
                    if data.get("debug") is True or data.get("DEBUG") is True:
                        observations.append(FileObservation(
                            rule_id="RULE-CFG-DEBUG",
                            rule_name="Debug Mode Enabled in Configuration",
                            category="Security Misconfiguration",
                            severity="MEDIUM",
                            description="Application debug mode is explicitly set to true. Debug modes may expose stack traces, internal endpoints, and sensitive memory variables.",
                            remediation="Set 'debug': false in production configuration files.",
                            cwe_id="CWE-489",
                            owasp_id="A05:2021-Security Misconfiguration",
                            file_path=file_path,
                            file_name=file_name,
                            file_size=file_size,
                            sha256=sha256,
                            redacted_snippet='"debug": true',
                            command=f'Select-String -Path "{file_name}" -Pattern "debug"',
                            expected_output='"debug": false',
                            observed_output='"debug": true'
                        ))
                    if data.get("allow_root_login") is True or data.get("permit_root_login") is True:
                        observations.append(FileObservation(
                            rule_id="RULE-CFG-ROOT",
                            rule_name="Permit Root Login Enabled in Configuration",
                            category="Access Control & Privilege Management",
                            severity="HIGH",
                            description="Direct superuser/root authentication is enabled in server configuration.",
                            remediation="Disable root login ('permit_root_login': false) and enforce unprivileged user elevation (sudo).",
                            cwe_id="CWE-250",
                            owasp_id="A01:2021-Broken Access Control",
                            file_path=file_path,
                            file_name=file_name,
                            file_size=file_size,
                            sha256=sha256,
                            redacted_snippet='"allow_root_login": true',
                            command=f'Select-String -Path "{file_name}" -Pattern "root_login"',
                            expected_output='"permit_root_login": false',
                            observed_output='"allow_root_login": true'
                        ))
            except Exception:
                pass

        return observations
