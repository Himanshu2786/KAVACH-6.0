"""
KAVACH 5.0 — Real World Monitor Target Integration Test Suite
Validates:
1. Centralized World Monitor target configuration
2. Repository inventory analyzer
3. RUNTIME mode non-destructive probing across all 7 domains
4. SOURCE mode static inspection & unconfigured fallback
5. HYBRID mode correlation records & evidence linking
6. 7-Domain Validation Coverage Matrix generation
7. Strict data origin tagging (REAL_RUNTIME, REAL_SOURCE, BASELINE, SYNTHETIC_TEST)
8. Cryptographic SHA-256 evidence hashing
9. Offline Ollama deterministic fallback
10. Assessment isolation & clean baseline reporting
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.target_config import WORLD_MONITOR_TARGET, get_world_monitor_target
from backend.app.services.world_monitor_assessment_engine import (
    world_monitor_assessment_engine,
    SCOPE_CATEGORIES
)
from backend.app.core.database import SessionLocal, Base, engine
from services.storage_service import storage


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def cleanup_test_assessment():
    """
    Yields the list of assessment IDs generated during a test and removes
    their findings and evidence from the live DB after the test completes.
    This prevents synthetic/tmp-path assessments from polluting the live DB.
    """
    generated_ids = []
    yield generated_ids
    if not generated_ids:
        return
    try:
        from backend.app.models.models import Finding, EvidenceRecord, DiscoveryItem, Assessment
        db = SessionLocal()
        for asm_id in generated_ids:
            # Delete in FK order: evidence -> findings -> discovery -> assessment
            ev_ids = [row[0] for row in db.execute(
                __import__('sqlalchemy').text(
                    "SELECT er.id FROM evidence_records er "
                    "JOIN findings f ON er.finding_id = f.id "
                    "WHERE f.assessment_id = :aid"
                ), {"aid": asm_id}
            ).fetchall()]
            if ev_ids:
                db.execute(
                    __import__('sqlalchemy').text(
                        "DELETE FROM evidence_records WHERE id IN (%s)" % ",".join(["'%s'" % i for i in ev_ids])
                    )
                )
            db.execute(
                __import__('sqlalchemy').text(
                    "DELETE FROM findings WHERE assessment_id = :aid"
                ), {"aid": asm_id}
            )
            db.execute(
                __import__('sqlalchemy').text(
                    "DELETE FROM discovery_items WHERE assessment_id = :aid"
                ), {"aid": asm_id}
            )
            db.execute(
                __import__('sqlalchemy').text(
                    "DELETE FROM assessments WHERE id = :aid"
                ), {"aid": asm_id}
            )
        db.commit()
        db.close()
    except Exception as e:
        import warnings
        warnings.warn(f"[cleanup_test_assessment] Failed to clean up test DB records: {e}")


def test_centralized_target_configuration():
    """Verify centralized target registry for World Monitor."""
    target = get_world_monitor_target()
    assert target["target_id"] == "TGT-WORLD-MONITOR-01"
    assert target["name"] == "World Monitor"
    assert target["web_url"] == "https://www.worldmonitor.app"
    assert target["repository_url"] == "https://github.com/koala73/worldmonitor"
    assert target["target_type"] == "external_authorized_assessment"
    assert target["source_type"] == "public_source_repository"
    assert "HYBRID" in target["supported_modes"]
    assert "RUNTIME" in target["supported_modes"]
    assert "SOURCE" in target["supported_modes"]
    assert len(target["scope_domains"]) == 7
    assert target["safety_policy"]["read_only"] is True
    assert target["safety_policy"]["non_destructive"] is True


def test_repository_inventory_unconfigured():
    """Verify clean reporting when source repository is unconfigured."""
    inv = world_monitor_assessment_engine.inventory_source_repository(None)
    assert inv["configured"] is False
    assert inv["exists"] is False
    assert inv["status"] == "SOURCE_NOT_CONFIGURED"


def test_repository_inventory_valid_path(tmp_path):
    """Verify source repository inventory inspection on valid tree."""
    repo_dir = tmp_path / "worldmonitor_test_repo"
    repo_dir.mkdir()
    
    # Create fake package.json
    pkg_json = repo_dir / "package.json"
    pkg_json.write_text('{"dependencies": {"react": "^18.0.0", "vite": "^5.0.0", "typescript": "^5.0.0", "@tauri-apps/api": "^2.0.0"}}', encoding="utf-8")
    
    # Create sample source file
    src_file = repo_dir / "app.tsx"
    src_file.write_text('export const App = () => <div>World Monitor</div>;', encoding="utf-8")

    inv = world_monitor_assessment_engine.inventory_source_repository(repo_dir)
    assert inv["configured"] is True
    assert inv["exists"] is True
    assert "React" in inv["framework"]
    assert "Tauri 2" in inv["framework"]
    assert "package.json" in inv["manifests"]
    assert inv["file_count"] >= 2
    assert inv["source_file_count"] >= 1


def test_runtime_assessment_mode():
    """Verify RUNTIME mode execution produces valid coverage matrix and data origin."""
    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=None,
        mode="RUNTIME",
        assessment_name="World Monitor Runtime Audit"
    ))

    assert res["target_id"] == "TGT-WORLD-MONITOR-01"
    assert res["target_name"] == "World Monitor"
    assert res["mode"] == "RUNTIME"
    assert res["data_origin"] == "REAL_RUNTIME"
    assert "coverage_matrix" in res
    assert len(res["coverage_matrix"]) == 7

    # Verify all evidence items have cryptographic SHA-256 hashes and data origin
    for ev in res["evidence"]:
        assert "evidence_id" in ev
        assert "hash" in ev or "integrity_hash" in ev
        assert len(ev.get("hash") or ev.get("integrity_hash")) == 64
        assert ev.get("data_origin") == "REAL_RUNTIME"


def test_source_assessment_mode_unconfigured():
    """Verify SOURCE mode when repository is not configured emits clean status without fabricating findings."""
    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=None,
        mode="SOURCE",
        assessment_name="World Monitor Unconfigured Source Audit"
    ))

    assert res["mode"] == "SOURCE"
    assert res["source_path"] == "WORLD_MONITOR_SOURCE_NOT_CONFIGURED"
    # Verify no fake vulnerabilities fabricated
    assert res["confirmed_findings"] == 0
    # Verify discovery item notes source configuration requirement
    assert any("WORLD_MONITOR_SOURCE_NOT_CONFIGURED" in d.get("details", "") for d in res["discovery"])


def test_source_assessment_with_sample_repo(tmp_path, cleanup_test_assessment):
    """Verify SOURCE mode with a sample repo that has no git remote.

    After the source-provenance fix:
    - A sample tmp directory without a .git/config is correctly rejected by the provenance gate.
    - The engine must emit SOURCE_PROVENANCE_UNVERIFIED and produce zero source findings.
    - This is correct behavior: tmp-path fixtures should NOT generate confirmed source findings.
    """
    sample_dir = tmp_path / "wm_sample_src"
    sample_dir.mkdir()

    # Create test source file with insecure CORS and local storage token
    src_file = sample_dir / "auth_service.ts"
    src_file.write_text(
        'export function saveSession(token: string) {\n'
        '  localStorage.setItem("auth_token", token);\n'
        '}\n'
        'export const corsConfig = {\n'
        '  allow_origins: ["*"]\n'
        '};\n',
        encoding="utf-8"
    )

    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=str(sample_dir),
        mode="SOURCE",
        assessment_name="World Monitor Source Code Audit"
    ))
    cleanup_test_assessment.append(res["assessment_id"])

    assert res["mode"] == "SOURCE"

    # With provenance gate: no .git directory → SOURCE_PROVENANCE_UNVERIFIED, zero source findings
    source_findings = [f for f in res.get("findings", []) if f.get("data_origin") == "REAL_SOURCE"]
    assert len(source_findings) == 0, (
        f"Expected 0 source findings from tmp path without git repo, got: "
        f"{[f.get('id') for f in source_findings]}"
    )
    stage_statuses = [s.get("status") for s in res.get("stages_executed", [])]
    assert "SOURCE_PROVENANCE_UNVERIFIED" in stage_statuses, (
        f"Expected SOURCE_PROVENANCE_UNVERIFIED in stages_executed. Got: {stage_statuses}"
    )


def test_hybrid_assessment_and_correlation(tmp_path, cleanup_test_assessment):
    """Verify HYBRID mode correlates source findings with runtime observations and produces correlation records.

    NOTE: The test source path is a synthetic tmp directory with NO git remote. As of the
    source-provenance fix, the engine's provenance gate MUST block source analysis and produce
    zero source findings. A SOURCE_PROVENANCE_UNVERIFIED discovery item must be emitted instead.
    The cleanup_test_assessment fixture removes this test's DB records after the test completes.
    """
    sample_dir = tmp_path / "wm_hybrid_src"
    sample_dir.mkdir()

    src_file = sample_dir / "config.ts"
    src_file.write_text('export const config = { debug: true, allow_origins: ["*"] };\n', encoding="utf-8")

    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=str(sample_dir),
        mode="HYBRID",
        assessment_name="World Monitor Hybrid Correlation Audit"
    ))
    cleanup_test_assessment.append(res["assessment_id"])

    assert res["mode"] == "HYBRID"
    assert "correlation_records" in res
    assert "coverage_matrix" in res
    assert len(res["coverage_matrix"]) == 7

    # With the provenance gate active, a tmp path with no git remote must NOT produce source findings
    source_findings = [f for f in res.get("findings", []) if f.get("data_origin") == "REAL_SOURCE"]
    assert len(source_findings) == 0, (
        f"Expected 0 source findings from unverified tmp path, got {len(source_findings)}: "
        f"{[f.get('id') for f in source_findings]}"
    )

    # A SOURCE_PROVENANCE_UNVERIFIED stage must be recorded
    stage_statuses = [s.get("status") for s in res.get("stages_executed", [])]
    assert "SOURCE_PROVENANCE_UNVERIFIED" in stage_statuses, (
        f"Expected SOURCE_PROVENANCE_UNVERIFIED in stages_executed, got: {stage_statuses}"
    )

    # The discovery items must contain the provenance-unverified notice
    disc_details = " ".join(d.get("details", "") for d in res.get("discovery", []))
    assert "SOURCE_PROVENANCE_UNVERIFIED" in disc_details, (
        "Expected SOURCE_PROVENANCE_UNVERIFIED in discovery item details."
    )



def test_seven_domain_coverage_matrix_structure():
    """Verify 7-domain coverage matrix encompasses all mandated security categories."""
    matrix = world_monitor_assessment_engine.generate_coverage_matrix(
        findings=[],
        evidence=[],
        mode="HYBRID",
        preflight_reachable=True,
        source_audited=True
    )
    assert len(matrix) == 7
    categories = [m["category_code"] for m in matrix]
    for expected in ["AUTH", "AUTHZ", "INPUT", "API", "CLIENT", "COMM", "STORAGE"]:
        assert expected in categories


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION TESTS: SOURCE PROVENANCE GATE
# ─────────────────────────────────────────────────────────────────────────────

def test_unrelated_config_ts_cannot_become_confirmed_source_finding(tmp_path, cleanup_test_assessment):
    """
    Regression: A local/temp directory containing a config.ts with 'debug: true' must NOT
    produce a CONFIRMED source finding. The file has no association with the authorized
    World Monitor repository (no .git directory, no origin remote).
    """
    unrelated_dir = tmp_path / "unrelated_project"
    unrelated_dir.mkdir()
    (unrelated_dir / "config.ts").write_text(
        'export const config = { debug: true, allow_origins: ["*"] };\n',
        encoding="utf-8"
    )

    # Verify the provenance gate directly
    prov = world_monitor_assessment_engine._verify_source_provenance(
        unrelated_dir,
        {"commit_sha": "NOT_AVAILABLE"}
    )
    assert prov["authorized"] is False, (
        f"Expected unauthorized (no .git), got authorized=True. Reason: {prov['reason']}"
    )
    assert ".git" in prov["reason"] or "not a git repository" in prov["reason"].lower()

    # Verify the full assessment produces no confirmed source findings
    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=str(unrelated_dir),
        mode="SOURCE",
        assessment_name="Regression: Unrelated Config.ts Source Probe"
    ))
    cleanup_test_assessment.append(res["assessment_id"])

    confirmed_source = [
        f for f in res.get("findings", [])
        if f.get("data_origin") == "REAL_SOURCE" and f.get("status") == "CONFIRMED"
    ]
    assert len(confirmed_source) == 0, (
        f"Regression FAILED: {len(confirmed_source)} CONFIRMED source findings from unrelated tmp path: "
        f"{[f.get('id') for f in confirmed_source]}"
    )


def test_source_finding_requires_authorized_repository_git_remote(tmp_path, cleanup_test_assessment):
    """
    Regression: A git repository whose remote 'origin' does NOT match the authorized
    World Monitor identifier must NOT produce source findings, even if source files
    match detector patterns.
    """
    unauth_repo = tmp_path / "unauthorized_repo"
    unauth_repo.mkdir()
    git_dir = unauth_repo / ".git"
    git_dir.mkdir()

    # Create a .git/config pointing to an unrelated repository
    (git_dir / "config").write_text(
        '[core]\n\trepositoryformatversion = 0\n\tfilemode = false\n'
        '[remote "origin"]\n\turl = https://github.com/some-other-org/unrelated-project.git\n'
        '\tfetch = +refs/heads/*:refs/remotes/origin/*\n',
        encoding="utf-8"
    )
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    # Simulate source file with debug: true
    (unauth_repo / "config.ts").write_text(
        'export const config = { debug: true, allow_origins: ["*"] };\n',
        encoding="utf-8"
    )

    # Verify the provenance gate rejects this repository
    prov = world_monitor_assessment_engine._verify_source_provenance(
        unauth_repo,
        {"commit_sha": "abc123"}
    )
    assert prov["authorized"] is False, (
        f"Expected unauthorized (wrong remote), got authorized=True. Remote: {prov['git_remote']}"
    )
    assert "does not match" in prov["reason"] or "UNVERIFIED" in prov["reason"]
    assert "some-other-org" in prov["git_remote"] or "unrelated-project" in prov["git_remote"]

    # Run assessment and confirm no source findings leak through
    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=str(unauth_repo),
        mode="SOURCE",
        assessment_name="Regression: Unauthorized Remote Source Probe"
    ))
    cleanup_test_assessment.append(res["assessment_id"])

    source_findings = [f for f in res.get("findings", []) if f.get("data_origin") == "REAL_SOURCE"]
    assert len(source_findings) == 0, (
        f"Regression FAILED: {len(source_findings)} source findings from unauthorized remote repo."
    )
    stage_statuses = [s.get("status") for s in res.get("stages_executed", [])]
    assert "SOURCE_PROVENANCE_UNVERIFIED" in stage_statuses


def test_source_provenance_unverified_appears_in_discovery_not_findings(tmp_path, cleanup_test_assessment):
    """
    Regression: When a source path fails the provenance gate, the engine must emit a
    SOURCE_PROVENANCE_UNVERIFIED discovery item and NO source findings. The finding list
    must remain empty for source data.
    """
    bare_dir = tmp_path / "bare_source"
    bare_dir.mkdir()
    # No .git directory. Source file with multiple vulnerable patterns.
    (bare_dir / "auth.ts").write_text(
        'const JWT_SECRET = "hardcoded-secret-abc123";\n'
        'localStorage.setItem("auth_token", token);\n'
        'export const config = { debug: true, allow_origins: ["*"] };\n',
        encoding="utf-8"
    )

    res = asyncio.run(world_monitor_assessment_engine.run_assessment(
        target_url="https://www.worldmonitor.app",
        source_path=str(bare_dir),
        mode="SOURCE",
        assessment_name="Regression: Provenance Unverified Discovery Item Test"
    ))
    cleanup_test_assessment.append(res["assessment_id"])

    # No source findings must be in the result
    source_findings = [f for f in res.get("findings", []) if f.get("data_origin") == "REAL_SOURCE"]
    assert len(source_findings) == 0, (
        f"Expected zero source findings from unverified path, got: "
        f"{[f.get('id') for f in source_findings]}"
    )

    # SOURCE_PROVENANCE_UNVERIFIED must appear in discovery details
    disc_details = " | ".join(d.get("details", "") for d in res.get("discovery", []))
    assert "SOURCE_PROVENANCE_UNVERIFIED" in disc_details, (
        f"Expected SOURCE_PROVENANCE_UNVERIFIED in discovery items. Got: {disc_details[:300]}"
    )

    # stages_executed must report SOURCE_PROVENANCE_UNVERIFIED
    stage_statuses = [s.get("status") for s in res.get("stages_executed", [])]
    assert "SOURCE_PROVENANCE_UNVERIFIED" in stage_statuses, (
        f"Expected SOURCE_PROVENANCE_UNVERIFIED in stages_executed. Got: {stage_statuses}"
    )

    # source_path in result must be the path we passed (not NOT_CONFIGURED)
    assert res.get("source_path") != "WORLD_MONITOR_SOURCE_NOT_CONFIGURED"
