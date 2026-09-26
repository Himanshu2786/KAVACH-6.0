import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kavach.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("PRAGMA table_info(assessments)")
cols = [row[1] for row in c.fetchall()]
if "assessment_type" not in cols:
    print("Adding assessment_type column to assessments...")
    c.execute("ALTER TABLE assessments ADD COLUMN assessment_type TEXT DEFAULT 'GENERIC_ASSESSMENT'")
    conn.commit()
else:
    print("Column assessment_type exists.")

# Mark test fixture runs as TEST_FIXTURE
c.execute("UPDATE assessments SET assessment_type = 'TEST_FIXTURE' WHERE id LIKE 'KAVACH-WM-%' AND id != 'KAVACH-WM-20260922-2FC1'")

# Explicitly mark dedicated empirical World Monitor assessment
c.execute("UPDATE assessments SET assessment_type = 'WORLD_MONITOR_EMPIRICAL' WHERE id = 'KAVACH-WM-20260922-2FC1'")

# Explicitly mark generic assessment
c.execute("UPDATE assessments SET assessment_type = 'GENERIC_ASSESSMENT' WHERE id = 'ASM-2572377F'")

# Explicitly mark demo assessments
c.execute("UPDATE assessments SET assessment_type = 'DEMO' WHERE is_demo = 1 OR id LIKE 'ASM-DEMO-%'")

conn.commit()

c.execute("SELECT id, name, target_url, started_at, is_demo, assessment_type FROM assessments WHERE id IN ('KAVACH-WM-20260922-2FC1', 'ASM-2572377F', 'ASM-DEMO-001', 'KAVACH-WM-20260922-F092')")
rows = c.fetchall()
for r in rows:
    print(r)

conn.close()
