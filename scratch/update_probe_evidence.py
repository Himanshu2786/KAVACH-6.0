import sqlite3
import json

conn = sqlite3.connect('kavach.db')
c = conn.cursor()

# 1. Verify EV-WM-API-DOCS-A018 exists
c.execute('SELECT id, integrity_hash FROM evidence_records WHERE id = ?', ('EV-WM-API-DOCS-A018',))
orig_ev = c.fetchone()
print('Original EV record:', orig_ev)

# 2. Insert EV-WM-API-DOCS-A018-GET if not exists
raw_payload = {
    'endpoint': 'https://www.worldmonitor.app/openapi.json',
    'http_method': 'GET',
    'http_status': 200,
    'content_type': 'application/json; charset=utf-8',
    'schema_detected': True,
    'schema_version': '3.1.0',
    'schema_title': 'WorldMonitor API',
    'servers': [{'url': 'https://api.worldmonitor.app'}],
    'body_length': 949532,
    'body_sha256': 'dc1b4710a6c560fa9d4f30d9b2b55f6e71ae6467b8f66890f04558a7bde93c13',
    'auth_state': 'UNAUTHENTICATED',
    'authz_state': 'PUBLIC',
    'observed_behavior': 'HTTP 200 OK with OpenAPI 3.1.0 schema document delivered (Content-Type: application/json; charset=utf-8, Body SHA-256: dc1b4710a6c560fa9d4f30d9b2b55f6e71ae6467b8f66890f04558a7bde93c13).',
    'expected_behavior': 'HTTP 401/403/404 on production deployments.',
    'actual_behavior': 'OpenAPI 3.1.0 specification is readable by unauthenticated users, disclosing endpoint paths and request structures.'
}

c.execute('SELECT id FROM evidence_records WHERE id = ?', ('EV-WM-API-DOCS-A018-GET',))
if not c.fetchone():
    c.execute('''
        INSERT INTO evidence_records (
            id, finding_id, evidence_type, source, timestamp, description,
            raw_data, validation_result, integrity_hash, is_demo, what_found,
            why_matters, where_found, confidence_level, verification_command,
            expected_output, observed_output, evidence_nature
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'EV-WM-API-DOCS-A018-GET',
        'WM-API-DOCS-A018',
        'API Documentation Public Accessibility Probe (GET)',
        'LIVE_PROBE',
        '2026-09-23T12:50:00.000000+00:00',
        'Unauthenticated GET request to \'/openapi.json\' returned HTTP 200 with OpenAPI 3.1.0 schema document.',
        json.dumps(raw_payload),
        'CONFIRMED',
        'dc1b4710a6c560fa9d4f30d9b2b55f6e71ae6467b8f66890f04558a7bde93c13',
        0,
        'Unauthenticated GET request to \'/openapi.json\' returned HTTP 200 with OpenAPI 3.1.0 schema document.',
        'Category: API security',
        'https://www.worldmonitor.app/openapi.json',
        'HIGH',
        'Invoke-WebRequest -Uri "https://www.worldmonitor.app/openapi.json" -Method Get',
        'HTTP 401 / 403 / 404 (Restricted in production)',
        'HTTP 200 OK — OpenAPI 3.1.0 schema document delivered (application/json; charset=utf-8, SHA-256: dc1b4710a6c560fa9d4f30d9b2b55f6e71ae6467b8f66890f04558a7bde93c13).',
        'REAL EVIDENCE'
    ))
    print('Inserted EV-WM-API-DOCS-A018-GET')
else:
    print('EV-WM-API-DOCS-A018-GET already exists')

# 3. Update Finding WM-API-DOCS-A018 verification_json and evidence_ids_json
verification_dict = {
    'command': 'Invoke-WebRequest -Uri "https://www.worldmonitor.app/openapi.json" -Method Get',
    'expected': 'HTTP 401 / 403 / 404 (Restricted)',
    'before_result': 'HTTP 200 OK — OpenAPI 3.1.0 schema document delivered (application/json; charset=utf-8)',
    'after_result': 'Pending verification'
}

c.execute('''
    UPDATE findings
    SET evidence_ids_json = ?,
        verification_json = ?,
        safe_poc = ?
    WHERE id = ?
''', (
    json.dumps(['EV-WM-API-DOCS-A018', 'EV-WM-API-DOCS-A018-GET']),
    json.dumps(verification_dict),
    'Invoke-WebRequest -Uri "https://www.worldmonitor.app/openapi.json" -Method Get',
    'WM-API-DOCS-A018'
))

conn.commit()

# Verify records
c.execute('SELECT id, integrity_hash, verification_command FROM evidence_records WHERE finding_id = ?', ('WM-API-DOCS-A018',))
print('Evidence records for WM-API-DOCS-A018:')
for r in c.fetchall():
    print('  ', r)

c.execute('SELECT id, verification_json, evidence_ids_json FROM findings WHERE id = ?', ('WM-API-DOCS-A018',))
print('Finding WM-API-DOCS-A018:', c.fetchone())
conn.close()
