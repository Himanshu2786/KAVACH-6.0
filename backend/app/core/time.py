"""
KAVACH 5.0 — Sovereign Time Subsystem (Indian Standard Time - IST)
Standardizes all timestamps, logging, scanning metadata, evidence chains,
and audit logs across the platform to Indian Standard Time (UTC+05:30).
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union

# Indian Standard Time (IST): UTC + 5 hours 30 minutes
IST = timezone(timedelta(hours=5, minutes=30), name="IST")

def ist_now() -> datetime:
    """Return current timezone-aware datetime in Indian Standard Time (IST)."""
    return datetime.now(IST)

def ist_isoformat() -> str:
    """Return ISO-8601 formatted timestamp string in IST (e.g. '2026-09-21T21:45:00+05:30')."""
    return ist_now().isoformat()

def ist_formatted(fmt: str = "%Y-%m-%d %H:%M:%S IST") -> str:
    """Return current timestamp formatted as a human-readable string in IST."""
    return ist_now().strftime(fmt)

def to_ist(dt_input: Optional[Union[datetime, str]]) -> datetime:
    """
    Convert any datetime object or ISO string to Indian Standard Time (IST).
    If naive datetime is provided, assume UTC first and convert to IST.
    """
    if dt_input is None:
        return ist_now()

    if isinstance(dt_input, str):
        # Handle 'Z' or ISO formats
        clean_str = dt_input.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(clean_str)
        except ValueError:
            return ist_now()
    else:
        dt = dt_input

    if dt.tzinfo is None:
        # Naive datetime: treat as UTC then convert to IST
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(IST)

def to_ist_formatted(dt_input: Optional[Union[datetime, str]], fmt: str = "%Y-%m-%d %H:%M:%S IST") -> str:
    """Convert any datetime or ISO string to a formatted IST string."""
    return to_ist(dt_input).strftime(fmt)
