import sqlite3
import json

conn = sqlite3.connect('kavach.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== FINDING: WM-SRC-SRC_DEBUG_ENABLED-0541-1 ===")
rows = c.execute(
    "SELECT id, assessment_id, title, category, status, evidence_status, affected_component, base_severity, priority_score "
    "FROM findings WHERE id = ?", ("WM-SRC-SRC_DEBUG_ENABLED-0541-1",)
).fetchall()
if rows:
    for r in rows:
        for k in r.keys():
            print(f"  {k}: {r[k]}")
else:
    print("  NOT FOUND")

print()
print("=== EVIDENCE: EV-WM-SRC-SRC_DEBUG_ENABLED-0541-1 ===")
rows = c.execute(
    "SELECT id, finding_id, evidence_type, validation_result, confidence_level, evidence_nature, what_found "
    "FROM evidence_records WHERE id = ?", ("EV-WM-SRC-SRC_DEBUG_ENABLED-0541-1",)
).fetchall()
if rows:
    for r in rows:
        for k in r.keys():
            print(f"  {k}: {r[k]}")
else:
    print("  NOT FOUND")

print()
print("=== ALL findings for assessment KAVACH-WM-20260922-0541 ===")
rows = c.execute(
    "SELECT id, title, status, evidence_status, category FROM findings WHERE assessment_id = ?",
    ("KAVACH-WM-20260922-0541",)
).fetchall()
for r in rows:
    print(dict(r))

print()
print("=== ALL evidence_records for finding_id LIKE %0541% ===")
rows = c.execute(
    "SELECT id, finding_id, evidence_type, validation_result, evidence_nature FROM evidence_records WHERE finding_id LIKE ?",
    ("%0541%",)
).fetchall()
for r in rows:
    print(dict(r))

print()
print("=== FINDING WM-API-DOCS-0541 (valid runtime) ===")
rows = c.execute(
    "SELECT id, status, evidence_status, base_severity, priority_score FROM findings WHERE id = ?",
    ("WM-API-DOCS-0541",)
).fetchall()
if rows:
    for r in rows:
        for k in r.keys():
            print(f"  {k}: {r[k]}")
else:
    print("  NOT FOUND")

print()
print("=== Assessment KAVACH-WM-20260922-0541 ===")
rows = c.execute(
    "SELECT id, name, target_url, environment, status FROM assessments WHERE id = ?",
    ("KAVACH-WM-20260922-0541",)
).fetchall()
if rows:
    for r in rows:
        for k in r.keys():
            print(f"  {k}: {r[k]}")
else:
    print("  NOT FOUND - searching partial...")
    rows2 = c.execute(
        "SELECT id, name, target_url FROM assessments WHERE id LIKE ?",
        ("%0541%",)
    ).fetchall()
    for r in rows2:
        print(dict(r))

conn.close()
