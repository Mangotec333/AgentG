"""
Pattern matcher for threat signatures.
"""
import json
import re
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import threat_logger


class PatternMatcher:
    """Matches events against threat patterns."""
    
    def __init__(self, pattern_file: str = None):
        if pattern_file is None:
            pattern_file = Path(__file__).parent / "pattern_list.json"
        
        self.pattern_file = pattern_file
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns from JSON file."""
        try:
            with open(self.pattern_file, 'r') as f:
                data = json.load(f)
                return data.get("patterns", [])
        except Exception as e:
            threat_logger.error(f"Error loading patterns: {e}")
            return []
    
    def match(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Match event against patterns.
        
        Args:
            event: Event dictionary
        
        Returns:
            List of matched patterns with metadata
        """
        matches = []
        raw = event.get("raw", "").lower()
        payload = event.get("payload", {})
        
        # Combine all text for matching
        text_to_match = f"{raw} {str(payload)}".lower()
        
        for pattern in self.patterns:
            signature = pattern.get("signature", "").lower()
            
            # Try exact match first
            if signature in text_to_match:
                matches.append({
                    "pattern_id": pattern.get("id"),
                    "category": pattern.get("category"),
                    "severity": pattern.get("severity"),
                    "signature": signature,
                    "matched_text": self._extract_match(text_to_match, signature),
                    "confidence": 1.0
                })
            # Try regex match
            elif self._regex_match(text_to_match, signature):
                matches.append({
                    "pattern_id": pattern.get("id"),
                    "category": pattern.get("category"),
                    "severity": pattern.get("severity"),
                    "signature": signature,
                    "matched_text": signature,
                    "confidence": 0.8
                })
        
        return matches
    
    def _extract_match(self, text: str, pattern: str) -> str:
        """Extract matching text snippet."""
        idx = text.find(pattern)
        if idx >= 0:
            start = max(0, idx - 20)
            end = min(len(text), idx + len(pattern) + 20)
            return text[start:end]
        return pattern
    
    def _regex_match(self, text: str, pattern: str) -> bool:
        """Try regex matching."""
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            return False

