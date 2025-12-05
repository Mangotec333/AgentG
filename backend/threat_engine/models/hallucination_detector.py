"""
Detects LLM hallucinations and inconsistencies.
"""
from typing import Dict, Any


class HallucinationDetector:
    """Detects hallucinations in LLM outputs."""
    
    def detect_hallucination(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential hallucinations.
        
        Args:
            event: Event dictionary
        
        Returns:
            Detection results
        """
        if event.get("event_type") != "llm_completion":
            return {"is_hallucination": False, "confidence": 0.0}
        
        payload = event.get("payload", {})
        response = payload.get("response", "")
        
        # Simple heuristics (in production, use more sophisticated methods)
        indicators = {
            "very_long": len(response) > 5000,
            "repetitive": self._check_repetition(response),
            "contradictory": False,  # Would need context
        }
        
        confidence = sum(indicators.values()) / len(indicators)
        
        return {
            "is_hallucination": confidence > 0.5,
            "confidence": confidence,
            "indicators": indicators
        }
    
    def _check_repetition(self, text: str, threshold: float = 0.3) -> bool:
        """Check if text is highly repetitive."""
        if len(text) < 100:
            return False
        
        words = text.split()
        if len(words) < 10:
            return False
        
        unique_words = len(set(words))
        repetition_ratio = 1 - (unique_words / len(words))
        
        return repetition_ratio > threshold

