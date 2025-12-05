"""
Batch sender for transmitting events to ingestion API.
"""
import json
import time
import uuid
from typing import List, Optional
import requests
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.schemas.events import AgentEvent, BatchEvent
from shared.logger import guardian_logger
from shared.token_auth import TokenManager
from guardian_agent.config import config


class BatchSender:
    """Sends batches of events to the ingestion API."""
    
    def __init__(self):
        self.api_endpoint = config.ingestion_endpoint
        self.api_key = config.api_key
        self.retry_count = 3
        self.retry_delay = 1.0
        self.success_count = 0
        self.failure_count = 0
    
    def send_batch(self, events: List[AgentEvent]) -> bool:
        """
        Send a batch of events to the ingestion API.
        
        Args:
            events: List of events to send
        
        Returns:
            True if successful
        """
        if not events:
            return True
        
        # Create batch payload
        batch = BatchEvent(
            workspace_id=config.workspace_id,
            agent_id=config.agent_id,
            events=events,
            batch_id=str(uuid.uuid4())
        )
        
        # Convert to dict for JSON serialization
        payload = batch.model_dump()
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Guardian-Agent/1.0"
        }
        
        # Add authentication token if API key is available
        if self.api_key:
            token = TokenManager.generate_token(
                self.api_key,
                config.workspace_id
            )
            headers["Authorization"] = f"Bearer {token}"
            headers["X-API-Key"] = self.api_key
        
        # Retry logic
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.success_count += len(events)
                    guardian_logger.info(
                        f"Successfully sent batch of {len(events)} events "
                        f"(batch_id={batch.batch_id})"
                    )
                    return True
                else:
                    guardian_logger.warning(
                        f"API returned status {response.status_code}: {response.text[:200]}"
                    )
            
            except requests.exceptions.RequestException as e:
                guardian_logger.error(f"Request error (attempt {attempt + 1}/{self.retry_count}): {e}")
            
            # Wait before retry
            if attempt < self.retry_count - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        # All retries failed
        self.failure_count += len(events)
        guardian_logger.error(
            f"Failed to send batch of {len(events)} events after {self.retry_count} attempts"
        )
        return False
    
    def send_single(self, event: AgentEvent) -> bool:
        """
        Send a single event (wraps in batch).
        
        Args:
            event: Event to send
        
        Returns:
            True if successful
        """
        return self.send_batch([event])
    
    def get_stats(self) -> dict:
        """Get sender statistics."""
        return {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_sent": self.success_count,
            "api_endpoint": self.api_endpoint
        }

