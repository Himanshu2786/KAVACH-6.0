"""
Comprehensive automated test suite for KAVACH secure defensive file scanner.
"""

import os
import tempfile
from core.scanner.filesystem_scanner import FilesystemScanner
from core.scanner.hash_analyzer import HashAnalyzer
from core.scanner.rule_engine import mask_secret
from services.storage_service import storage

def test_scanner():
    print("================================================================================")
    print("                    KAVACH SCANNER AUTOMATED TEST SUITE                         ")
    print("================================================================================")
    
    scanner = FilesystemScanner()
    
    # 1. Test Secret Redaction helper
    print("\n[TEST 1] Secret Redaction:")
    raw_key = "AKIAIOSFODNN7EXAMPLE"
    masked = mask_secret(raw_key)
    print(f" - Raw Key:   {raw_key}")
    print(f" - Masked:    {masked}")
    assert masked.startswith("AKIA"), "Masked key should preserve first 4 characters"
    assert "*" in masked, "Masked key should contain asterisks"
    assert "EXAMPLE" not in masked, "Masked key should not expose plaintext suffix"
    print(" [PASS] Secret redaction working securely.")

    # 2. Test Scan on demo_api_keys.env
    print("\n[TEST 2] Scanning demo_api_keys.env:")
    env_path = "demo/training_samples/demo_api_keys.env"
    res = scanner.scan_target(env_path)
    print(f" - Status: {res.status}")
    print(f" - Files Scanned: {res.total_files_scanned}")
    print(f" - Observations Generated: {len(res.observations)}")
    for o in res.observations:
        print(f"   * [{o.severity}] {o.rule_name} | {o.redacted_snippet}")
    assert len(res.observations) >= 2, "Should detect at least AWS key and DB password"
    print(" [PASS] Secret detection & redaction verified.")

    # 3. Test Scan on suspicious_invoice.pdf.exe
    print("\n[TEST 3] Scanning suspicious_invoice.pdf.exe:")
    pdf_exe_path = "demo/training_samples/suspicious_invoice.pdf.exe"
    res = scanner.scan_target(pdf_exe_path)
    print(f" - Observations Generated: {len(res.observations)}")
    assert any("Double Extension" in o.rule_name for o in res.observations), "Should detect double extension"
    print(" [PASS] Double extension detection verified.")

    # 4. Test Scan on demo_insecure_config.json
    print("\n[TEST 4] Scanning demo_insecure_config.json:")
    cfg_path = "demo/training_samples/demo_insecure_config.json"
    res = scanner.scan_target(cfg_path)
    print(f" - Observations Generated: {len(res.observations)}")
    for o in res.observations:
        print(f"   * [{o.severity}] {o.rule_name}")
    assert any("Debug Mode" in o.rule_name for o in res.observations), "Should detect debug mode"
    print(" [PASS] Insecure configuration analysis verified.")

    # 5. Test Scan on clean_document.txt
    print("\n[TEST 5] Scanning clean_document.txt (Zero Findings Benchmark):")
    clean_path = "demo/training_samples/clean_document.txt"
    res = scanner.scan_target(clean_path)
    print(f" - Observations Generated: {len(res.observations)}")
    assert len(res.observations) == 0, "Clean file should produce exactly 0 findings"
    print(" [PASS] Clean file produces 0 findings.")

    # 6. Test Recursive Folder Scan
    print("\n[TEST 6] Recursive Folder Scan on demo/training_samples/:")
    folder_path = "demo/training_samples"
    res = scanner.scan_target(folder_path)
    print(f" - Files Scanned: {res.total_files_scanned}")
    print(f" - Total Findings: {len(res.observations)}")
    print(f" - Duration: {res.duration_seconds}s")
    assert res.total_files_scanned >= 4, "Should scan at least 4 demo sample files"
    print(" [PASS] Recursive folder scan verified.")

    # 7. Test Nonexistent Path
    print("\n[TEST 7] Error Handling for Nonexistent Path:")
    res = scanner.scan_target("nonexistent_folder_xyz_123")
    print(f" - Status: {res.status} | Error: {res.error_message}")
    assert res.status == "ERROR", "Should report ERROR for missing path"
    print(" [PASS] Nonexistent path handled cleanly.")

    # 8. Test SHA-256 Bitwise Reproducibility
    print("\n[TEST 8] SHA-256 Bitwise Reproducibility:")
    h1 = HashAnalyzer.calculate_sha256(clean_path)
    h2 = HashAnalyzer.calculate_sha256(clean_path)
    print(f" - Hash 1: {h1}")
    print(f" - Hash 2: {h2}")
    assert h1 == h2, "Hash must be identical on subsequent reads"
    print(" [PASS] SHA-256 calculation verified.")

    print("\n================================================================================")
    print("                     ALL SCANNER TESTS PASSED (8/8)                             ")
    print("================================================================================")

if __name__ == "__main__":
    test_scanner()
