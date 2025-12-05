"""
Entropy-based anomaly detection.
High entropy may indicate encoded/encrypted content.
"""
from typing import Dict, Any
import math


def calculate_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of text.
    
    Args:
        text: Text to analyze
    
    Returns:
        Entropy value (0-8 for ASCII)
    """
    if not text:
        return 0.0
    
    # Count character frequencies
    char_counts = {}
    for char in text:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # Calculate entropy
    length = len(text)
    entropy = 0.0
    for count in char_counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy


def detect_high_entropy(event: Dict[str, Any], threshold: float = 6.0) -> int:
    """
    Detect high entropy content (potential encoding/encryption).
    
    Args:
        event: Event dictionary
        threshold: Entropy threshold (default 6.0)
    
    Returns:
        Risk score (0-10)
    """
    risk = 0
    raw = event.get("raw", "")
    payload = event.get("payload", {})
    
    # Check raw field
    if raw:
        entropy = calculate_entropy(raw)
        if entropy > threshold:
            risk += 4
    
    # Check payload fields
    for key, value in payload.items():
        if isinstance(value, str) and len(value) > 50:
            entropy = calculate_entropy(value)
            if entropy > threshold:
                risk += 3
                break
    
    return min(risk, 10)

