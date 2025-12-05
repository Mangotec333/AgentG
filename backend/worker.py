"""
Background worker for processing queued events through threat engine.
"""
import asyncio
import asyncpg
import json
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import backend_logger
from shared.config import BackendConfig
from backend.threat_engine.processor import ThreatEngineProcessor


class ThreatEngineWorker:
    """Background worker that processes events through threat engine."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.processor = ThreatEngineProcessor()
        self.pool = None
        self.running = False
    
    async def _get_pool(self):
        """Get database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.config.database_url)
        return self.pool
    
    async def start(self, batch_size: int = 10, poll_interval: int = 5):
        """
        Start the worker.
        
        Args:
            batch_size: Number of events to process per batch
            poll_interval: Seconds between polls
        """
        self.running = True
        backend_logger.info("Threat Engine Worker started")
        
        while self.running:
            try:
                # Get batch of unprocessed events
                events = await self._get_unprocessed_events(batch_size)
                
                if events:
                    backend_logger.info(f"Processing batch of {len(events)} events")
                    results = await self.processor.process_batch(events)
                    backend_logger.info(f"Processed {len(results)} events")
                else:
                    # No events to process, wait
                    await asyncio.sleep(poll_interval)
            
            except Exception as e:
                backend_logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(poll_interval)
    
    async def stop(self):
        """Stop the worker."""
        self.running = False
        backend_logger.info("Threat Engine Worker stopped")
    
    async def _get_unprocessed_events(self, limit: int) -> List[Dict[str, Any]]:
        """
        Get unprocessed events from database.
        
        Events are considered unprocessed if risk_engine is NULL.
        
        Args:
            limit: Maximum number of events to fetch
        
        Returns:
            List of event dictionaries
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM events
                WHERE risk_engine IS NULL
                ORDER BY created_at ASC
                LIMIT $1
                """,
                limit
            )
            
            events = []
            for row in rows:
                event = dict(row)
                # Parse JSON fields
                if event.get("payload"):
                    event["payload"] = json.loads(event["payload"])
                if event.get("metadata"):
                    event["metadata"] = json.loads(event["metadata"])
                events.append(event)
            
            return events


async def main():
    """Main entry point for worker."""
    worker = ThreatEngineWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        backend_logger.info("Received shutdown signal")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())

