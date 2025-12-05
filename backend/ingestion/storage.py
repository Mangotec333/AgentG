"""
Event storage - stores events in database and queues for threat engine.
"""
import asyncpg
import json
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import backend_logger
from shared.config import BackendConfig


class EventStorage:
    """Stores events in database."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.pool = None
    
    async def _get_pool(self):
        """Get database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.config.database_url)
        return self.pool
    
    async def store_events(self, events: List[Dict[str, Any]], workspace_id: str) -> int:
        """
        Store events in database.
        
        Args:
            events: List of normalized events
            workspace_id: Workspace identifier
        
        Returns:
            Number of events stored
        """
        pool = await self._get_pool()
        stored_count = 0
        
        async with pool.acquire() as conn:
            for event in events:
                try:
                    await conn.execute(
                        """
                        INSERT INTO events (
                            id, workspace_id, agent_id, workflow_id,
                            event_type, payload, metadata, raw,
                            risk_local, event_hash, created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (event_hash) DO NOTHING
                        """,
                        event.get("id"),
                        workspace_id,
                        event.get("agent_id"),
                        event.get("workflow_id"),
                        event.get("event_type"),
                        json.dumps(event.get("payload", {})),
                        json.dumps(event.get("metadata", {})),
                        event.get("raw", ""),
                        event.get("risk_local", 0),
                        event.get("event_hash"),
                        event.get("timestamp")
                    )
                    stored_count += 1
                
                except Exception as e:
                    backend_logger.error(f"Error storing event {event.get('id')}: {e}")
        
        backend_logger.info(f"Stored {stored_count}/{len(events)} events")
        return stored_count
    
    async def queue_for_threat_engine(self, events: List[Dict[str, Any]]):
        """
        Queue events for threat engine processing.
        
        In production, this would use a message queue (Redis, RabbitMQ, etc.).
        For now, we'll mark events as pending processing.
        
        Args:
            events: List of events to queue
        """
        # In a real implementation, this would:
        # 1. Add to Redis queue
        # 2. Or trigger async task processor
        # 3. Or use Celery/background workers
        
        backend_logger.info(f"Queued {len(events)} events for threat engine processing")
        
        # For now, we can add a flag to events or use a separate queue table
        # This is a placeholder for the actual queue implementation

