# KAVACH 6.0 — Complete Dependencies & Selection Rationale

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation  
> **Package Files:** `requirements.txt`, `backend/requirements.txt`, `frontend/package.json`  

---

## 1. Python Backend Dependencies

| Package | Version | Purpose | Selection Rationale | Alternative Considered & Reason Not Selected | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`fastapi`** | `>=0.115.0` | Async REST API Framework | Native async I/O, automatic OpenAPI documentation, high performance. | Flask (synchronous I/O blocks long-running scanner tasks). | `IMPLEMENTED + TESTED LOCALLY` |
| **`uvicorn`** | `>=0.30.0` | Production ASGI Web Server | Lightweight, high-throughput ASGI server bound safely to `127.0.0.1`. | Gunicorn (unnecessary deployment complexity on Windows). | `IMPLEMENTED + TESTED LOCALLY` |
| **`pydantic`** | `>=2.8.0` | Data Validation & Schemas | Fast C-based validation, schema enforcement, clean JSON serialization. | Marshmallow (slower execution, lacks native FastAPI integration). | `IMPLEMENTED + TESTED LOCALLY` |
| **`sqlalchemy`** | `>=2.0.30` | Declarative Database ORM | Type-safe declarative schema modeling, clean relationship cascades. | Raw SQL (harder to manage schema migrations across features). | `IMPLEMENTED + TESTED LOCALLY` |
| **`httpx`** | `>=0.27.0` | Async HTTP Client | Full async/await client support for URL scanning and public feed ingestion. | `requests` (synchronous only, blocks async FastAPI worker loop). | `IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR` |
| **`numpy`** | `>=1.26.0` | Vector Math & Similarity | Vectorized matrix operations for RAG vector search without heavy external dependencies. | Pinecone / Milvus (requires external servers or paid cloud API keys). | `IMPLEMENTED + TESTED LOCALLY` |
| **`pytest`** | `>=8.0.0` | Automated Test Framework | Industry-standard test runner with rich assertion reporting and fixture support. | `unittest` (more verbose test syntax, less extensible plugins). | `IMPLEMENTED + TESTED LOCALLY` |

---

## 2. Frontend Dependencies (React & Vite)

| Package | Version | Purpose | Selection Rationale | Alternative Considered & Reason Not Selected | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`react`** | `^19.2.8` | UI Component Framework | Declarative component model, virtual DOM diffing, modern React hooks. | Vue / Angular (team expertise and Three.js ecosystem integration). | `IMPLEMENTED + TESTED LOCALLY` |
| **`typescript`** | `~6.0.2` | Compile-Time Type Safety | Prevents runtime JavaScript errors, provides strict API contract types. | Vanilla JS (higher error rate in complex security dashboards). | `IMPLEMENTED + TESTED LOCALLY` |
| **`vite`** | `^8.2.2` | Frontend Build Engine | Instant HMR development server, optimized ESM bundling. | Webpack (slow cold start and rebuild times). | `IMPLEMENTED + TESTED LOCALLY` |
| **`three`** | `^0.186.0` | 3D WebGL Earth Globe | Hardware-accelerated 3D sphere with glowing shaders and threat arcs. | 2D Leaflet / Mapbox (lacks futuristic security command center aesthetics). | `IMPLEMENTED + TESTED LOCALLY` |
| **`tailwindcss`** | `^4.3.3` | Responsive Styling | Utility-first CSS framework with rapid responsive layout styling. | Bootstrap (rigid monolithic classes, harder to customize dark glass UI). | `IMPLEMENTED + TESTED LOCALLY` |
| **`lucide-react`** | `^1.42.0` | Cybersecurity Icon Set | Lightweight, clean, modern SVG icons for security metrics and findings. | FontAwesome (larger bundle size, restrictive licensing). | `IMPLEMENTED + TESTED LOCALLY` |
| **`clsx`** / **`tailwind-merge`** | `^2.1.1` / `^3.6.0` | Dynamic Class Composition | Conflict-free conditional CSS class merging for glassmorphic components. | Manual string concatenation (error-prone style collisions). | `IMPLEMENTED + TESTED LOCALLY` |

---

## 3. Local External Service Dependencies

| Component | Minimum Version | Protocol & Port | Purpose | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Ollama** | `>=0.3.0` | HTTP `127.0.0.1:11434` | Local LLM inference hosting `phi3:mini` | Fallback to deterministic rule-based synthesis |
| **SQLite 3** | Standard (Python built-in) | Embedded C Library | Relational storage (`kavach.db`) with WAL mode | In-memory SQLite if file system permissions restricted |
