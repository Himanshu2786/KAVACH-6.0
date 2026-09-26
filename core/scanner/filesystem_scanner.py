"""
KAVACH 6.0 Desktop - Filesystem Scanner Orchestrator.
Recursively inspects files and folders, computing hashes, executing rule evaluations, and creating verifiable findings.
"""

import os
import time
import hashlib
from datetime import datetime, timezone
from typing import Callable, Optional, Dict, Any, List
from core.scanner.scan_result import ScanResult, FileObservation
from core.scanner.hash_analyzer import HashAnalyzer
from core.scanner.rule_engine import RuleEngine
from services.storage_service import storage

class FilesystemScanner:
    def __init__(self, on_progress: Optional[Callable[[int, str, int], None]] = None):
        """
        on_progress(scanned_count: int, current_file: str, findings_count: int)
        """
        self.on_progress = on_progress
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def scan_target(self, target_path: str, follow_symlinks: bool = False) -> ScanResult:
        """Executes defensive assessment on a single file or directory."""
        self.is_cancelled = False
        target_path = os.path.abspath(target_path)
        
        scan_id = f"SCAN-{int(time.time())}"
        start_time = datetime.now(timezone.utc).isoformat()
        
        if not os.path.exists(target_path):
            return ScanResult(
                scan_id=scan_id,
                target_path=target_path,
                is_directory=False,
                status="ERROR",
                error_message="Target path does not exist on the filesystem."
            )

        is_dir = os.path.isdir(target_path)
        result = ScanResult(
            scan_id=scan_id,
            target_path=target_path,
            is_directory=is_dir,
            start_time=start_time
        )
        
        t0 = time.time()
        observations: List[FileObservation] = []
        
        if not is_dir:
            # Single file scan
            obs = self._scan_single_file(target_path)
            observations.extend(obs)
            result.total_files_scanned = 1
        else:
            # Recursive directory scan
            for root, dirs, files in os.walk(target_path, followlinks=follow_symlinks):
                if self.is_cancelled:
                    result.status = "CANCELLED"
                    break
                    
                result.total_dirs_scanned += 1
                for fname in files:
                    if self.is_cancelled:
                        result.status = "CANCELLED"
                        break
                        
                    fpath = os.path.join(root, fname)
                    result.total_files_scanned += 1
                    
                    if self.on_progress:
                        self.on_progress(result.total_files_scanned, fname, len(observations))
                        
                    obs = self._scan_single_file(fpath)
                    observations.extend(obs)

        result.end_time = datetime.now(timezone.utc).isoformat()
        result.duration_seconds = round(time.time() - t0, 3)
        result.observations = observations
        
        # Convert observations to KAVACH findings and cryptographic evidence
        self._persist_results(result)
        
        return result

    def _scan_single_file(self, file_path: str) -> List[FileObservation]:
        """Safely analyzes a single file without executing it."""
        try:
            if not os.access(file_path, os.R_OK):
                return []
        except Exception:
            return []

        file_name = os.path.basename(file_path)
        size, sha256 = HashAnalyzer.get_file_metadata(file_path)
        
        obs = []
        # 1. Filename & Metadata rules
        obs.extend(RuleEngine.inspect_filename_and_metadata(file_path, file_name, size, sha256))
        # 2. Static Content rules
        obs.extend(RuleEngine.inspect_file_content(file_path, file_name, size, sha256))
        
        return obs

    def _persist_results(self, result: ScanResult):
        """Converts observations into structured SQLite findings, evidence, and audit logs."""
        asm_id = result.scan_id
        created_at = result.start_time
        
        findings = []
        evidence_list = []
        
        for idx, obs in enumerate(result.observations, 1):
            fnd_id = f"FND-FILE-{asm_id[-4:]}-{idx:02d}"
            ev_id = f"EV-FILE-{asm_id[-4:]}-{idx:02d}"
            
            # Evidence Integrity Hash calculation
            h_data = f"{obs.file_path}|{obs.sha256}|{obs.redacted_snippet}|{obs.command}"
            ev_hash = hashlib.sha256(h_data.encode('utf-8')).hexdigest()
            
            findings.append({
                "id": fnd_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "title": obs.rule_name,
                "category": obs.category,
                "severity": obs.severity,
                "cwe_id": obs.cwe_id,
                "owasp_id": obs.owasp_id,
                "confidence": "HIGH",
                "affected_component": obs.file_path,
                "description": obs.description,
                "remediation": obs.remediation,
                "status": "OPEN",
                "evidence_id": ev_id,
                "created_at": created_at
            })
            
            evidence_list.append({
                "id": ev_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "type": "FILE_INSPECTION",
                "data": {
                    "file_path": obs.file_path,
                    "file_name": obs.file_name,
                    "file_size": obs.file_size,
                    "sha256": obs.sha256,
                    "line_number": obs.line_number,
                    "redacted_snippet": obs.redacted_snippet
                },
                "integrity_hash": ev_hash,
                "command": obs.command,
                "expected_output": obs.expected_output,
                "observed_output": obs.observed_output,
                "verification_steps": [
                    f'Open PowerShell in directory: cd "{os.path.dirname(obs.file_path)}"',
                    f'Execute command: {obs.command}',
                    "Verify matching line output against OBSERVED RESULT."
                ],
                "created_at": created_at
            })

        asm_record = {
            "id": asm_id,
            "target_url": result.target_path,
            "name": f"File Security Assessment ({os.path.basename(result.target_path)})",
            "mode": "FILESYSTEM_AUDIT",
            "status": result.status,
            "created_at": created_at,
            "completed_at": result.end_time,
            "summary": f"Scanned {result.total_files_scanned} files across {result.total_dirs_scanned} directories in {result.duration_seconds}s. Identified {len(findings)} findings.",
            "metadata": {
                "files_scanned": result.total_files_scanned,
                "dirs_scanned": result.total_dirs_scanned,
                "findings_count": len(findings),
                "duration_seconds": result.duration_seconds
            }
        }
        
        storage.save_assessment(asm_record)
        storage.save_findings(findings)
        storage.save_evidence_list(evidence_list)
        
        # Log to Audit Trail
        storage.log_audit_event(
            "FILE_SCAN_COMPLETED",
            f"Completed secure scan of '{result.target_path}'. Scanned {result.total_files_scanned} files, {len(findings)} findings generated.",
            actor="Operator",
            details={
                "target": result.target_path,
                "files_scanned": result.total_files_scanned,
                "findings_count": len(findings),
                "scan_id": asm_id
            }
        )
