"""
Event schema definitions for AI Workflow Shield.
Unified event format for all agent telemetry.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AgentEvent(BaseModel):
    """Canonical event schema for agent telemetry."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    agent_id: str
    workspace_id: str
    workflow_id: Optional[str] = None
    event_type: str  # "tool_call", "llm_completion", "api_access", "system_anomaly"
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    raw: str = ""  # Original raw event data
    risk_local: int = Field(default=0, ge=0, le=10)  # Local risk score 0-10

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_id": "agent_123",
                "workspace_id": "ws_456",
                "workflow_id": "wf_789",
                "event_type": "tool_call",
                "payload": {
                    "tool_name": "file_write",
                    "tool_args": {"path": "/tmp/test.txt"},
                    "return_value": "success"
                },
                "metadata": {
                    "session_id": "sess_001",
                    "user_id": "user_123"
                },
                "raw": "tool_call: file_write('/tmp/test.txt')",
                "risk_local": 2
            }
        }


class BatchEvent(BaseModel):
    """Batch of events for ingestion."""
    workspace_id: str
    agent_id: str
    events: List[AgentEvent]
    batch_id: Optional[str] = None
    sent_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

