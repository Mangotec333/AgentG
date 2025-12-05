"""
Hashing utilities for data integrity and deduplication.
"""
import hashlib
import json
from typing import Any, Dict


def hash_event(event: Dict[str, Any]) -> str:
    """
    Generate a deterministic hash for an event.
    Used for deduplication and integrity checks.
    
    Args:
        event: Event dictionary
    
    Returns:
        SHA256 hash as hex string
    """
    # Create a normalized representation
    normalized = {
        "timestamp": event.get("timestamp"),
        "agent_id": event.get("agent_id"),
        "event_type": event.get("event_type"),
        "payload": event.get("payload", {}),
    }
    
    # Sort keys for deterministic hashing
    json_str = json.dumps(normalized, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


def hash_string(text: str) -> str:
    """Hash a string using SHA256."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

