"""
KAVACH 5.0 — Backend Service bridge for CVSS v3.1 and RiskEngine.
"""

from core.risk_engine import (
    CVSSv31Calculator,
    RiskEngine,
    cvss_calculator,
    risk_engine
)

__all__ = ["CVSSv31Calculator", "RiskEngine", "cvss_calculator", "risk_engine"]
