"""
Pattern updater - manages threat pattern library.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import threat_logger
from patterns.matcher import PatternMatcher


class PatternUpdater:
    """Updates and manages threat pattern library."""
    
    def __init__(self, pattern_file: str = None):
        if pattern_file is None:
            pattern_file = Path(__file__).parent / "pattern_list.json"
        
        self.pattern_file = pattern_file
        self.matcher = PatternMatcher(pattern_file)
    
    def add_pattern(
        self,
        category: str,
        signature: str,
        severity: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Add a new pattern to the library.
        
        Args:
            category: Pattern category
            signature: Pattern signature
            severity: Severity level (low/medium/high)
            description: Pattern description
        
        Returns:
            Created pattern dictionary
        """
        # Load existing patterns
        patterns_data = self._load_patterns_data()
        patterns = patterns_data.get("patterns", [])
        
        # Create new pattern
        pattern_id = f"{category[:2].upper()}-{len(patterns) + 1:03d}"
        new_pattern = {
            "id": pattern_id,
            "category": category,
            "signature": signature,
            "severity": severity,
            "description": description,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "match_count": 0
            }
        }
        
        patterns.append(new_pattern)
        
        # Save
        patterns_data["patterns"] = patterns
        patterns_data["last_updated"] = datetime.utcnow().isoformat()
        self._save_patterns_data(patterns_data)
        
        threat_logger.info(f"Added pattern: {pattern_id}")
        return new_pattern
    
    def update_pattern_match_count(self, pattern_id: str):
        """Increment match count for a pattern."""
        patterns_data = self._load_patterns_data()
        patterns = patterns_data.get("patterns", [])
        
        for pattern in patterns:
            if pattern.get("id") == pattern_id:
                pattern["metadata"]["match_count"] = pattern["metadata"].get("match_count", 0) + 1
                break
        
        patterns_data["patterns"] = patterns
        patterns_data["last_updated"] = datetime.utcnow().isoformat()
        self._save_patterns_data(patterns_data)
    
    def _load_patterns_data(self) -> Dict[str, Any]:
        """Load patterns data from file."""
        try:
            with open(self.pattern_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            threat_logger.error(f"Error loading patterns: {e}")
            return {"patterns": [], "version": "1.0.0"}
    
    def _save_patterns_data(self, data: Dict[str, Any]):
        """Save patterns data to file."""
        try:
            with open(self.pattern_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            threat_logger.error(f"Error saving patterns: {e}")

