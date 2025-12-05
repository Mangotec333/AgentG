"""
Event normalizer - converts events to canonical form.
"""
import uuid
from datetime import datetime
from shared.schemas.events import AgentEvent
from shared.pii_cleaner import PIICleaner
from shared.hashing import hash_event
from shared.logger import backend_logger


class EventNormalizer:
    """Normalizes events to canonical form."""
    
    def __init__(self):
        self.pii_cleaner = PIICleaner()
    
    def normalize(self, event: AgentEvent) -> dict:
        """
        Normalize an event to canonical form.
        
        Args:
            event: Event to normalize
        
        Returns:
            Normalized event dictionary
        """
        # Convert to dict
        event_dict = event.model_dump()
        
        # Generate event ID if not present
        if "id" not in event_dict:
            event_dict["id"] = str(uuid.uuid4())
        
        # Clean PII
        event_dict = self.pii_cleaner.clean_event(event_dict)
        
        # Generate event hash for deduplication
        event_dict["event_hash"] = hash_event(event_dict)
        
        # Ensure timestamp is ISO format
        if "timestamp" in event_dict:
            try:
                # Validate timestamp format
                datetime.fromisoformat(event_dict["timestamp"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                event_dict["timestamp"] = datetime.utcnow().isoformat()
        
        # Normalize metadata
        if "metadata" not in event_dict:
            event_dict["metadata"] = {}
        
        # Add normalization metadata
        event_dict["metadata"]["normalized_at"] = datetime.utcnow().isoformat()
        
        return event_dict

