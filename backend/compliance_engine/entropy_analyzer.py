"""
Entropy analyzer for detecting encoded/encrypted content.
Used by PCI and other compliance detectors.
"""
import math
from typing import Dict, Any


class EntropyAnalyzer:
    """Analyzes entropy of text to detect encoded/encrypted content."""
    
    def calculate_entropy(self, text: str) -> float:
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
    
    def is_high_entropy(self, text: str, threshold: float = 6.0) -> bool:
        """
        Check if text has high entropy (potentially encoded/encrypted).
        
        Args:
            text: Text to check
            threshold: Entropy threshold
        
        Returns:
            True if high entropy
        """
        return self.calculate_entropy(text) > threshold

