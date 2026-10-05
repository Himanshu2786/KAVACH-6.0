import sqlite3

con = sqlite3.connect('kavach.db')
cur = con.cursor()

cur.execute("SELECT id, assessment_id, event_type, timestamp, description FROM audit_events WHERE timestamp LIKE '2026-09-28T22:%' ORDER BY timestamp ASC")
rows = cur.fetchall()
print("Audit events around 22:00 on Sept 28:", len(rows))
for r in rows:
    print(" ", r)

# Also check assessments created around that time
cur.execute("SELECT id, target_url, created_at, started_at FROM assessments WHERE started_at LIKE '2026-09-28T22:%' OR created_at LIKE '2026-09-28T22:%'")
asm_rows = cur.fetchall()
print("Assessments around 22:00 on Sept 28:", len(asm_rows))
for r in asm_rows:
    print(" ", r)

con.close()
