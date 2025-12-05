"""
Unit tests for event collector.
"""
import pytest
import sys
import os
from pathlib import Path

# Add project root and guardian-agent to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "guardian-agent"))

try:
    from event_collector import EventCollector
    EVENT_COLLECTOR_AVAILABLE = True
except ImportError as e:
    EVENT_COLLECTOR_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason=f"Event collector import failed: {e}")


@pytest.mark.skipif(not EVENT_COLLECTOR_AVAILABLE, reason="Event collector not available")
def test_event_collector_initialization():
    """Test event collector can be initialized."""
    collector = EventCollector()
    assert collector is not None


@pytest.mark.skipif(not EVENT_COLLECTOR_AVAILABLE, reason="Event collector not available")
def test_collect_llm_completion(sample_event):
    """Test collecting LLM completion event."""
    collector = EventCollector()
    
    event = collector.collect_llm_completion(
        prompt=sample_event["payload"]["prompt"],
        response=sample_event["payload"]["response"],
        model=sample_event["payload"]["model"],
        metadata={}
    )
    
    assert event is not None
    assert event.event_type == "llm_completion"
    assert event.payload["prompt"] == sample_event["payload"]["prompt"]
    assert event.payload["response"] == sample_event["payload"]["response"]


@pytest.mark.skipif(not EVENT_COLLECTOR_AVAILABLE, reason="Event collector not available")
def test_collect_tool_call():
    """Test collecting tool call event."""
    collector = EventCollector()
    
    event = collector.collect_tool_call(
        tool_name="read_file",
        tool_args={"path": "/tmp/test.txt"},
        return_value="file contents",
        metadata={}
    )
    
    assert event is not None
    assert event.event_type == "tool_call"
    assert event.payload["tool_name"] == "read_file"


@pytest.mark.skipif(not EVENT_COLLECTOR_AVAILABLE, reason="Event collector not available")
def test_event_normalization(sample_event):
    """Test event normalization."""
    collector = EventCollector()
    
    event = collector.collect_llm_completion(
        prompt=sample_event["payload"]["prompt"],
        response=sample_event["payload"]["response"],
        model=sample_event["payload"]["model"]
    )
    
    # Check event has required fields
    assert hasattr(event, "timestamp")
    assert hasattr(event, "agent_id")
    assert hasattr(event, "event_type")
    assert hasattr(event, "payload")

