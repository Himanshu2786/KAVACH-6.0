# KAVACH 6.0 — Database & Data Architecture

This directory documents the persistent data models and stores for KAVACH 6.0.

## Storage Architecture
- **Runtime SQLite Database**: `kavach.db` (Located at repository root for live local execution and dual-client sync)
- **Production Database**: PostgreSQL (Configured via `DATABASE_URL`)
- **Data Seeds**: `backend/app/data/seed_data.py`
- **ORM Schemas**: `backend/app/schemas/schemas.py` and `backend/app/models/models.py`
