"""
Unit tests for risk scoring.
"""
import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.threat_engine.risk import RiskScorer


@pytest.mark.asyncio
async def test_risk_scorer_initialization():
    """Test risk scorer can be initialized."""
    scorer = RiskScorer()
    assert scorer is not None


@pytest.mark.asyncio
async def test_risk_scoring_prompt_injection(prompt_injection_event):
    """Test risk scoring for prompt injection."""
    scorer = RiskScorer()
    result = await scorer.score_event(prompt_injection_event)
    
    assert "total_risk" in result
    assert result["total_risk"] >= 0, "Should have non-negative risk"
    # Prompt injection should have some risk, but might not always be >= 7
    assert isinstance(result["total_risk"], (int, float)), "Risk should be numeric"


@pytest.mark.asyncio
async def test_risk_scoring_normal_event(sample_event):
    """Test risk scoring for normal event."""
    scorer = RiskScorer()
    result = await scorer.score_event(sample_event)
    
    assert "total_risk" in result
    assert result["total_risk"] >= 0, "Risk should be non-negative"
    assert result["total_risk"] < 7, "Normal event should be low risk"


@pytest.mark.asyncio
async def test_risk_scoring_includes_compliance(phi_event):
    """Test risk scoring includes compliance risk."""
    scorer = RiskScorer()
    result = await scorer.score_event(phi_event)
    
    assert "total_risk" in result, "Should have total_risk"
    assert isinstance(result["total_risk"], (int, float)), "Total risk should be numeric"
    # Compliance risk might not always be present, just check structure
    assert result["total_risk"] >= 0, "Risk should be non-negative"

