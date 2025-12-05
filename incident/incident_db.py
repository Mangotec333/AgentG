"""
Incident database operations.
"""
import asyncpg
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import backend_logger
from shared.config import BackendConfig


class IncidentDB:
    """Database operations for incidents."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.pool = None
    
    async def _get_pool(self):
        """Get database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.config.database_url)
        return self.pool
    
    async def create_incident(self, incident: Dict[str, Any]) -> str:
        """
        Create an incident in database.
        
        Args:
            incident: Incident dictionary
        
        Returns:
            Incident ID
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO incidents (
                    id, workspace_id, agent_id, trigger_event_id,
                    severity, status, title, summary, rca_summary,
                    timeline, pdf_path, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                incident.get("id"),
                incident.get("workspace_id"),
                incident.get("agent_id"),
                incident.get("trigger_event_id"),
                incident.get("severity"),
                incident.get("status"),
                incident.get("title"),
                incident.get("summary"),
                incident.get("rca_summary"),
                json.dumps(incident.get("timeline", [])),
                incident.get("pdf_path"),
                incident.get("created_at"),
                incident.get("updated_at")
            )
        
        backend_logger.info(f"Created incident: {incident.get('id')}")
        return incident.get("id")
    
    async def update_incident(self, incident_id: str, updates: Dict[str, Any]):
        """Update an incident."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            set_clauses = []
            values = []
            param_num = 1
            
            for key, value in updates.items():
                if key == "timeline":
                    set_clauses.append(f"{key} = ${param_num}")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = ${param_num}")
                    values.append(value)
                param_num += 1
            
            set_clauses.append(f"updated_at = ${param_num}")
            values.append(datetime.utcnow().isoformat())
            values.append(incident_id)
            
            query = f"UPDATE incidents SET {', '.join(set_clauses)} WHERE id = ${param_num}"
            await conn.execute(query, *values)
    
    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get an incident by ID."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM incidents WHERE id = $1",
                incident_id
            )
            
            if row:
                incident = dict(row)
                if incident.get("timeline"):
                    incident["timeline"] = json.loads(incident["timeline"])
                return incident
        
        return None
    
    async def list_incidents(
        self,
        workspace_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List incidents for a workspace."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            query = "SELECT * FROM incidents WHERE workspace_id = $1"
            params = [workspace_id]
            
            if status:
                query += " AND status = $2"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT $3"
            params.append(limit)
            
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

