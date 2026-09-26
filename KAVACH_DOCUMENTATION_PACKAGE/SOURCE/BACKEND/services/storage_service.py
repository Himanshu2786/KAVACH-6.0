"""
KAVACH 6.0 Desktop - Local SQLite Storage Service.
Provides persistent tamper-evident storage for assessments, findings, evidence, audit trail, risk records, and team notes.
Supports assessment isolation, deterministic CVSS 3.1 risk records, and structured business impacts.
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.config import get_database_path


class StorageService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_database_path()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Assessments Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id TEXT PRIMARY KEY,
                target_url TEXT NOT NULL,
                name TEXT NOT NULL,
                mode TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                summary TEXT,
                metadata_json TEXT
            )
            """)

            # Findings Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                assessment_id TEXT NOT NULL,
                finding_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                base_severity TEXT DEFAULT 'MEDIUM',
                priority TEXT DEFAULT 'MEDIUM',
                priority_score REAL DEFAULT 5.0,
                evidence_status TEXT DEFAULT 'NONE',
                cwe_id TEXT,
                owasp_id TEXT,
                confidence TEXT NOT NULL,
                affected_component TEXT NOT NULL,
                description TEXT NOT NULL,
                remediation TEXT NOT NULL,
                status TEXT NOT NULL,
                evidence_id TEXT,
                evidence_ids_json TEXT,
                cvss_score REAL,
                cvss_vector TEXT,
                reproduction_steps_json TEXT,
                safe_poc TEXT,
                business_impact TEXT,
                business_impact_json TEXT,
                technical_impact TEXT,
                calculation_factors_json TEXT,
                verification_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments (id)
            )
            """)

            # Evidence Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                assessment_id TEXT NOT NULL,
                finding_id TEXT NOT NULL,
                type TEXT NOT NULL,
                data_json TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                command TEXT,
                expected_output TEXT,
                observed_output TEXT,
                verification_steps_json TEXT,
                simple_explanation TEXT,
                technical_explanation_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments (id)
            )
            """)

            # Risk Records Table (Priority 2 Finding-Specific Risk & CVSS 3.1)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_records (
                id TEXT PRIMARY KEY,
                assessment_id TEXT NOT NULL,
                finding_id TEXT NOT NULL,
                cvss_version TEXT NOT NULL,
                cvss_score REAL NOT NULL,
                cvss_vector TEXT NOT NULL,
                severity TEXT NOT NULL,
                attack_vector TEXT NOT NULL,
                attack_complexity TEXT NOT NULL,
                privileges_required TEXT NOT NULL,
                user_interaction TEXT NOT NULL,
                scope TEXT NOT NULL,
                confidentiality_impact TEXT NOT NULL,
                integrity_impact TEXT NOT NULL,
                availability_impact TEXT NOT NULL,
                calculation_factors_json TEXT NOT NULL,
                business_impact_json TEXT NOT NULL,
                affected_assets_json TEXT NOT NULL,
                confidence TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments (id),
                FOREIGN KEY (finding_id) REFERENCES findings (id)
            )
            """)

            # Auto-migrate assessments columns if DB existed from earlier versions
            cursor.execute("PRAGMA table_info(assessments)")
            asm_cols = {row["name"] for row in cursor.fetchall()}
            asm_new_cols = {
                "name": "TEXT",
                "target_url": "TEXT",
                "mode": "TEXT DEFAULT 'HYBRID'",
                "status": "TEXT DEFAULT 'COMPLETED'",
                "created_at": "TEXT",
                "completed_at": "TEXT",
                "summary": "TEXT",
                "metadata_json": "TEXT",
                "progress": "INTEGER DEFAULT 100",
                "current_stage": "TEXT DEFAULT 'COMPLETE'",
                "scope": "TEXT DEFAULT 'Full Application'",
                "description": "TEXT DEFAULT ''",
                "environment": "TEXT DEFAULT 'Testing Environment'",
                "is_demo": "BOOLEAN DEFAULT 0",
                "assessment_type": "TEXT DEFAULT 'GENERIC_ASSESSMENT'",
                "parent_assessment_id": "TEXT"
            }
            for col, col_type in asm_new_cols.items():
                if col not in asm_cols:
                    try:
                        cursor.execute(f"ALTER TABLE assessments ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Auto-migrate findings columns if DB existed from earlier versions
            cursor.execute("PRAGMA table_info(findings)")
            f_cols = {row["name"] for row in cursor.fetchall()}
            f_new_cols = {
                "finding_id": "TEXT",
                "severity": "TEXT DEFAULT 'MEDIUM'",
                "confidence": "TEXT DEFAULT 'HIGH'",
                "remediation": "TEXT DEFAULT ''",
                "cwe_id": "TEXT DEFAULT ''",
                "owasp_id": "TEXT DEFAULT ''",
                "evidence_id": "TEXT",
                "evidence_ids_json": "TEXT",
                "cvss_score": "REAL DEFAULT 5.0",
                "cvss_vector": "TEXT",
                "reproduction_steps_json": "TEXT",
                "safe_poc": "TEXT",
                "business_impact": "TEXT",
                "business_impact_json": "TEXT",
                "technical_impact": "TEXT",
                "calculation_factors_json": "TEXT",
                "verification_json": "TEXT",
                "file": "TEXT",
                "line": "INTEGER",
                "symbol_or_function": "TEXT",
                "code_pattern": "TEXT",
                "security_relevance": "TEXT",
                "detector": "TEXT",
                "runtime_validation_status": "TEXT",
                "source_details_json": "TEXT",
                "created_at": "TEXT",
                "updated_at": "TEXT"
            }
            for col, col_type in f_new_cols.items():
                if col not in f_cols:
                    try:
                        cursor.execute(f"ALTER TABLE findings ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Auto-migrate evidence columns if DB existed from earlier versions
            cursor.execute("PRAGMA table_info(evidence)")
            e_cols = {row["name"] for row in cursor.fetchall()}
            e_new_cols = {
                "simple_explanation": "TEXT",
                "technical_explanation_json": "TEXT",
                "integrity_hash": "TEXT",
                "command": "TEXT",
                "expected_output": "TEXT",
                "observed_output": "TEXT",
                "verification_steps_json": "TEXT",
                "created_at": "TEXT"
            }
            for col, col_type in e_new_cols.items():
                if col not in e_cols:
                    try:
                        cursor.execute(f"ALTER TABLE evidence ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Auto-migrate audit_events columns if DB existed from earlier versions
            cursor.execute("PRAGMA table_info(audit_events)")
            aud_cols = {row["name"] for row in cursor.fetchall()}
            aud_new_cols = {
                "timestamp": "TEXT",
                "event_type": "TEXT DEFAULT 'CORE_EVENT'",
                "actor": "TEXT DEFAULT 'SYSTEM'",
                "action": "TEXT DEFAULT 'EXECUTED'",
                "description": "TEXT DEFAULT ''",
                "details_json": "TEXT DEFAULT '{}'",
                "metadata_json": "TEXT DEFAULT '{}'",
                "module": "TEXT DEFAULT 'CORE'",
                "prev_hash": "TEXT",
                "event_hash": "TEXT",
                "assessment_id": "TEXT",
                "finding_id": "TEXT",
                "object": "TEXT",
                "status": "TEXT DEFAULT 'SUCCESS'",
                "result": "TEXT DEFAULT 'SUCCESS'",
                "evidence_ref": "TEXT",
                "evidence_id": "TEXT",
                "hash": "TEXT"
            }
            for col, col_type in aud_new_cols.items():
                if col not in aud_cols:
                    try:
                        cursor.execute(f"ALTER TABLE audit_events ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            # Experience DB (False Positive Suppressions)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS experience_db (
                id TEXT PRIMARY KEY,
                finding_signature TEXT NOT NULL,
                finding_id TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                target_pattern TEXT NOT NULL,
                rationale TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            # Audit Trail (Tamper-evident chain)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                description TEXT DEFAULT '',
                details_json TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}',
                module TEXT DEFAULT 'CORE',
                prev_hash TEXT,
                event_hash TEXT NOT NULL,
                assessment_id TEXT,
                finding_id TEXT,
                object TEXT,
                status TEXT DEFAULT 'SUCCESS',
                result TEXT,
                evidence_ref TEXT,
                evidence_id TEXT,
                hash TEXT
            )
            """)

            # Team Desk Notes & Assignments
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_findings (
                finding_id TEXT PRIMARY KEY,
                assigned_to TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                team_notes TEXT,
                updated_at TEXT NOT NULL
            )
            """)

            # Controlled Test Suites History
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id TEXT PRIMARY KEY,
                suite_id TEXT NOT NULL,
                suite_name TEXT NOT NULL,
                status TEXT NOT NULL,
                output TEXT NOT NULL,
                executed_at TEXT NOT NULL
            )
            """)

            conn.commit()

    def log_audit_event(
        self,
        event_type: str,
        action: str,
        actor: str = "Operator",
        assessment_id: Optional[str] = None,
        object_name: Optional[str] = None,
        result: str = "SUCCESS",
        evidence_ref: Optional[str] = None,
        hash_val: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        finding_id: Optional[str] = None
    ) -> str:
        """
        Appends a cryptographically chained audit log entry for complete reproducibility.
        Guarantees all 8 required fields: timestamp, assessment_id, actor, action, object, result, evidence_ref, hash.
        """
        details_map = dict(details or {})
        
        # Extract from details map if not provided in keyword args
        asm_id = assessment_id or details_map.get("assessment_id") or "GLOBAL"
        obj_name = object_name or details_map.get("object") or details_map.get("target") or "SYSTEM"
        res_val = result or details_map.get("result") or "SUCCESS"
        ev_ref = evidence_ref or details_map.get("evidence_ref") or details_map.get("evidence_id") or ""
        h_val = hash_val or details_map.get("hash") or details_map.get("integrity_hash") or ""

        # Finding ID resolution: For assessment-level events, finding_id must be None unless a real finding is involved
        fnd_id = finding_id or details_map.get("finding_id")
        if not fnd_id:
            if event_type in ("FINDING_CREATED", "POC_EXECUTED", "FINDING_UPDATED", "FINDING_VERIFIED", "RE_VERIFICATION_ATTEMPT"):
                if obj_name and obj_name != asm_id:
                    fnd_id = obj_name
            else:
                fnd_id = None

        # Update details map with explicit fields
        details_map["assessment_id"] = asm_id
        if fnd_id:
            details_map["finding_id"] = fnd_id
        elif "finding_id" in details_map and event_type in ("ASSESSMENT_STARTED", "TARGET_SELECTED"):
            details_map.pop("finding_id", None)
        details_map["object"] = obj_name
        details_map["result"] = res_val
        details_map["evidence_ref"] = ev_ref
        details_map["hash"] = h_val

        details_json = json.dumps(details_map, sort_keys=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Check schema of audit_events table
            cursor.execute("PRAGMA table_info(audit_events)")
            cols_info = {row["name"]: row["type"] for row in cursor.fetchall()}
            
            cursor.execute("SELECT event_hash FROM audit_events WHERE event_hash IS NOT NULL AND event_hash != '' ORDER BY rowid DESC LIMIT 1")
            last_row = cursor.fetchone()
            prev_hash = last_row["event_hash"] if last_row and last_row["event_hash"] else "GENESIS_HASH_KAVACH_5.0"
            
            payload = f"{timestamp}|{asm_id}|{event_type}|{actor}|{action}|{obj_name}|{res_val}|{details_json}|{prev_hash}"
            event_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
            event_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{event_hash[:6]}"
            
            # If id column is integer autoincrement in existing db, let sqlite auto-increment
            id_type = cols_info.get("id", "TEXT").upper()
            if "INT" in id_type:
                cursor.execute("""
                INSERT INTO audit_events (
                    timestamp, event_type, actor, action, description, details_json, metadata_json,
                    module, prev_hash, event_hash, assessment_id, finding_id, object, status, result,
                    evidence_ref, evidence_id, hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp, event_type, actor, action, action, details_json, details_json,
                    details_map.get("module", "CORE"), prev_hash, event_hash, asm_id, fnd_id, obj_name, res_val, res_val,
                    ev_ref, ev_ref, h_val
                ))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO audit_events (
                    id, timestamp, event_type, actor, action, description, details_json, metadata_json,
                    module, prev_hash, event_hash, assessment_id, finding_id, object, status, result,
                    evidence_ref, evidence_id, hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id, timestamp, event_type, actor, action, action, details_json, details_json,
                    details_map.get("module", "CORE"), prev_hash, event_hash, asm_id, fnd_id, obj_name, res_val, res_val,
                    ev_ref, ev_ref, h_val
                ))
            conn.commit()
            return event_id

    def get_audit_events(self, assessment_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if assessment_id:
                cursor.execute("""
                SELECT * FROM audit_events 
                WHERE assessment_id = ? OR details_json LIKE ? OR metadata_json LIKE ?
                ORDER BY rowid DESC LIMIT ?
                """, (assessment_id, f'%"{assessment_id}"%', f'%"{assessment_id}"%', limit))
            else:
                cursor.execute("SELECT * FROM audit_events ORDER BY rowid DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            events = []
            for r in rows:
                item = dict(r)
                item["details"] = json.loads(item.get("details_json") or item.get("metadata_json") or "{}")
                if not item.get("assessment_id") and "assessment_id" in item["details"]:
                    item["assessment_id"] = item["details"]["assessment_id"]
                if not item.get("object") and "object" in item["details"]:
                    item["object"] = item["details"]["object"]
                if not item.get("result") and "result" in item["details"]:
                    item["result"] = item["details"]["result"]
                if not item.get("evidence_ref") and "evidence_ref" in item["details"]:
                    item["evidence_ref"] = item["details"]["evidence_ref"]
                if not item.get("hash") and "hash" in item["details"]:
                    item["hash"] = item["details"]["hash"]
                events.append(item)
            return events

    def save_assessment(self, assessment: Dict[str, Any]):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            asm_id = assessment["id"]
            name = assessment.get("name") or f"Assessment {asm_id}"
            target_url = assessment.get("target_url") or "http://localhost:8000"
            created_at = assessment.get("created_at") or datetime.now(timezone.utc).isoformat()
            completed_at = assessment.get("completed_at") or created_at
            status = assessment.get("status", "COMPLETED")
            mode = assessment.get("mode", "HYBRID")
            summary = assessment.get("summary", "")
            assessment_type = assessment.get("assessment_type", "GENERIC_ASSESSMENT")
            parent_assessment_id = assessment.get("parent_assessment_id")
            meta_json = json.dumps(assessment.get("metadata", {}))

            cursor.execute("""
            INSERT OR REPLACE INTO assessments (
                id, target_url, name, mode, status, created_at, started_at, completed_at, summary, metadata_json,
                progress, current_stage, scope, description, environment, is_demo, assessment_type, parent_assessment_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asm_id,
                target_url,
                name,
                mode,
                status,
                created_at,
                created_at,
                completed_at,
                summary,
                meta_json,
                100,
                "COMPLETE",
                "Full Application",
                summary,
                "Testing Environment",
                0,
                assessment_type,
                parent_assessment_id
            ))
            conn.commit()

    def save_findings(self, findings: List[Dict[str, Any]]):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            for f in findings:
                ev_ids = f.get("evidence_ids", [f.get("evidence_id")] if f.get("evidence_id") else [])
                repro = f.get("reproduction_steps", [])
                verif = f.get("verification", {})
                b_imp = f.get("business_impact", "")
                b_imp_str = json.dumps(b_imp) if isinstance(b_imp, dict) else str(b_imp)
                calc_factors = f.get("calculation_factors", {})
                source_details = {
                    "what_code_caused_problem": f.get("what_code_caused_problem", {}),
                    "what_happened_at_runtime": f.get("what_happened_at_runtime", {}),
                    "what_evidence_proves_it": f.get("what_evidence_proves_it", {}),
                    "what_is_the_impact": f.get("what_is_the_impact", {}),
                    "how_should_it_be_fixed": f.get("how_should_it_be_fixed", {})
                }
                base_sev = f.get("base_severity") or f.get("severity", "MEDIUM")
                sev = f.get("severity") or f.get("base_severity", "MEDIUM")
                p_tier = f.get("priority") or sev
                p_score = float(f.get("cvss_score", f.get("priority_score", 5.0)))
                ev_status = f.get("evidence_status") or ("VERIFIED" if f.get("status") == "CONFIRMED" else ("AVAILABLE" if ev_ids else "NONE"))
                cursor.execute("""
                INSERT OR REPLACE INTO findings (
                    id, assessment_id, finding_id, title, category, severity, base_severity, priority, priority_score, evidence_status, cwe_id, owasp_id,
                    confidence, affected_component, description, remediation, status, evidence_id,
                    evidence_ids_json, cvss_score, cvss_vector, reproduction_steps_json, safe_poc,
                    business_impact, business_impact_json, technical_impact, calculation_factors_json,
                    verification_json, file, line, symbol_or_function, code_pattern,
                    security_relevance, detector, runtime_validation_status, source_details_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f.get("finding_id") or f["id"],
                    f["assessment_id"],
                    f.get("finding_id") or f["id"],
                    f["title"],
                    f["category"],
                    sev,
                    base_sev,
                    p_tier,
                    p_score,
                    ev_status,
                    f.get("cwe") or f.get("cwe_id", ""),
                    f.get("owasp_mapping") or f.get("owasp_id", ""),
                    f.get("confidence", "HIGH"),
                    f.get("affected_component", ""),
                    f.get("description", ""),
                    f.get("remediation", ""),
                    f.get("status", "OPEN"),
                    f.get("evidence_id", ev_ids[0] if ev_ids else ""),
                    json.dumps(ev_ids),
                    p_score,
                    f.get("cvss_vector", ""),
                    json.dumps(repro),
                    f.get("safe_poc", ""),
                    str(b_imp.get("business_consequence", b_imp) if isinstance(b_imp, dict) else b_imp),
                    b_imp_str,
                    f.get("technical_impact", ""),
                    json.dumps(calc_factors),
                    json.dumps(verif),
                    f.get("file", ""),
                    int(f.get("line", 1) or 1),
                    f.get("symbol_or_function", ""),
                    f.get("code_pattern", ""),
                    f.get("security_relevance", ""),
                    f.get("detector", ""),
                    f.get("runtime_validation_status", f.get("status", "POTENTIAL")),
                    json.dumps(source_details),
                    f.get("created_at", datetime.now(timezone.utc).isoformat())
                ))
            conn.commit()

    def save_evidence_list(self, evidence_list: List[Dict[str, Any]]):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            for ev in evidence_list:
                tech_exp = ev.get("technical_explanation", {})
                cursor.execute("""
                INSERT OR REPLACE INTO evidence (
                    id, assessment_id, finding_id, type, data_json, integrity_hash,
                    command, expected_output, observed_output, verification_steps_json,
                    simple_explanation, technical_explanation_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ev.get("evidence_id") or ev["id"],
                    ev["assessment_id"],
                    ev.get("finding_id", ""),
                    ev.get("test_name", ev.get("type", "COMMAND_OUTPUT")),
                    json.dumps(ev.get("response", ev.get("data", {}))),
                    ev.get("hash", ev.get("integrity_hash", "")),
                    ev.get("verification_command", ev.get("command", "")),
                    ev.get("expected_output", ""),
                    ev.get("observed_output", ev.get("raw_observation", "")),
                    json.dumps(ev.get("verification_steps", [])),
                    ev.get("simple_explanation", ""),
                    json.dumps(tech_exp),
                    ev.get("timestamp", ev.get("created_at", datetime.now(timezone.utc).isoformat()))
                ))
            conn.commit()

    def save_risk_records(self, risk_records: List[Dict[str, Any]]):
        """Persists finding-specific CVSS 3.1 risk records with calculation factors."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            for r in risk_records:
                metrics = r.get("metrics", {})
                cursor.execute("""
                INSERT OR REPLACE INTO risk_records (
                    id, assessment_id, finding_id, cvss_version, cvss_score, cvss_vector,
                    severity, attack_vector, attack_complexity, privileges_required, user_interaction,
                    scope, confidentiality_impact, integrity_impact, availability_impact,
                    calculation_factors_json, business_impact_json, affected_assets_json,
                    confidence, reasoning, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["risk_id"],
                    r["assessment_id"],
                    r["finding_id"],
                    r.get("cvss_version", "CVSS v3.1"),
                    float(r.get("cvss_score", 0.0)),
                    r.get("cvss_vector", ""),
                    r.get("severity", "NONE"),
                    metrics.get("attack_vector", "NETWORK"),
                    metrics.get("attack_complexity", "LOW"),
                    metrics.get("privileges_required", "NONE"),
                    metrics.get("user_interaction", "NONE"),
                    metrics.get("scope", "UNCHANGED"),
                    metrics.get("confidentiality_impact", "NONE"),
                    metrics.get("integrity_impact", "NONE"),
                    metrics.get("availability_impact", "NONE"),
                    json.dumps(r.get("calculation_factors", {})),
                    json.dumps(r.get("business_impact", {})),
                    json.dumps(r.get("affected_assets", [])),
                    r.get("confidence", "CERTAIN"),
                    r.get("reasoning", ""),
                    r.get("created_at", datetime.now(timezone.utc).isoformat())
                ))
            conn.commit()

    def get_all_assessments(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assessments ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def get_all_findings(self, assessment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if assessment_id:
                cursor.execute("SELECT * FROM findings WHERE assessment_id = ? ORDER BY rowid DESC", (assessment_id,))
            else:
                cursor.execute("SELECT * FROM findings ORDER BY rowid DESC")
            rows = cursor.fetchall()
            findings = []
            for r in rows:
                item = dict(r)
                item["evidence_ids"] = json.loads(item.get("evidence_ids_json") or "[]")
                item["reproduction_steps"] = json.loads(item.get("reproduction_steps_json") or "[]")
                item["verification"] = json.loads(item.get("verification_json") or "{}")
                item["calculation_factors"] = json.loads(item.get("calculation_factors_json") or "{}")
                try:
                    item["business_impact_details"] = json.loads(item.get("business_impact_json") or "{}")
                except Exception:
                    item["business_impact_details"] = {"business_consequence": item.get("business_impact", "")}

                src_details = json.loads(item.get("source_details_json") or "{}")
                for q_key in ["what_code_caused_problem", "what_happened_at_runtime", "what_evidence_proves_it", "what_is_the_impact", "how_should_it_be_fixed"]:
                    if q_key in src_details:
                        item[q_key] = src_details[q_key]

                findings.append(item)
            return findings

    def get_all_evidence(self, assessment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if assessment_id:
                cursor.execute("""
                SELECT e.*, f.title as f_title, f.severity as f_sev, f.category as f_cat,
                       f.cwe_id as f_cwe, f.owasp_id as f_owasp, f.description as f_desc,
                       f.remediation as f_rem, f.status as f_status, f.affected_component as f_target,
                       f.cvss_score as f_cvss, f.cvss_vector as f_vector, f.safe_poc as f_poc,
                       f.calculation_factors_json as f_calc_json, f.business_impact_json as f_biz_json
                FROM evidence e
                LEFT JOIN findings f ON e.finding_id = f.id
                WHERE e.assessment_id = ?
                ORDER BY e.rowid DESC
                """, (assessment_id,))
            else:
                cursor.execute("""
                SELECT e.*, f.title as f_title, f.severity as f_sev, f.category as f_cat,
                       f.cwe_id as f_cwe, f.owasp_id as f_owasp, f.description as f_desc,
                       f.remediation as f_rem, f.status as f_status, f.affected_component as f_target,
                       f.cvss_score as f_cvss, f.cvss_vector as f_vector, f.safe_poc as f_poc,
                       f.calculation_factors_json as f_calc_json, f.business_impact_json as f_biz_json
                FROM evidence e
                LEFT JOIN findings f ON e.finding_id = f.id
                ORDER BY e.rowid DESC
                """)
            rows = cursor.fetchall()
            evidence_list = []
            for r in rows:
                item = dict(r)
                item["data"] = json.loads(item.get("data_json") or "{}")
                item["verification_steps"] = json.loads(item.get("verification_steps_json") or "[]")
                item["technical_explanation"] = json.loads(item.get("technical_explanation_json") or "{}")
                item["calculation_factors"] = json.loads(item.get("f_calc_json") or "{}")
                evidence_list.append(item)
            return evidence_list

    def get_risk_records(self, assessment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if assessment_id:
                cursor.execute("SELECT * FROM risk_records WHERE assessment_id = ? ORDER BY cvss_score DESC", (assessment_id,))
            else:
                cursor.execute("SELECT * FROM risk_records ORDER BY cvss_score DESC")
            rows = cursor.fetchall()
            risks = []
            for r in rows:
                item = dict(r)
                item["calculation_factors"] = json.loads(item.get("calculation_factors_json") or "{}")
                item["business_impact"] = json.loads(item.get("business_impact_json") or "{}")
                item["affected_assets"] = json.loads(item.get("affected_assets_json") or "[]")
                risks.append(item)
            return risks

    def get_risk_by_finding(self, finding_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM risk_records WHERE finding_id = ?", (finding_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            res["calculation_factors"] = json.loads(res.get("calculation_factors_json") or "{}")
            res["business_impact"] = json.loads(res.get("business_impact_json") or "{}")
            res["affected_assets"] = json.loads(res.get("affected_assets_json") or "[]")
            return res

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            res["data"] = json.loads(res.get("data_json") or "{}")
            res["verification_steps"] = json.loads(res.get("verification_steps_json") or "[]")
            res["technical_explanation"] = json.loads(res.get("technical_explanation_json") or "{}")
            return res

    def get_experience_items(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experience_db ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def add_experience_item(self, finding_id: str, rationale: str, rule_name: str = "Custom Suppress", target: str = "*") -> str:
        item_id = f"EXP-{int(datetime.now().timestamp())}"
        created_at = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO experience_db (id, finding_signature, finding_id, rule_name, target_pattern, rationale, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
            """, (item_id, f"SIG-{finding_id}", finding_id, rule_name, target, rationale, created_at))
            conn.commit()
        self.log_audit_event("EXPERIENCE_DB_COMMIT", f"Committed false-positive lesson for {finding_id}", details={"rationale": rationale})
        return item_id

    def update_finding_status(
        self,
        finding_id: str,
        new_status: str,
        reason: str = "Status update",
        actor: str = "Operator"
    ) -> bool:
        """
        Transitions finding lifecycle status across:
        OPEN, REMEDIATION_RECOMMENDED, RETEST_REQUIRED, VERIFIED, NOT_VERIFIED.
        Records an immutable, cryptographically chained audit event.
        """
        valid_statuses = {"OPEN", "REMEDIATION_RECOMMENDED", "RETEST_REQUIRED", "VERIFIED", "NOT_VERIFIED", "CONFIRMED", "RESOLVED", "FALSE_POSITIVE"}
        if new_status not in valid_statuses:
            new_status = new_status.upper()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT assessment_id, status, evidence_id FROM findings WHERE id = ? OR finding_id = ?", (finding_id, finding_id))
            row = cursor.fetchone()
            if not row:
                return False
            old_status = row["status"]
            asm_id = row["assessment_id"] or "GLOBAL"
            ev_id = row["evidence_id"] or ""
            cursor.execute(
                "UPDATE findings SET status = ? WHERE id = ? OR finding_id = ?",
                (new_status, finding_id, finding_id)
            )
            conn.commit()

        # Log tamper-evident audit events with all 8 fields
        h_val = hashlib.sha256(f"{finding_id}:{old_status}->{new_status}".encode()).hexdigest()
        self.log_audit_event(
            event_type="FINDING_STATUS_CHANGED",
            action=f"Finding status changed from {old_status} to {new_status}",
            actor=actor,
            assessment_id=asm_id,
            object_name=finding_id,
            result=new_status,
            evidence_ref=ev_id,
            hash_val=h_val,
            details={
                "finding_id": finding_id,
                "previous_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        self.log_audit_event(
            event_type="FINDING_STATUS_TRANSITION",
            action=f"Finding {finding_id} status transitioned from {old_status} to {new_status}",
            actor=actor,
            assessment_id=asm_id,
            object_name=finding_id,
            result=new_status,
            evidence_ref=ev_id,
            hash_val=h_val,
            details={
                "finding_id": finding_id,
                "previous_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        return True


# Global singleton storage instance
storage = StorageService()

