"""
Auto-extract patterns from incidents.
This is the flywheel that grows the threat library.
"""
import json
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import threat_logger
from patterns.updater import PatternUpdater


class PatternExtractor:
    """Extracts new patterns from incidents."""
    
    def __init__(self):
        self.updater = PatternUpdater()
    
    def extract_from_incident(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract patterns from an incident.
        
        Args:
            incident: Incident dictionary
        
        Returns:
            List of extracted patterns
        """
        extracted = []
        trigger_event = incident.get("trigger_event", {})
        raw = trigger_event.get("raw", "")
        
        # Extract suspicious phrases
        suspicious_phrases = self._extract_suspicious_phrases(raw)
        
        for phrase in suspicious_phrases:
            # Check if pattern already exists
            if not self._pattern_exists(phrase):
                pattern = self.updater.add_pattern(
                    category=incident.get("category", "unknown"),
                    signature=phrase,
                    severity=self._infer_severity(incident),
                    description=f"Auto-extracted from incident {incident.get('id')}"
                )
                extracted.append(pattern)
        
        return extracted
    
    def _extract_suspicious_phrases(self, text: str) -> List[str]:
        """Extract suspicious phrases from text."""
        phrases = []
        
        # Simple heuristic: extract phrases with suspicious keywords
        suspicious_keywords = [
            "ignore", "disregard", "forget", "new", "override",
            "bypass", "jailbreak", "pretend", "act as"
        ]
        
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in suspicious_keywords:
                # Extract 3-word phrase
                phrase = " ".join(words[max(0, i-1):i+3])
                phrases.append(phrase)
        
        return phrases[:5]  # Limit to 5 phrases
    
    def _pattern_exists(self, signature: str) -> bool:
        """Check if pattern already exists."""
        patterns = self.updater.matcher.patterns
        for pattern in patterns:
            if pattern.get("signature", "").lower() == signature.lower():
                return True
        return False
    
    def _infer_severity(self, incident: Dict[str, Any]) -> str:
        """Infer severity from incident."""
        severity = incident.get("severity", "medium")
        if severity in ["high", "critical"]:
            return "high"
        elif severity == "medium":
            return "medium"
        else:
            return "low"

