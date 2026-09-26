import sqlite3
import os

def migrate():
    db_path = "kavach.db"
    if not os.path.exists(db_path):
        print("No existing DB to migrate.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Add missing columns to evidence_records
    cur.execute("PRAGMA table_info(evidence_records)")
    existing_cols = [r[1] for r in cur.fetchall()]

    new_cols = [
        ("what_found", "TEXT DEFAULT ''"),
        ("why_matters", "TEXT DEFAULT ''"),
        ("where_found", "VARCHAR(255) DEFAULT ''"),
        ("confidence_level", "VARCHAR(50) DEFAULT 'HIGH'"),
        ("verification_command", "TEXT DEFAULT ''"),
        ("expected_output", "TEXT DEFAULT ''"),
        ("observed_output", "TEXT DEFAULT ''"),
        ("evidence_nature", "VARCHAR(50) DEFAULT 'REAL EVIDENCE'")
    ]

    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            print(f"Adding column {col_name} to evidence_records...")
            cur.execute(f"ALTER TABLE evidence_records ADD COLUMN {col_name} {col_type}")

    # 2. Create re_verifications table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS re_verifications (
        id VARCHAR(50) PRIMARY KEY,
        finding_id VARCHAR(50),
        timestamp VARCHAR(50),
        previous_status VARCHAR(50),
        new_status VARCHAR(50),
        command_executed TEXT,
        output_before TEXT,
        output_after TEXT,
        summary TEXT,
        FOREIGN KEY(finding_id) REFERENCES findings(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database migration completed successfully.")

if __name__ == "__main__":
    migrate()
