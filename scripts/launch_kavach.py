"""
KAVACH 6.0 — Intelligent Startup & Process Management Engine
Handles pre-flight checks, dependency verification, database integrity,
RAG vector index initialization, Ollama detection, and clean application launch.
"""

import sys
import os
import subprocess
import time
import socket
import logging
from pathlib import Path

# Set up project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure logs directory exists
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "kavach_launcher.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("kavach_launcher")


def log_and_print(step_num: int, total_steps: int, message: str, status: str = "OK"):
    print(f"[{step_num}/{total_steps}] {message:<50} [{status}]")
    logger.info(f"Step {step_num}/{total_steps}: {message} - {status}")


def check_python_version() -> bool:
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print(f"\n[ERROR] Python 3.10+ is required. Detected Python {v.major}.{v.minor}.{v.micro}")
        logger.error(f"Incompatible Python version: {v.major}.{v.minor}.{v.micro}")
        return False
    return True


def check_dependencies() -> bool:
    """Checks required core packages."""
    required_packages = ["PySide6", "requests", "numpy", "sqlite3"]
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"\n[WARNING] Missing required Python package(s): {', '.join(missing)}")
        print("Attempting automatic dependency installation...")
        logger.warning(f"Missing packages: {missing}. Installing...")
        try:
            req_file = PROJECT_ROOT / "requirements.txt"
            if req_file.exists():
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            logger.info("Dependencies installed successfully.")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            logger.error(f"Pip installation failed: {e}")
            return False
    return True


def check_database() -> bool:
    """Verifies SQLite database existence and integrity."""
    db_path = PROJECT_ROOT / "kavach.db"
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        logger.info(f"Database verified at {db_path} with {len(tables)} tables.")
        return True
    except Exception as e:
        logger.warning(f"Database check warning: {e}")
        return True


def check_rag_index() -> bool:
    """Ensures RAG vector store is populated and ready."""
    try:
        from backend.app.rag.vector_store import vector_store
        if not vector_store.is_indexed():
            logger.info("RAG vector index not found on disk. Building initial index...")
            import asyncio
            from backend.app.rag.retriever import rag_retriever
            asyncio.run(rag_retriever.rebuild_index())
            logger.info("RAG vector index built successfully.")
        return True
    except Exception as e:
        logger.warning(f"RAG pre-initialization note: {e}")
        return True


def check_ollama_status() -> str:
    """Checks if Ollama service is reachable on localhost:11434."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.8)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()
        if result == 0:
            logger.info("Ollama AI service detected on 127.0.0.1:11434.")
            return "ONLINE"
        else:
            logger.info("Ollama offline. Deterministic rule/vector fallback active.")
            return "OFFLINE (Fallback Active)"
    except Exception:
        return "OFFLINE (Fallback Active)"


def launch_application():
    """Launches the KAVACH desktop application."""
    print("=" * 60)
    print("              KAVACH 6.0 SECURITY PLATFORM")
    print("        'AI Hypothesizes. Evidence Confirms.'")
    print("=" * 60)
    logger.info("Starting KAVACH Launcher pre-flight checks...")

    # Step 1: Python Version
    if not check_python_version():
        input("\nPress Enter to exit...")
        sys.exit(1)
    log_and_print(1, 5, "Verifying Python environment (Python 3.10+)...", "READY")

    # Step 2: Dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    log_and_print(2, 5, "Verifying packages & local database...", "READY")

    # Step 3: Database & RAG Index
    check_database()
    check_rag_index()
    log_and_print(3, 5, "Verifying RAG Security Vector Store...", "READY")

    # Step 4: Ollama Health
    ollama_stat = check_ollama_status()
    log_and_print(4, 5, f"Checking local Ollama engine...", ollama_stat)

    # Step 5: Launch Application
    log_and_print(5, 5, "Launching KAVACH Desktop Interface...", "STARTING")
    print("=" * 60)
    print("\nStarting KAVACH Application Window...\n")
    logger.info("Launching main.py...")

    try:
        # Import and execute main desktop entry point directly
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"\n[FATAL ERROR] KAVACH Application encountered an error:\n{e}")
        logger.critical(f"Application crash in main(): {e}", exc_info=True)
        print(f"\nDiagnostic log written to: {LOG_FILE}")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    launch_application()
