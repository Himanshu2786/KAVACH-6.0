from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

# Configure database engine with connection pooling for PostgreSQL and single-thread safety for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL / MySQL production pooling
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=int(getattr(settings, "POSTGRES_POOL_SIZE", 10)),
        max_overflow=int(getattr(settings, "POSTGRES_MAX_OVERFLOW", 20)),
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def migrate_schema(target_engine):
    """Ensure newly added columns exist in existing databases without requiring drop/re-create."""
    try:
        import backend.app.models.models  # Ensure all SQLAlchemy models are registered
        Base.metadata.create_all(bind=target_engine)
        inspector = inspect(target_engine)
        table_names = inspector.get_table_names()
        with target_engine.connect() as conn:
            if "users" in table_names:
                columns = [c["name"] for c in inspector.get_columns("users")]
                if "username" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50)"))
                    if "user_id" in columns:
                        conn.execute(text("UPDATE users SET username = user_id WHERE username IS NULL OR username = ''"))
                if "user_id" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN user_id VARCHAR(50)"))
                    if "username" in columns:
                        conn.execute(text("UPDATE users SET user_id = username WHERE user_id IS NULL OR user_id = ''"))
                if "hashed_password" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"))
                    if "password_hash" in columns:
                        conn.execute(text("UPDATE users SET hashed_password = password_hash WHERE hashed_password IS NULL OR hashed_password = ''"))
                if "password_hash" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                    if "hashed_password" in columns:
                        conn.execute(text("UPDATE users SET password_hash = hashed_password WHERE password_hash IS NULL OR password_hash = ''"))
                if "role" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'team_member'"))
                if "full_name" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(100) DEFAULT ''"))
                if "is_active" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                if "created_at" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN created_at VARCHAR(50) DEFAULT ''"))
                if "first_login_at" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN first_login_at VARCHAR(50) DEFAULT ''"))
                if "last_login_at" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at VARCHAR(50) DEFAULT ''"))
                if "last_active_at" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_active_at VARCHAR(50) DEFAULT ''"))

            if "assessments" in table_names:
                columns = [c["name"] for c in inspector.get_columns("assessments")]
                if "owner_id" not in columns:
                    conn.execute(text("ALTER TABLE assessments ADD COLUMN owner_id VARCHAR(50)"))

            if "audit_events" in table_names:
                columns = [c["name"] for c in inspector.get_columns("audit_events")]
                if "module" not in columns:
                    conn.execute(text("ALTER TABLE audit_events ADD COLUMN module VARCHAR(50) DEFAULT 'CORE'"))
                if "evidence_id" not in columns:
                    conn.execute(text("ALTER TABLE audit_events ADD COLUMN evidence_id VARCHAR(64)"))
                if "status" not in columns:
                    conn.execute(text("ALTER TABLE audit_events ADD COLUMN status VARCHAR(30) DEFAULT 'SUCCESS'"))
            
            if "findings" in table_names:
                columns = [c["name"] for c in inspector.get_columns("findings")]
                if "assigned_to" not in columns:
                    conn.execute(text("ALTER TABLE findings ADD COLUMN assigned_to VARCHAR(100) DEFAULT 'Unassigned'"))
                if "team_notes" not in columns:
                    conn.execute(text("ALTER TABLE findings ADD COLUMN team_notes TEXT DEFAULT ''"))
                if "triage_status" not in columns:
                    conn.execute(text("ALTER TABLE findings ADD COLUMN triage_status VARCHAR(50) DEFAULT 'NEW'"))

            if "re_verifications" in table_names:
                columns = [c["name"] for c in inspector.get_columns("re_verifications")]
                if "target_url" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN target_url VARCHAR(255) DEFAULT ''"))
                if "before_evidence_id" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN before_evidence_id VARCHAR(50) DEFAULT ''"))
                if "after_evidence_id" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN after_evidence_id VARCHAR(50) DEFAULT ''"))
                if "before_evidence_hash" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN before_evidence_hash VARCHAR(64) DEFAULT ''"))
                if "after_evidence_hash" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN after_evidence_hash VARCHAR(64) DEFAULT ''"))
                if "state_diff" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN state_diff TEXT DEFAULT ''"))
                if "verification_verdict" not in columns:
                    conn.execute(text("ALTER TABLE re_verifications ADD COLUMN verification_verdict VARCHAR(50) DEFAULT 'VERIFIED_REMEDIATED'"))

            if "user_feedbacks" in table_names:
                columns = [c["name"] for c in inspector.get_columns("user_feedbacks")]
                if "updated_at" not in columns:
                    conn.execute(text("ALTER TABLE user_feedbacks ADD COLUMN updated_at VARCHAR(50) DEFAULT ''"))
            conn.commit()
    except Exception as e:
        print(f"[DB MIGRATION WARNING]: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
