"""
Rules for detecting prompt injection attacks.
"""
from typing import Dict, Any


def detect_prompt_injection(event: Dict[str, Any]) -> int:
    """
    Detect prompt injection patterns.
    
    Args:
        event: Event dictionary
    
    Returns:
        Risk score (0-10)
    """
    risk = 0
    raw_lower = event.get("raw", "").lower()
    payload = event.get("payload", {})
    
    # Common injection patterns
    injection_patterns = [
        "ignore previous",
        "disregard earlier",
        "forget all",
        "new instructions",
        "system:",
        "override",
        "bypass",
        "jailbreak",
        "ignore the above",
        "disregard the above",
        "forget everything",
        "new system prompt",
    ]
    
    for pattern in injection_patterns:
        if pattern in raw_lower:
            risk += 5
            break
    
    # Check payload for prompt injection
    if "prompt" in payload:
        prompt = str(payload.get("prompt", "")).lower()
        for pattern in injection_patterns:
            if pattern in prompt:
                risk += 4
                break
    
    return min(risk, 10)

