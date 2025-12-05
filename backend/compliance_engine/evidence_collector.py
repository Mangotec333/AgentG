"""
Compliance evidence collector.
Collects logs, traces, and snapshots for audit and regulatory purposes.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import backend_logger
from shared.config import BackendConfig


class EvidenceCollector:
    """Collects compliance evidence for incidents."""
    
    def __init__(self, evidence_dir: str = "evidence"):
        self.config = BackendConfig()
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(exist_ok=True)
    
    def collect_incident_evidence(
        self,
        incident_id: str,
        trigger_event: Dict[str, Any],
        related_events: List[Dict[str, Any]],
        compliance_mapping: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> str:
        """
        Collect evidence for a compliance incident.
        
        Args:
            incident_id: Incident identifier
            trigger_event: Event that triggered the incident
            related_events: Related events in timeline
            compliance_mapping: Compliance mapping results
            risk_analysis: Risk analysis results
        
        Returns:
            Path to evidence directory
        """
        evidence_path = self.evidence_dir / incident_id
        evidence_path.mkdir(exist_ok=True)
        
        # Collect trigger event
        self._save_event(evidence_path / "trigger_event.json", trigger_event)
        
        # Collect related events
        self._save_events(evidence_path / "related_events.json", related_events)
        
        # Collect compliance mapping
        self._save_json(evidence_path / "compliance_mapping.json", compliance_mapping)
        
        # Collect risk analysis
        self._save_json(evidence_path / "risk_analysis.json", risk_analysis)
        
        # Collect agent traces
        agent_traces = self._extract_agent_traces(related_events)
        self._save_json(evidence_path / "agent_traces.json", agent_traces)
        
        # Collect LLM inputs/outputs
        llm_data = self._extract_llm_data(related_events)
        self._save_json(evidence_path / "llm_data.json", llm_data)
        
        # Collect tool calls
        tool_calls = self._extract_tool_calls(related_events)
        self._save_json(evidence_path / "tool_calls.json", tool_calls)
        
        # Collect API chains
        api_chains = self._extract_api_chains(related_events)
        self._save_json(evidence_path / "api_chains.json", api_chains)
        
        # Collect raw payloads
        raw_payloads = self._extract_raw_payloads(related_events)
        self._save_json(evidence_path / "raw_payloads.json", raw_payloads)
        
        # Create evidence manifest
        manifest = {
            "incident_id": incident_id,
            "collected_at": datetime.utcnow().isoformat(),
            "evidence_files": [
                "trigger_event.json",
                "related_events.json",
                "compliance_mapping.json",
                "risk_analysis.json",
                "agent_traces.json",
                "llm_data.json",
                "tool_calls.json",
                "api_chains.json",
                "raw_payloads.json"
            ],
            "event_count": len(related_events),
            "compliance_standards": compliance_mapping.get("affected_standards", []),
            "violation_count": compliance_mapping.get("violation_count", 0)
        }
        self._save_json(evidence_path / "manifest.json", manifest)
        
        backend_logger.info(f"Collected evidence for incident {incident_id} at {evidence_path}")
        return str(evidence_path)
    
    def _save_event(self, path: Path, event: Dict[str, Any]):
        """Save a single event."""
        self._save_json(path, event)
    
    def _save_events(self, path: Path, events: List[Dict[str, Any]]):
        """Save multiple events."""
        self._save_json(path, events)
    
    def _save_json(self, path: Path, data: Any):
        """Save JSON data to file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _extract_agent_traces(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract agent trace information."""
        traces = []
        for event in events:
            traces.append({
                "timestamp": event.get("timestamp"),
                "agent_id": event.get("agent_id"),
                "workflow_id": event.get("workflow_id"),
                "event_type": event.get("event_type"),
                "metadata": event.get("metadata", {})
            })
        return traces
    
    def _extract_llm_data(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract LLM input/output data."""
        llm_data = []
        for event in events:
            if event.get("event_type") == "llm_completion":
                payload = event.get("payload", {})
                llm_data.append({
                    "timestamp": event.get("timestamp"),
                    "prompt": payload.get("prompt", "")[:1000],  # Truncate
                    "response": payload.get("response", "")[:2000],  # Truncate
                    "model": payload.get("model"),
                    "metadata": event.get("metadata", {})
                })
        return llm_data
    
    def _extract_tool_calls(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tool call information."""
        tool_calls = []
        for event in events:
            if event.get("event_type") == "tool_call":
                payload = event.get("payload", {})
                tool_calls.append({
                    "timestamp": event.get("timestamp"),
                    "tool_name": payload.get("tool_name"),
                    "tool_args": payload.get("tool_args", {}),
                    "return_value": payload.get("return_value"),
                    "metadata": event.get("metadata", {})
                })
        return tool_calls
    
    def _extract_api_chains(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract API call chains."""
        api_chains = []
        for event in events:
            if event.get("event_type") == "api_access":
                payload = event.get("payload", {})
                api_chains.append({
                    "timestamp": event.get("timestamp"),
                    "endpoint": payload.get("endpoint"),
                    "method": payload.get("method"),
                    "status_code": payload.get("status_code"),
                    "metadata": event.get("metadata", {})
                })
        return api_chains
    
    def _extract_raw_payloads(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract raw payloads (sanitized)."""
        raw_payloads = []
        for event in events:
            raw_payloads.append({
                "event_id": event.get("id"),
                "timestamp": event.get("timestamp"),
                "raw": event.get("raw", "")[:500],  # Truncate for safety
                "event_type": event.get("event_type")
            })
        return raw_payloads

