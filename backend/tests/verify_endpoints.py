import sys, os
sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
res = client.get('/api/assessments/world-monitor/latest')
wm_id = res.json().get('id')
print(f'GET /api/assessments/world-monitor/latest: {res.status_code}, id={wm_id}, findings={res.json().get("total_findings")}')

res_f = client.get(f'/api/findings?assessment_id={wm_id}')
print(f'GET /api/findings: {res_f.status_code}, count={len(res_f.json())}')

res_e = client.get(f'/api/evidence?assessment_id={wm_id}')
print(f'GET /api/evidence: {res_e.status_code}, count={len(res_e.json())}')

res_r = client.get(f'/api/risk/prioritization/{wm_id}')
print(f'GET /api/risk/prioritization: {res_r.status_code}, count={len(res_r.json()) if res_r.status_code == 200 else res_r.text}')

res_rep = client.get(f'/api/reports/{wm_id}')
findings_in_rep = len(res_rep.json().get('findings_detail', [])) if res_rep.status_code == 200 else 0
print(f'GET /api/reports: {res_rep.status_code}, findings in report={findings_in_rep}')

res_url = client.get('/api/url-check/latest')
print(f'GET /api/url-check/latest: {res_url.status_code}, run_id={res_url.json().get("run_id")}, parent={res_url.json().get("parent_assessment_id")}')
