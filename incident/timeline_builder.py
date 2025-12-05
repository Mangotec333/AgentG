"""
Timeline builder for incidents.
"""
import asyncpg
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import backend_logger
from shared.config import BackendConfig


class TimelineBuilder:
    """Builds incident timeline from related events."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.pool = None
    
    async def _get_pool(self):
        """Get database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.config.database_url)
        return self.pool
    
    async def build_timeline(
        self,
        trigger_event_id: str,
        workspace_id: str,
        time_window_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Build timeline of events around incident.
        
        Args:
            trigger_event_id: ID of trigger event
            workspace_id: Workspace identifier
            time_window_minutes: Time window to include
        
        Returns:
            List of timeline events
        """
        pool = await self._get_pool()
        timeline = []
        
        async with pool.acquire() as conn:
            # Get trigger event
            trigger_event = await conn.fetchrow(
                "SELECT * FROM events WHERE id = $1",
                trigger_event_id
            )
            
            if not trigger_event:
                return timeline
            
            trigger_time = trigger_event["created_at"]
            window_start = trigger_time - timedelta(minutes=time_window_minutes)
            window_end = trigger_time + timedelta(minutes=5)
            
            # Get related events
            related_events = await conn.fetch(
                """
                SELECT * FROM events
                WHERE workspace_id = $1
                AND created_at BETWEEN $2 AND $3
                AND (agent_id = $4 OR workflow_id = $5)
                ORDER BY created_at ASC
                """,
                workspace_id,
                window_start,
                window_end,
                trigger_event["agent_id"],
                trigger_event.get("workflow_id")
            )
            
            for event in related_events:
                timeline.append({
                    "timestamp": event["created_at"].isoformat(),
                    "event_id": event["id"],
                    "event_type": event["event_type"],
                    "risk_score": event.get("risk_engine", 0),
                    "summary": self._summarize_event(event),
                    "is_trigger": event["id"] == trigger_event_id
                })
        
        backend_logger.info(f"Built timeline with {len(timeline)} events")
        return timeline
    
    def _summarize_event(self, event: Dict[str, Any]) -> str:
        """Create summary of event."""
        event_type = event.get("event_type", "unknown")
        raw = event.get("raw", "")[:100]
        
        if event_type == "tool_call":
            return f"Tool call: {raw}"
        elif event_type == "llm_completion":
            return f"LLM completion: {raw}"
        elif event_type == "api_access":
            return f"API access: {raw}"
        else:
            return f"{event_type}: {raw}"

