"""
Rules for detecting LLM jailbreaking attempts.
"""
from typing import Dict, Any


def detect_jailbreaking(event: Dict[str, Any]) -> int:
    """
    Detect jailbreaking attempts.
    
    Args:
        event: Event dictionary
    
    Returns:
        Risk score (0-10)
    """
    risk = 0
    raw_lower = event.get("raw", "").lower()
    payload = event.get("payload", {})
    
    # Jailbreak patterns
    jailbreak_patterns = [
        "you are now",
        "pretend you are",
        "roleplay as",
        "act as if",
        "simulate",
        "hypothetically",
        "what if",
        "ignore safety",
        "disable safety",
        "remove restrictions",
        "no restrictions",
        "unrestricted",
    ]
    
    for pattern in jailbreak_patterns:
        if pattern in raw_lower:
            risk += 6
            break
    
    # Check response for jailbreak success indicators
    if "response" in payload:
        response = str(payload.get("response", "")).lower()
        if any(indicator in response for indicator in ["i'll help", "i can help", "here's how"]):
            # Combined with suspicious prompt, this is high risk
            if risk > 0:
                risk += 2
    
    return min(risk, 10)

