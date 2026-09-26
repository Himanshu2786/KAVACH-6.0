from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Any, Optional
import os
import sys
import json

def load_ai_config_file() -> Dict[str, Any]:
    """Search for centralized AI/config.json across working dir, bundle dir, and project root."""
    candidate_paths = [
        os.path.join(os.getcwd(), "AI", "config.json"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "AI", "config.json")),
    ]
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        candidate_paths.insert(0, os.path.join(sys._MEIPASS, "AI", "config.json"))
        # Also check adjacent to the executable on USB
        exe_dir = os.path.dirname(sys.executable)
        candidate_paths.insert(0, os.path.join(exe_dir, "AI", "config.json"))

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[AI CONFIG WARNING] Failed reading {path}: {e}")
    return {}

_ai_file_cfg = load_ai_config_file()

class Settings(BaseSettings):
    PROJECT_NAME: str = "KAVACH Security Intelligence Platform"
    VERSION: str = "6.0.0"
    API_V1_STR: str = "/api"
    
    # Centralized Ollama AI Configuration (Loaded from AI/config.json with env/default fallback)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", _ai_file_cfg.get("endpoint", "http://127.0.0.1:11434"))
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", _ai_file_cfg.get("model_name", "llama3"))
    AI_TIMEOUT: float = float(os.getenv("AI_TIMEOUT", str(_ai_file_cfg.get("timeout_seconds", 30.0))))
    AI_ENABLED: bool = os.getenv("AI_ENABLED", str(_ai_file_cfg.get("enabled", True))).lower() in ("true", "1", "yes")
    AI_AUTO_START: bool = os.getenv("AI_AUTO_START", str(_ai_file_cfg.get("auto_start", True))).lower() in ("true", "1", "yes")
    AI_MASK_SENSITIVE: bool = os.getenv("AI_MASK_SENSITIVE", str(_ai_file_cfg.get("mask_sensitive_data", True))).lower() in ("true", "1", "yes")
    AI_CONFIG_RAW: Dict[str, Any] = _ai_file_cfg
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kavach.db")
    
    # Operational Mode
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
