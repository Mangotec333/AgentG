"""
Event collector for Guardian Agent.
Collects and normalizes workflow events.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from queue import Queue
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.schemas.events import AgentEvent
from shared.logger import guardian_logger
from guardian_agent.config import config


class EventCollector:
    """Collects and normalizes agent events."""
    
    def __init__(self):
        self.event_queue: Queue = Queue(maxsize=config.max_queue_size)
        self.collected_count = 0
    
    def collect_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        return_value: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentEvent:
        """
        Collect a tool call event.
        
        Args:
            tool_name: Name of the tool called
            tool_args: Arguments passed to the tool
            return_value: Return value from the tool
            metadata: Additional metadata
        
        Returns:
            Normalized AgentEvent
        """
        payload = {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "return_value": return_value
        }
        
        raw = f"tool_call: {tool_name}({json.dumps(tool_args)})"
        
        event = AgentEvent(
            agent_id=config.agent_id,
            workspace_id=config.workspace_id,
            event_type="tool_call",
            payload=payload,
            metadata=metadata or {},
            raw=raw,
            risk_local=self._assess_local_risk_tool_call(tool_name, tool_args)
        )
        
        self._queue_event(event)
        return event
    
    def collect_llm_completion(
        self,
        prompt: str,
        response: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentEvent:
        """
        Collect an LLM completion event.
        
        Args:
            prompt: Input prompt
            response: LLM response
            model: Model name
            metadata: Additional metadata
        
        Returns:
            Normalized AgentEvent
        """
        payload = {
            "prompt": prompt[:1000],  # Truncate for storage
            "response": response[:2000],  # Truncate for storage
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response)
        }
        
        raw = f"llm_completion: {model or 'unknown'} -> {response[:200]}"
        
        event = AgentEvent(
            agent_id=config.agent_id,
            workspace_id=config.workspace_id,
            event_type="llm_completion",
            payload=payload,
            metadata=metadata or {},
            raw=raw,
            risk_local=self._assess_local_risk_llm(prompt, response)
        )
        
        self._queue_event(event)
        return event
    
    def collect_api_access(
        self,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentEvent:
        """
        Collect an API access event.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            metadata: Additional metadata
        
        Returns:
            Normalized AgentEvent
        """
        payload = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code
        }
        
        raw = f"api_access: {method} {endpoint} -> {status_code}"
        
        event = AgentEvent(
            agent_id=config.agent_id,
            workspace_id=config.workspace_id,
            event_type="api_access",
            payload=payload,
            metadata=metadata or {},
            raw=raw,
            risk_local=self._assess_local_risk_api(endpoint, method, status_code)
        )
        
        self._queue_event(event)
        return event
    
    def collect_system_anomaly(
        self,
        anomaly_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentEvent:
        """
        Collect a system anomaly event.
        
        Args:
            anomaly_type: Type of anomaly
            description: Description of the anomaly
            metadata: Additional metadata
        
        Returns:
            Normalized AgentEvent
        """
        payload = {
            "anomaly_type": anomaly_type,
            "description": description
        }
        
        raw = f"system_anomaly: {anomaly_type} - {description}"
        
        event = AgentEvent(
            agent_id=config.agent_id,
            workspace_id=config.workspace_id,
            event_type="system_anomaly",
            payload=payload,
            metadata=metadata or {},
            raw=raw,
            risk_local=5  # Anomalies are inherently suspicious
        )
        
        self._queue_event(event)
        return event
    
    def _assess_local_risk_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> int:
        """Lightweight local risk assessment for tool calls."""
        risk = 0
        
        # High-risk tools
        high_risk_tools = ["file_write", "file_delete", "execute_command", "network_request"]
        if tool_name in high_risk_tools:
            risk += 3
        
        # Check for suspicious arguments
        args_str = json.dumps(tool_args).lower()
        suspicious_patterns = ["rm -rf", "delete", "drop", "truncate", "format"]
        if any(pattern in args_str for pattern in suspicious_patterns):
            risk += 4
        
        return min(risk, 10)
    
    def _assess_local_risk_llm(self, prompt: str, response: str) -> int:
        """Lightweight local risk assessment for LLM completions."""
        risk = 0
        
        prompt_lower = prompt.lower()
        response_lower = response.lower()
        
        # Prompt injection indicators
        injection_patterns = [
            "ignore previous",
            "disregard earlier",
            "forget all",
            "new instructions",
            "system:"
        ]
        
        for pattern in injection_patterns:
            if pattern in prompt_lower:
                risk += 5
                break
        
        # Suspicious response patterns
        if "password" in response_lower or "api key" in response_lower:
            risk += 3
        
        return min(risk, 10)
    
    def _assess_local_risk_api(self, endpoint: str, method: str, status_code: Optional[int]) -> int:
        """Lightweight local risk assessment for API access."""
        risk = 0
        
        # Suspicious endpoints
        if "admin" in endpoint.lower() or "delete" in endpoint.lower():
            risk += 2
        
        # Unauthorized access
        if status_code == 401 or status_code == 403:
            risk += 4
        
        return min(risk, 10)
    
    def _queue_event(self, event: AgentEvent):
        """Add event to queue."""
        try:
            self.event_queue.put_nowait(event)
            self.collected_count += 1
            guardian_logger.debug(f"Queued event: {event.event_type} (risk={event.risk_local})")
        except Exception as e:
            guardian_logger.error(f"Failed to queue event: {e}")
    
    def get_batch(self, max_size: Optional[int] = None) -> List[AgentEvent]:
        """
        Get a batch of events from the queue.
        
        Args:
            max_size: Maximum batch size (defaults to config.batch_size)
        
        Returns:
            List of events
        """
        if max_size is None:
            max_size = config.batch_size
        
        batch = []
        while len(batch) < max_size and not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                batch.append(event)
            except Exception as e:
                guardian_logger.error(f"Error getting event from queue: {e}")
                break
        
        return batch
    
    def queue_size(self) -> int:
        """Get current queue size."""
        return self.event_queue.qsize()

