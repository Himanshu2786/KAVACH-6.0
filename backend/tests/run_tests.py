import sys
from backend.tests.test_api import (
    setup_test_db,
    test_api_health,
    test_system_status,
    test_ollama_health_offline_handling,
    test_assessment_creation_scope_guard,
    test_findings_retrieval,
    test_knowledge_correlation,
    test_ai_analysis_and_rule_based_fallback,
    test_evidence_validation_confirms_finding,
    test_risk_prioritization_calculation,
    test_remediation_details,
    test_report_generation,
    test_terminal_verification,
    test_re_verification
)

def main():
    print("=== Running KAVACH Backend Test Suite ===")
    
    # Initialize fixture
    gen = setup_test_db()
    next(gen)

    tests = [
        ("API Health", test_api_health),
        ("System Status Grid", test_system_status),
        ("Ollama Offline Handling", test_ollama_health_offline_handling),
        ("Assessment Creation Scope Guard", test_assessment_creation_scope_guard),
        ("Findings Retrieval & Serialization", test_findings_retrieval),
        ("Knowledge Engine Correlation", test_knowledge_correlation),
        ("AI Analysis & Rule-based Fallback", test_ai_analysis_and_rule_based_fallback),
        ("Evidence Validation Confirms Finding", test_evidence_validation_confirms_finding),
        ("Risk Prioritization Deterministic Score", test_risk_prioritization_calculation),
        ("Remediation Guidance & Code Samples", test_remediation_details),
        ("Report Generation (JSON & HTML Print)", test_report_generation),
        ("Technical Terminal Evidence Matching", test_terminal_verification),
        ("Re-Verification & Status Transition", test_re_verification),
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as ex:
            print(f"  [FAIL] {name}: {ex}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests.")
    if failed > 0:
        sys.exit(1)
    print("=== ALL KAVACH BACKEND TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
