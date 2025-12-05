"""
Threat engine processor - main entry point for threat analysis.
"""
import asyncpg
import json
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import threat_logger
from shared.config import BackendConfig
from backend.threat_engine.risk import RiskScorer
from backend.threat_engine.incident_handler import IncidentHandler


class ThreatEngineProcessor:
    """Processes events through the threat engine."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.risk_scorer = RiskScorer()
        self.incident_handler = IncidentHandler()
        self.pool = None
    
    async def _get_pool(self):
        """Get database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.config.database_url)
        return self.pool
    
    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single event through the threat engine.
        
        Args:
            event: Event dictionary
        
        Returns:
            Processing results with risk scores
        """
        # Calculate risk scores
        risk_analysis = await self.risk_scorer.score_event(event)
        
        # Store risk scores in database
        await self._store_risk_scores(event.get("id"), risk_analysis)
        
        # Update event with risk score
        await self._update_event_risk(event.get("id"), risk_analysis["total_risk"])
        
        # Check if incident should be triggered
        if risk_analysis["total_risk"] >= self.config.risk_threshold_incident:
            threat_logger.warning(
                f"High-risk event detected: {event.get('id')} "
                f"(risk={risk_analysis['total_risk']})"
            )
            # Trigger incident creation (handled by incident system)
            await self._trigger_incident(event, risk_analysis)
        
        return risk_analysis
    
    async def process_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of events.
        
        Args:
            events: List of events
        
        Returns:
            List of processing results
        """
        results = []
        for event in events:
            try:
                result = await self.process_event(event)
                results.append(result)
            except Exception as e:
                threat_logger.error(f"Error processing event {event.get('id')}: {e}")
        
        return results
    
    async def _store_risk_scores(self, event_id: str, risk_analysis: Dict[str, Any]):
        """Store risk scores in database."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO risk_scores (
                    event_id, rules_risk, model_risk, pattern_risk,
                    compliance_risk, total_risk, model_details
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                event_id,
                risk_analysis.get("rules_risk", 0),
                risk_analysis.get("model_risk", 0),
                risk_analysis.get("pattern_risk", 0),
                risk_analysis.get("compliance_risk", 0),
                risk_analysis.get("total_risk", 0),
                json.dumps(risk_analysis.get("llm_analysis", {}))
            )
    
    async def _update_event_risk(self, event_id: str, risk_score: int):
        """Update event with risk score."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE events SET risk_engine = $1 WHERE id = $2",
                risk_score,
                event_id
            )
    
    async def _trigger_incident(self, event: Dict[str, Any], risk_analysis: Dict[str, Any]):
        """Trigger incident creation."""
        workspace_id = event.get("workspace_id")
        if not workspace_id:
            threat_logger.error("Cannot create incident: missing workspace_id")
            return
        
        try:
            incident = await self.incident_handler.handle_high_risk_event(
                event=event,
                risk_analysis=risk_analysis,
                workspace_id=workspace_id
            )
            threat_logger.info(f"Incident {incident.get('id')} created successfully")
        except Exception as e:
            threat_logger.error(f"Error creating incident: {e}")

