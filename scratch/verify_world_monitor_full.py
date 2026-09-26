import asyncio
import sys
import os

# Add project root and backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.app.services.world_monitor_service import world_monitor_service
from backend.app.core.database import SessionLocal
from backend.app.api.routes.test_center import run_controlled_test, RunTestRequest

async def verify_all():
    print("==================================================")
    print("VERIFYING WORLD MONITOR ENDPOINTS AND ARCHITECTURE")
    print("==================================================")
    
    # 1. Fetch live / demo events
    live_res = world_monitor_service.get_events(mode='live')
    print(f"1. Live Events: Mode={live_res['mode']}, Count={live_res['total_count']}, Filtered={live_res['filtered_count']}")
    assert live_res['total_count'] > 0, "Expected events in live mode"
    
    # Verify coordinate integrity: only genuine coordinates are marked has_coordinates=True
    geo_events = [e for e in live_res['events'] if e['location']['has_coordinates']]
    non_geo_events = [e for e in live_res['events'] if not e['location']['has_coordinates']]
    print(f"   Geo-pinned events: {len(geo_events)} | Non-geo feed-only events: {len(non_geo_events)}")
    for g in geo_events:
        assert g['location']['latitude'] is not None and g['location']['longitude'] is not None
        print(f"   - [GEO] {g['title']} ({g['location']['city']}, {g['location']['country_code']}) -> ({g['location']['latitude']}, {g['location']['longitude']})")
    
    # 2. Demo mode
    demo_res = world_monitor_service.get_events(mode='demo')
    print(f"2. Demo Events: Mode={demo_res['mode']}, Count={demo_res['total_count']}")
    assert demo_res['mode'] in ['DEMO', 'LIVE']
    for e in demo_res['events']:
        assert e['is_demo'] is True
    print("   All demo events properly flagged is_demo=True")
    
    # 3. Source status
    sources = world_monitor_service.get_sources()
    print(f"3. Sources count: {len(sources)}")
    for s in sources:
        print(f"   - {s['name']}: Status={s['status']} (Type={s['type']}, Events={s['events_count']})")
        
    # 4. Correlation Tests
    print("4. Testing Correlation Engine:")
    
    # Test A: Exact CVE match
    findings_exact_cve = [
        {
            "id": "KAV-FIND-001",
            "title": "Vulnerability in XZ Utils / SSH",
            "cve_id": "CVE-2024-3094",
            "cve_ids": ["CVE-2024-3094"],
            "affected_component": "liblzma",
            "technology": "XZ Utils"
        }
    ]
    corr_exact = world_monitor_service.correlate_with_findings({"target_url": "https://example.com"}, findings_exact_cve)
    print(f"   Test A (Exact CVE): Correlations={len(corr_exact)}")
    assert len(corr_exact) >= 1
    assert corr_exact[0]["confidence"] == "HIGH"
    print(f"   -> Matched {corr_exact[0]['event_title']} with confidence={corr_exact[0]['confidence']}")
    print(f"   -> Explanation: {corr_exact[0]['explanation']}")
    
    # Test B: Technology match without CVE
    findings_tech = [
        {
            "id": "KAV-FIND-002",
            "title": "Exposed Server Version Header",
            "category": "Information Disclosure",
            "affected_component": "FastAPI",
            "technology": "FastAPI",
            "cve_ids": []
        }
    ]
    corr_tech = world_monitor_service.correlate_with_findings({"target_url": "https://example.com"}, findings_tech)
    print(f"   Test B (Tech match): Correlations={len(corr_tech)}")
    assert len(corr_tech) >= 1
    print(f"   -> Matched {corr_tech[0]['event_title']} with confidence={corr_tech[0]['confidence']}")
    assert corr_tech[0]["confidence"] in ["MEDIUM", "LOW"]
        
    # Test C: Unrelated finding
    findings_unrelated = [
        {
            "id": "KAV-FIND-003",
            "title": "CustomInternal proprietary check",
            "category": "Proprietary",
            "technology": "CustomInternalAppXYZ",
            "cve_ids": []
        }
    ]
    corr_unrelated = world_monitor_service.correlate_with_findings({"target_url": "https://internal-app.local"}, findings_unrelated)
    print(f"   Test C (Unrelated): Correlations={len(corr_unrelated)}")
    assert len(corr_unrelated) == 0, "Unrelated finding should not correlate"
    print("   -> Correctly produced 0 correlations")

    # 5. Test Center World Monitor Suites
    print("5. Testing Test Center World Monitor test suites in DB:")
    db = SessionLocal()
    try:
        suites = ["wm_cve_exact_match", "wm_technology_match", "wm_unrelated_event"]
        for s_id in suites:
            res = run_controlled_test(RunTestRequest(suite_id=s_id), db)
            print(f"   - Suite '{s_id}': Passed={res['passed_checks']}/{res['total_checks']} Status={res['overall_status']}")
            assert res['passed_checks'] == res['total_checks']
    finally:
        db.close()
        
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    asyncio.run(verify_all())
