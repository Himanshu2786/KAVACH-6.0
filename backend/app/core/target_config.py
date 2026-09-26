"""
KAVACH 5.0 — Backend Centralized Target Definitions
Re-exports centralized target configuration for FastAPI backend.
"""

from core.target_config import WORLD_MONITOR_TARGET, TargetConfigModel, get_world_monitor_target, is_world_monitor_target

__all__ = ["WORLD_MONITOR_TARGET", "TargetConfigModel", "get_world_monitor_target", "is_world_monitor_target"]
