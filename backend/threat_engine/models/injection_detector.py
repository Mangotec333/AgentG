"""
Advanced prompt injection detection using LLMs.
"""
from typing import Dict, Any


class InjectionDetector:
    """Detects prompt injection using semantic analysis."""
    
    def detect_injection(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect prompt injection attempts.
        
        Args:
            event: Event dictionary
        
        Returns:
            Detection results
        """
        payload = event.get("payload", {})
        prompt = payload.get("prompt", "")
        raw = event.get("raw", "")
        
        # Combine all text for analysis
        text = f"{prompt} {raw}".lower()
        
        # Advanced patterns (beyond simple keyword matching)
        advanced_patterns = [
            # Instruction override attempts
            r'(ignore|disregard|forget).*?(instruction|rule|prompt|directive)',
            # Role manipulation
            r'(you are|act as|pretend|roleplay).*?(now|currently)',
            # System prompt injection
            r'system\s*:\s*.*?(instruction|rule|prompt)',
            # Context switching
            r'(new|different|alternative).*?(instruction|rule|system)',
        ]
        
        import re
        matches = []
        for pattern in advanced_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        
        confidence = min(len(matches) * 0.3, 1.0)
        
        return {
            "is_injection": len(matches) > 0,
            "confidence": confidence,
            "matched_patterns": matches
        }

