"""
KAVACH 6.0 Desktop - Centralized Runtime Configuration and Path Resolver.
Handles asset, data, and database paths seamlessly for both source execution and PyInstaller bundled EXEs.
"""

import sys
import os
from pathlib import Path

# Application Metadata
APP_NAME = "KAVACH"
APP_VERSION = "5.0"
APP_TITLE = "KAVACH 6.0 — Sovereign Security Intelligence Platform"
ORG_NAME = "KAVACH Security"

def get_base_dir() -> Path:
    """
    Returns base directory for bundled resources (icons, assets, demo fixtures).
    When running in PyInstaller frozen mode, uses sys._MEIPASS.
    When running from source, uses project root.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    # File is in <root>/app/config.py -> parent of parent is <root>
    return Path(__file__).resolve().parent.parent

def get_app_data_dir() -> Path:
    """
    Returns user writable directory for persistent database, cache, and exports.
    On Windows: %APPDATA%/KAVACH or local directory if portable.
    """
    if os.name == 'nt':
        appdata = os.environ.get('APPDATA')
        if appdata:
            path = Path(appdata) / "KAVACH"
            path.mkdir(parents=True, exist_ok=True)
            return path
    
    # Fallback to local user home
    path = Path.home() / ".kavach"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_database_path() -> str:
    """
    Returns absolute path to shared SQLite database (kavach.db).
    Ensures Web and Desktop operate as a single sovereign system on the exact same database.
    """
    env_path = os.environ.get("KAVACH_DB_PATH")
    if env_path:
        return env_path
    
    # Prioritize kavach.db in project base dir
    base_db = get_base_dir() / "kavach.db"
    if base_db.exists():
        return str(base_db)
        
    # Check working directory
    cwd_db = Path.cwd() / "kavach.db"
    if cwd_db.exists():
        return str(cwd_db)
        
    # Default to base_dir kavach.db or appdata if packaged
    if getattr(sys, 'frozen', False):
        return str(get_app_data_dir() / "kavach.db")
    return str(base_db)

def get_resource_path(*parts: str) -> str:
    """Resolves an absolute path to a bundled asset/file."""
    return str(get_base_dir().joinpath(*parts))

def get_demo_samples_dir() -> Path:
    """Resolves path to demo training samples."""
    # Check bundled location first
    bundled = get_base_dir() / "demo" / "training_samples"
    if bundled.exists():
        return bundled
    
    # Check backend location if running in source tree
    backend_demo = get_base_dir() / "backend" / "app" / "demo" / "training_samples"
    if backend_demo.exists():
        return backend_demo
        
    return bundled
