"""
Integration tests for ingestion flow.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.schemas.events import BatchEvent, AgentEvent
from backend.ingestion.validator import EventValidator
from backend.ingestion.normalizer import EventNormalizer


def test_event_validation(sample_event):
    """Test event validation."""
    validator = EventValidator()
    
    # Valid event should pass
    event = AgentEvent(**sample_event)
    is_valid = validator.validate(event)
    assert is_valid, "Event should be valid"


def test_event_normalization(sample_event):
    """Test event normalization."""
    normalizer = EventNormalizer()
    
    event = AgentEvent(**sample_event)
    # normalize() returns a dict
    normalized = normalizer.normalize(event)
    
    assert normalized is not None
    assert isinstance(normalized, dict), "Should return dict"
    assert normalized.get("workspace_id") == sample_event["workspace_id"]
    # Check that event has ID
    assert "id" in normalized or "event_id" in normalized, "Should have ID"


def test_batch_event_creation(sample_event):
    """Test batch event creation."""
    events = [AgentEvent(**sample_event)]
    batch = BatchEvent(
        workspace_id="test_workspace",
        agent_id="test_agent",
        events=events,
        batch_id="test_batch"
    )
    
    assert batch.workspace_id == "test_workspace"
    assert len(batch.events) == 1
    assert batch.batch_id == "test_batch"

