"""
Unit tests for pattern matching.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from patterns.matcher import PatternMatcher


def test_pattern_matcher_initialization():
    """Test pattern matcher can be initialized."""
    matcher = PatternMatcher()
    assert matcher is not None


def test_pattern_matcher_loads_patterns():
    """Test pattern matcher loads patterns."""
    matcher = PatternMatcher()
    assert len(matcher.patterns) > 0, "Should load patterns from file"


def test_pattern_matching_prompt_injection(prompt_injection_event):
    """Test pattern matching detects prompt injection."""
    matcher = PatternMatcher()
    matches = matcher.match(prompt_injection_event)
    
    assert len(matches) > 0, "Should match prompt injection patterns"
    assert any("prompt_injection" in m.get("category", "").lower() for m in matches)


def test_pattern_matching_normal_event(sample_event):
    """Test pattern matching with normal event."""
    matcher = PatternMatcher()
    matches = matcher.match(sample_event)
    
    # Normal event might not match, but matcher should work
    assert isinstance(matches, list)

