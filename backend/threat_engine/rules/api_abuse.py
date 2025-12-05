"""
Rules for detecting API abuse.
"""
from typing import Dict, Any


def detect_api_abuse(event: Dict[str, Any]) -> int:
    """
    Detect API abuse patterns.
    
    Args:
        event: Event dictionary
    
    Returns:
        Risk score (0-10)
    """
    if event.get("event_type") != "api_access":
        return 0
    
    risk = 0
    payload = event.get("payload", {})
    endpoint = payload.get("endpoint", "").lower()
    method = payload.get("method", "").upper()
    status_code = payload.get("status_code")
    
    # Suspicious endpoints
    suspicious_endpoints = [
        "/admin",
        "/api/admin",
        "/internal",
        "/delete",
        "/destroy",
        "/reset",
        "/format",
    ]
    
    for pattern in suspicious_endpoints:
        if pattern in endpoint:
            risk += 3
    
    # Unauthorized access attempts
    if status_code in [401, 403]:
        risk += 5
    
    # Suspicious methods on sensitive endpoints
    if method in ["DELETE", "PUT", "PATCH"] and any(pattern in endpoint for pattern in ["/user", "/account", "/admin"]):
        risk += 4
    
    # Rate limiting violations (would need context)
    # This is a placeholder for rate limit checking
    
    return min(risk, 10)

