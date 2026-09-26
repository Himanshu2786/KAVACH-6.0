import httpx
import json
import datetime

base = 'http://127.0.0.1:8000'
results = []

def test(name, method, path, body=None, expected_codes=None, timeout=15):
    if expected_codes is None:
        expected_codes = [200, 201]
    url = base + path
    try:
        if method == 'GET':
            r = httpx.get(url, timeout=timeout)
        elif method == 'POST':
            r = httpx.post(url, json=body, timeout=timeout)
        elif method == 'PUT':
            r = httpx.put(url, json=body, timeout=timeout)
        passed = r.status_code in expected_codes
        results.append({'name': name, 'status': r.status_code, 'pass': passed, 'url': path, 'method': method})
        status_word = 'PASS' if passed else 'FAIL'
        print(f"{status_word} [{r.status_code}] {name}")
        return r
    except Exception as e:
        results.append({'name': name, 'status': 'ERR', 'pass': False, 'url': path, 'method': method, 'error': str(e)})
        print(f"FAIL [ERR] {name}: {type(e).__name__}")
        return None

print("=" * 60)
print("KAVACH 6.0 — LIVE API TEST SUITE")
print(f"Timestamp: {datetime.datetime.now().isoformat()}")
print("=" * 60)

# ─── CORE HEALTH ────────────────────────────────────────────
print("\n--- CORE HEALTH ---")
r_health = test('Health Check', 'GET', '/api/health')
if r_health:
    data = r_health.json()
    print(f"  Version: {data.get('version')} | Status: {data.get('status')}")
test('System Status', 'GET', '/api/system/status')
r_ai = test('AI Status', 'GET', '/api/ai/status')
if r_ai and r_ai.status_code == 200:
    ai = r_ai.json()
    print(f"  AI State: {ai.get('lifecycle_state')} | Model: {ai.get('selected_model', 'None')}")
test('RAG Status', 'GET', '/api/rag/status')
test('Ollama Status', 'GET', '/api/system/ollama')

# ─── ASSESSMENTS ────────────────────────────────────────────
print("\n--- ASSESSMENTS ---")
test('List Assessments', 'GET', '/api/assessments')
r = test('Create Assessment', 'POST', '/api/assessments', {
    'name': 'KAVACH 6.0 Live Validation Test',
    'target_url': 'http://testphp.vulnweb.com',
    'description': 'Real-world live API validation - authorized test target',
    'environment': 'Testing Environment',
    'scope': 'Full Application - OWASP Top 10',
    'authorization_confirmed': True,
    'modules_enabled': ['Authentication', 'API Security', 'Security Headers', 'Input Validation'],
    'is_demo': False
})
assessment_id = None
if r and r.status_code in [200, 201]:
    asm = r.json()
    assessment_id = asm.get('id')
    print(f"  Created: {assessment_id} | {asm.get('name')}")

# ─── WORLD MONITOR ──────────────────────────────────────────
print("\n--- WORLD MONITOR ---")
r_wm = test('World Monitor Events', 'GET', '/api/world-monitor/events')
if r_wm and r_wm.status_code == 200:
    wm_data = r_wm.json()
    events = wm_data.get('events', wm_data if isinstance(wm_data, list) else [])
    print(f"  Events count: {len(events)}")
test('World Monitor Sources', 'GET', '/api/world-monitor/sources')
r_refresh = test('World Monitor Refresh', 'POST', '/api/world-monitor/refresh', {})
if r_refresh and r_refresh.status_code == 200:
    refresh_data = r_refresh.json()
    print(f"  Refresh mode: {refresh_data.get('mode', '?')} | {refresh_data.get('message', '')[:80]}")

# ─── KNOWLEDGE BASE ─────────────────────────────────────────
print("\n--- KNOWLEDGE BASE ---")
r_kb = test('Knowledge Base List', 'GET', '/api/knowledge')
if r_kb and r_kb.status_code == 200:
    kb_data = r_kb.json()
    count = len(kb_data) if isinstance(kb_data, list) else kb_data.get('count', '?')
    print(f"  Knowledge entries: {count}")

# ─── EVIDENCE ────────────────────────────────────────────────
print("\n--- EVIDENCE ---")
r_evd = test('Evidence List', 'GET', '/api/evidence')
if r_evd and r_evd.status_code == 200:
    evd_data = r_evd.json()
    evd_count = len(evd_data) if isinstance(evd_data, list) else '?'
    print(f"  Evidence records: {evd_count}")

# ─── FINDINGS ────────────────────────────────────────────────
print("\n--- FINDINGS ---")
r_findings = test('Findings List', 'GET', '/api/findings')
finding_id = None
if r_findings and r_findings.status_code == 200:
    findings = r_findings.json()
    if isinstance(findings, list) and len(findings) > 0:
        finding_id = findings[0].get('id')
        print(f"  Total findings: {len(findings)} | First: [{finding_id}] {findings[0].get('title','?')[:60]}")

# ─── PORTABLE SCANNER ────────────────────────────────────────
print("\n--- PORTABLE SCANNER ---")
test('Portable Permissions', 'GET', '/api/portable/permissions')
test('Portable Demo Samples', 'GET', '/api/portable/demo-samples')
test('Portable Results', 'GET', '/api/portable/results')

# ─── TEAM ────────────────────────────────────────────────────
print("\n--- TEAM ---")
test('Team Members', 'GET', '/api/team/members')
test('Team Assignments', 'GET', '/api/team/assignments')
if finding_id:
    r_notes = test('Team Notes (POST)', 'POST', '/api/team/notes', {
        'finding_id': finding_id,
        'notes': 'KAVACH 6.0 audit validation note — generated by live test suite'
    })
    if r_notes and r_notes.status_code == 200:
        print(f"  Note appended to finding {finding_id}")

# ─── EXPERIENCE / INSTITUTIONAL MEMORY ───────────────────────
print("\n--- EXPERIENCE / INSTITUTIONAL MEMORY ---")
test('Experience Summary', 'GET', '/api/experience/summary')
test('Re-verifications', 'GET', '/api/experience/re-verifications')
test('False Positives', 'GET', '/api/experience/false-positives')

# ─── TEST CENTER ─────────────────────────────────────────────
print("\n--- TEST CENTER ---")
r_tc = test('Test Center Suites', 'GET', '/api/test-center/suites')
if r_tc and r_tc.status_code == 200:
    suites_raw = r_tc.json()
    suites = suites_raw if isinstance(suites_raw, list) else suites_raw.get('suites', [])
    print(f"  Suites: {[s.get('name', s.get('id', '?')) for s in suites]}")

# ─── SYSTEM ──────────────────────────────────────────────────
print("\n--- SYSTEM ---")
test('System Geolocate', 'GET', '/api/system/geolocate')
test('System Audit', 'GET', '/api/system/audit')

# ─── ASSESSMENT-SPECIFIC TESTS ───────────────────────────────
if assessment_id:
    print(f"\n--- ASSESSMENT-SPECIFIC (id={assessment_id}) ---")
    test('Get Assessment Detail', 'GET', f'/api/assessments/{assessment_id}')
    test('Risk Prioritization', 'GET', f'/api/risk/prioritization/{assessment_id}')
    test('Forensic Audit Trail', 'GET', f'/api/forensic/audit-trail/{assessment_id}')
    test('Discovery', 'GET', f'/api/discovery/{assessment_id}')
    test('Assessment Posture', 'GET', f'/api/assessments/{assessment_id}/posture')
    test('Report JSON', 'GET', f'/api/reports/{assessment_id}')

# ─── AI ENDPOINTS ────────────────────────────────────────────
print("\n--- AI ENDPOINTS ---")
if finding_id:
    r_risk = test('AI Explain Risk', 'POST', '/api/ai/explain-risk', {'finding_id': finding_id}, timeout=90)
    if r_risk and r_risk.status_code == 200:
        risk_data = r_risk.json()
        print(f"  Risk explanation generated for: {risk_data.get('risk_explanation', {}).get('title', '?')[:60]}")

    r_5pt = test('AI Explain 5 Points', 'POST', '/api/ai/explain-5-points', {'finding_id': finding_id}, timeout=90)
    if r_5pt and r_5pt.status_code == 200:
        print(f"  5-point explanation: {str(r_5pt.text)[:80]}")

if assessment_id:
    r_summary = test('AI Assessment Summary', 'POST', '/api/ai/assessment-summary',
                     {'assessment_id': assessment_id}, timeout=90)

# ─── RAG ─────────────────────────────────────────────────────
print("\n--- RAG ---")
r_rag = test('RAG Query', 'POST', '/api/rag/query',
             {'query': 'SQL injection remediation'}, timeout=60)
if r_rag and r_rag.status_code == 200:
    print(f"  RAG response: {str(r_rag.text)[:100]}")

# ─── URL CHECK ───────────────────────────────────────────────
print("\n--- URL CHECK ---")
r_scan = test('URL Check Scan', 'POST', '/api/url-check/scan', {'url': 'https://example.com'})
if r_scan and r_scan.status_code == 200:
    scan_data = r_scan.json()
    print(f"  URL check result: {scan_data.get('result', scan_data.get('status', '?'))}")
test('URL Check Latest', 'GET', '/api/url-check/latest')

# ─── FINAL SUMMARY ───────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for r in results if r['pass'])
failed_list = [r for r in results if not r['pass']]
total = len(results)
print(f"FINAL SUMMARY: {passed}/{total} PASSED  |  {total-passed} FAILED")
print("=" * 60)
if failed_list:
    print("\nFAILED ENDPOINTS:")
    for f in failed_list:
        err = f.get('error', '')
        print(f"  - [{f['status']}] {f['method']} {f['url']}  ({f['name']}){' — ' + err if err else ''}")

# Write JSON results
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/api_test_results.json', 'w') as fp:
    json.dump({
        'timestamp': datetime.datetime.now().isoformat(),
        'passed': passed,
        'total': total,
        'pass_rate': f"{passed/total*100:.1f}%",
        'results': results
    }, fp, indent=2)
print(f"\nResults saved to scratch/api_test_results.json")
