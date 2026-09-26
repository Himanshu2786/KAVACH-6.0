"""
KAVACH 6.0 — Centralized Target Definitions
Centralized registry for authorized assessment targets.
Prevents scattered hardcoded URLs across the codebase.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

WORLD_MONITOR_TARGET: Dict[str, Any] = {
    "target_id": "TGT-WORLD-MONITOR-01",
    "name": "World Monitor",
    "web_url": "https://www.worldmonitor.app",
    "repository_url": "https://github.com/koala73/worldmonitor",
    "target_type": "external_authorized_assessment",
    "source_type": "public_source_repository",
    "default_mode": "HYBRID",
    "supported_modes": ["RUNTIME", "SOURCE", "HYBRID"],
    "scope_domains": ["AUTH", "AUTHZ", "INPUT", "API", "CLIENT", "COMM", "STORAGE"],
    "safety_policy": {
        "read_only": True,
        "non_destructive": True,
        "rate_limited": True,
        "allow_dos": False,
        "allow_bruteforce": False,
        "allow_data_alteration": False
    },
    "description": "Sovereign cyber situational awareness application evaluated for SIH Problem Statement 26163."
}

class TargetConfigModel(BaseModel):
    target_id: str = Field(default="TGT-WORLD-MONITOR-01")
    name: str = Field(default="World Monitor")
    web_url: str = Field(default="https://www.worldmonitor.app")
    repository_url: str = Field(default="https://github.com/koala73/worldmonitor")
    target_type: str = Field(default="external_authorized_assessment")
    source_type: str = Field(default="public_source_repository")
    default_mode: str = Field(default="HYBRID")
    supported_modes: List[str] = Field(default=["RUNTIME", "SOURCE", "HYBRID"])
    scope_domains: List[str] = Field(default=["AUTH", "AUTHZ", "INPUT", "API", "CLIENT", "COMM", "STORAGE"])
    description: str = Field(default="World Monitor Assessment Target")

def get_world_monitor_target() -> Dict[str, Any]:
    return WORLD_MONITOR_TARGET

def is_world_monitor_target(target_url: Optional[str]) -> bool:
    if not target_url:
        return False
    url = target_url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        return hostname in ("worldmonitor.app", "www.worldmonitor.app")
    except Exception:
        return False
