import pathlib, os, sqlite3, json

cwd = pathlib.Path('c:/Users/Himanshu Raj/OneDrive/Desktop/KHAALI KAVACH/KAVACH 6.0')

# Check all source path candidates the engine uses
candidates = [
    cwd / 'worldmonitor',
    cwd.parent / 'worldmonitor',
]
env_path = os.environ.get('WORLDMONITOR_SOURCE_PATH', '')
if env_path:
    candidates.insert(0, pathlib.Path(env_path))

print("=== Source path candidates ===")
for p in candidates:
    try:
        print(f"  {p.resolve()} => exists={p.exists()}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Query the DB for source_path in audit events for 0541
conn = sqlite3.connect(str(cwd / 'kavach.db'))
conn.row_factory = sqlite3.Row
c = conn.cursor()
print()
print("=== Audit events for KAVACH-WM-20260922-0541 (ASSESSMENT_STARTED / SOURCE_SELECTED) ===")
rows = c.execute(
    "SELECT id, event_type, details_json FROM audit_events WHERE assessment_id = ? AND event_type IN ('ASSESSMENT_STARTED', 'SOURCE_SELECTED')",
    ("KAVACH-WM-20260922-0541",)
).fetchall()
for r in rows:
    details = json.loads(r["details_json"] or "{}")
    etype = r["event_type"]
    src = details.get("source_path", "NOT IN DETAILS")
    commit = details.get("commit_sha", "N/A")
    print(f"  [{etype}] source_path={src} commit_sha={commit}")

if not rows:
    print("  No ASSESSMENT_STARTED / SOURCE_SELECTED events found for this assessment.")
    # Show all audit events for this assessment
    all_rows = c.execute(
        "SELECT id, event_type, details_json FROM audit_events WHERE assessment_id = ? LIMIT 10",
        ("KAVACH-WM-20260922-0541",)
    ).fetchall()
    print("  All audit events (first 10):")
    for r in all_rows:
        print(f"    [{r['event_type']}] id={r['id']}")

print()
print("=== Finding WM-SRC-SRC_DEBUG_ENABLED-0541-1 full columns ===")
# Get all columns for the finding
import sqlite3
conn2 = sqlite3.connect(str(cwd / 'kavach.db'))
conn2.row_factory = sqlite3.Row
c2 = conn2.cursor()
cols = [col[1] for col in c2.execute("PRAGMA table_info(findings)").fetchall()]
print(f"  Finding columns: {cols}")
row = c2.execute(
    "SELECT * FROM findings WHERE id = ?", ("WM-SRC-SRC_DEBUG_ENABLED-0541-1",)
).fetchone()
if row:
    for col in cols:
        val = row[col]
        if val and len(str(val)) > 120:
            val = str(val)[:120] + "..."
        print(f"  {col}: {val}")
else:
    print("  NOT FOUND")

print()
print("=== Evidence record EV-WM-SRC-SRC_DEBUG_ENABLED-0541-1 full columns ===")
ev_cols = [col[1] for col in c2.execute("PRAGMA table_info(evidence_records)").fetchall()]
ev_row = c2.execute(
    "SELECT * FROM evidence_records WHERE id = ?", ("EV-WM-SRC-SRC_DEBUG_ENABLED-0541-1",)
).fetchone()
if ev_row:
    for col in ev_cols:
        val = ev_row[col]
        if val and len(str(val)) > 200:
            val = str(val)[:200] + "..."
        print(f"  {col}: {val}")
else:
    print("  NOT FOUND")

conn.close()
conn2.close()
