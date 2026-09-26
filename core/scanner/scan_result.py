"""
KAVACH 6.0 Desktop - Structured Scan Models.
Defines data structures for file observations, findings, cryptographic evidence, and overall scan results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

@dataclass
class FileObservation:
    rule_id: str
    rule_name: str
    category: str
    severity: str
    description: str
    remediation: str
    cwe_id: str
    owasp_id: str
    file_path: str
    file_name: str
    file_size: int
    sha256: str
    line_number: Optional[int] = None
    redacted_snippet: str = ""
    command: str = ""
    expected_output: str = ""
    observed_output: str = ""

@dataclass
class ScanResult:
    scan_id: str
    target_path: str
    is_directory: bool
    total_files_scanned: int = 0
    total_dirs_scanned: int = 0
    skipped_files: int = 0
    permission_failures: int = 0
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    observations: List[FileObservation] = field(default_factory=list)
    status: str = "COMPLETED"
    error_message: Optional[str] = None
