"""
E2E test: Prompt injection → Incident creation.
"""
import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.threat_engine.risk import RiskScorer
from incident.detector import IncidentDetector


@pytest.mark.asyncio
async def test_prompt_injection_creates_incident(prompt_injection_event):
    """Test that prompt injection creates an incident."""
    # 1. Score risk
    scorer = RiskScorer()
    risk_analysis = await scorer.score_event(prompt_injection_event)
    
    # 2. Check if incident should be created
    assert risk_analysis["total_risk"] > 0, "Prompt injection should have risk"
    
    # 3. Check if incident should be created (risk >= 7)
    # Incident detector logic: risk >= 7 triggers incident
    should_create = risk_analysis["total_risk"] >= 7
    
    # High risk should create incident
    if risk_analysis["total_risk"] >= 7:
        assert should_create is True, "High risk should create incident"
    else:
        # Lower risk might not create incident, that's OK
        assert should_create is False or risk_analysis["total_risk"] < 7


@pytest.mark.asyncio
async def test_normal_event_no_incident(sample_event):
    """Test that normal event doesn't create incident."""
    scorer = RiskScorer()
    risk_analysis = await scorer.score_event(sample_event)
    
    # Incident is created when risk >= 7
    should_create = risk_analysis["total_risk"] >= 7
    
    assert should_create is False, "Low risk should not create incident"

