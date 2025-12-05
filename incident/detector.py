"""
Incident detector - triggers incidents from high-risk events.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import backend_logger


class IncidentDetector:
    """Detects and creates incidents from high-risk events."""
    
    def __init__(self, risk_threshold: int = 7):
        self.risk_threshold = risk_threshold
    
    def should_trigger_incident(self, event: Dict[str, Any], risk_score: int) -> bool:
        """
        Determine if an incident should be triggered.
        
        Args:
            event: Event dictionary
            risk_score: Calculated risk score
        
        Returns:
            True if incident should be triggered
        """
        return risk_score >= self.risk_threshold
    
    def create_incident(
        self,
        trigger_event: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Create an incident from a trigger event.
        
        Args:
            trigger_event: Event that triggered the incident
            risk_analysis: Risk analysis results
            workspace_id: Workspace identifier
        
        Returns:
            Incident dictionary
        """
        incident_id = str(uuid.uuid4())
        
        # Determine severity
        risk_score = risk_analysis.get("total_risk", 0)
        if risk_score >= 9:
            severity = "critical"
        elif risk_score >= 7:
            severity = "high"
        else:
            severity = "medium"
        
        # Create title
        title = self._generate_title(trigger_event, risk_analysis)
        
        incident = {
            "id": incident_id,
            "workspace_id": workspace_id,
            "agent_id": trigger_event.get("agent_id"),
            "trigger_event_id": trigger_event.get("id"),
            "severity": severity,
            "status": "open",
            "title": title,
            "summary": "",
            "rca_summary": "",
            "timeline": [],
            "pdf_path": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "risk_analysis": risk_analysis
        }
        
        backend_logger.info(f"Created incident: {incident_id} (severity={severity})")
        return incident
    
    def _generate_title(self, event: Dict[str, Any], risk_analysis: Dict[str, Any]) -> str:
        """Generate incident title."""
        event_type = event.get("event_type", "unknown")
        risk_level = risk_analysis.get("risk_level", "unknown")
        
        # Check for pattern matches
        pattern_matches = risk_analysis.get("pattern_matches", [])
        if pattern_matches:
            category = pattern_matches[0].get("category", "threat")
            return f"{category.replace('_', ' ').title()} Detected - {risk_level.upper()}"
        
        return f"{event_type.replace('_', ' ').title()} - {risk_level.upper()} Risk"

