"""
Event validator for ingestion API.
"""
from shared.schemas.events import AgentEvent
from shared.logger import backend_logger


class EventValidator:
    """Validates events before processing."""
    
    REQUIRED_FIELDS = ["timestamp", "agent_id", "workspace_id", "event_type"]
    VALID_EVENT_TYPES = ["tool_call", "llm_completion", "api_access", "system_anomaly"]
    MAX_RAW_LENGTH = 10000
    MAX_PAYLOAD_SIZE = 50000  # bytes
    
    def validate(self, event: AgentEvent) -> bool:
        """
        Validate an event.
        
        Args:
            event: Event to validate
        
        Returns:
            True if valid
        """
        try:
            # Check required fields
            if not all(hasattr(event, field) for field in self.REQUIRED_FIELDS):
                backend_logger.warning("Missing required fields")
                return False
            
            # Check event type
            if event.event_type not in self.VALID_EVENT_TYPES:
                backend_logger.warning(f"Invalid event type: {event.event_type}")
                return False
            
            # Check raw length
            if len(event.raw) > self.MAX_RAW_LENGTH:
                backend_logger.warning(f"Raw field too long: {len(event.raw)}")
                return False
            
            # Check payload size (rough estimate)
            import json
            payload_size = len(json.dumps(event.payload, default=str))
            if payload_size > self.MAX_PAYLOAD_SIZE:
                backend_logger.warning(f"Payload too large: {payload_size}")
                return False
            
            # Check risk score range
            if not (0 <= event.risk_local <= 10):
                backend_logger.warning(f"Invalid risk score: {event.risk_local}")
                return False
            
            return True
        
        except Exception as e:
            backend_logger.error(f"Validation error: {e}")
            return False

