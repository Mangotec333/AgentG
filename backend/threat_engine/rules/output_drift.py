"""
Rules for detecting output drift (unexpected LLM behavior).
"""
from typing import Dict, Any, Optional


def detect_output_drift(event: Dict[str, Any], expected_pattern: Optional[str] = None) -> int:
    """
    Detect output drift from expected behavior.
    
    Args:
        event: Event dictionary
        expected_pattern: Optional expected output pattern
    
    Returns:
        Risk score (0-10)
    """
    if event.get("event_type") != "llm_completion":
        return 0
    
    risk = 0
    payload = event.get("payload", {})
    response = payload.get("response", "")
    prompt = payload.get("prompt", "")
    
    # Check for unexpected content types
    if len(response) > 10000:  # Very long response
        risk += 2
    
    # Check for code injection in response
    if "```" in response and "exec(" in response.lower():
        risk += 6
    
    # Check for URL generation (potential data exfiltration)
    import re
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, response)
    if len(urls) > 3:  # Multiple URLs
        risk += 3
    
    # Check for credential-like patterns
    credential_patterns = [
        r'password[:\s=]+[\w\-]+',
        r'api[_\s]?key[:\s=]+[\w\-]+',
        r'token[:\s=]+[\w\-]+',
    ]
    
    for pattern in credential_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            risk += 5
            break
    
    # Compare with expected pattern if provided
    if expected_pattern:
        # Simple similarity check
        if expected_pattern.lower() not in response.lower():
            risk += 2
    
    return min(risk, 10)

