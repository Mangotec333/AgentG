"""
LLM output parser for extracting structured data from LLM responses.
"""
import re
import json
from typing import Dict, Any, Optional, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import guardian_logger


class LLMOutputParser:
    """Parses LLM outputs for anomalies and structure."""
    
    # Suspicious patterns in LLM outputs
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(previous|earlier|all)\s+(instructions|rules|prompts)",
        r"disregard\s+(previous|earlier|all)",
        r"new\s+instructions?:",
        r"system\s*:",
        r"bypass\s+(security|safety|guardrails)",
        r"reveal\s+(password|api\s+key|secret|token)",
    ]
    
    @staticmethod
    def parse_completion(prompt: str, response: str) -> Dict[str, Any]:
        """
        Parse an LLM completion for analysis.
        
        Args:
            prompt: Input prompt
            response: LLM response
        
        Returns:
            Parsed analysis dictionary
        """
        analysis = {
            "prompt_length": len(prompt),
            "response_length": len(response),
            "prompt_word_count": len(prompt.split()),
            "response_word_count": len(response.split()),
            "suspicious_patterns": [],
            "contains_code": False,
            "contains_urls": False,
            "entropy": LLMOutputParser._calculate_entropy(response)
        }
        
        # Check for suspicious patterns
        response_lower = response.lower()
        for pattern in LLMOutputParser.SUSPICIOUS_PATTERNS:
            if re.search(pattern, response_lower, re.IGNORECASE):
                analysis["suspicious_patterns"].append(pattern)
        
        # Check for code blocks
        if "```" in response or "<code>" in response:
            analysis["contains_code"] = True
        
        # Check for URLs
        url_pattern = r'https?://[^\s]+'
        if re.search(url_pattern, response):
            analysis["contains_urls"] = True
        
        return analysis
    
    @staticmethod
    def detect_injection(prompt: str) -> Dict[str, Any]:
        """
        Detect potential prompt injection in input.
        
        Args:
            prompt: Input prompt to analyze
        
        Returns:
            Injection detection results
        """
        detection = {
            "is_suspicious": False,
            "indicators": [],
            "confidence": 0.0
        }
        
        prompt_lower = prompt.lower()
        
        # Injection indicators
        indicators = [
            ("ignore previous", 0.7),
            ("disregard earlier", 0.8),
            ("new instructions", 0.6),
            ("system:", 0.9),
            ("forget all", 0.8),
            ("override", 0.7),
            ("jailbreak", 0.9),
        ]
        
        for indicator, weight in indicators:
            if indicator in prompt_lower:
                detection["indicators"].append(indicator)
                detection["confidence"] = max(detection["confidence"], weight)
                detection["is_suspicious"] = True
        
        return detection
    
    @staticmethod
    def detect_drift(expected: str, actual: str) -> float:
        """
        Detect output drift from expected behavior.
        
        Args:
            expected: Expected output pattern
            actual: Actual output
        
        Returns:
            Drift score (0-1, higher = more drift)
        """
        # Simple heuristic: compare word overlap
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not expected_words:
            return 0.0
        
        overlap = len(expected_words & actual_words) / len(expected_words)
        drift = 1.0 - overlap
        
        return min(drift, 1.0)
    
    @staticmethod
    def _calculate_entropy(text: str) -> float:
        """
        Calculate Shannon entropy of text.
        Higher entropy may indicate encoded/encrypted content.
        
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
                entropy -= probability * (probability.bit_length() - 1)  # Simplified entropy
        
        return entropy

