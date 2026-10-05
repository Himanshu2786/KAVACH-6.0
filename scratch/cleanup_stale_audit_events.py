import sqlite3

con = sqlite3.connect('kavach.db')
cur = con.cursor()

# Verify before deleting
cur.execute("SELECT id, assessment_id, event_type FROM audit_events WHERE assessment_id = 'test-asm'")
rows = cur.fetchall()
print(f"Found {len(rows)} stale events with assessment_id='test-asm':")
for r in rows:
    print(" ", r)

if len(rows) > 0:
    cur.execute("DELETE FROM audit_events WHERE assessment_id = 'test-asm'")
    con.commit()
    print(f"Successfully deleted {cur.rowcount} stale records from kavach.db.")

con.close()
