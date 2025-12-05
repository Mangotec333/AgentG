"""
Compliance API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import backend_logger
from backend.compliance_engine.compliance_mapper import ComplianceMapper
from backend.compliance_engine.compliance_risk import ComplianceRiskScorer
from backend.ingestion.security import verify_api_key
from incident.incident_db import IncidentDB

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

compliance_mapper = ComplianceMapper()
compliance_scorer = ComplianceRiskScorer()
incident_db = IncidentDB()


@router.get("/summary")
async def get_compliance_summary(
    workspace_id: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get compliance summary for a workspace.
    
    Returns:
        Summary of compliance violations and risk scores
    """
    if not verify_api_key(x_api_key, workspace_id):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # In production, would query database for aggregated stats
    return {
        "workspace_id": workspace_id,
        "total_violations": 0,
        "affected_standards": [],
        "risk_level": "minimal"
    }


@router.get("/events")
async def get_compliance_events(
    workspace_id: str,
    limit: int = 100,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get events with compliance violations.
    
    Returns:
        List of events with compliance flags
    """
    if not verify_api_key(x_api_key, workspace_id):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # In production, would query database
    return {
        "events": [],
        "total": 0
    }


@router.get("/incidents")
async def get_compliance_incidents(
    workspace_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get incidents with compliance violations.
    
    Returns:
        List of compliance incidents
    """
    if not verify_api_key(x_api_key, workspace_id):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    incidents = await incident_db.list_incidents(workspace_id, status, limit)
    return {
        "incidents": incidents,
        "total": len(incidents)
    }


@router.get("/report/{incident_id}")
async def get_compliance_report(
    incident_id: str,
    workspace_id: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get compliance report for an incident.
    
    Returns:
        Compliance report data
    """
    if not verify_api_key(x_api_key, workspace_id):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    incident = await incident_db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "incident_id": incident_id,
        "compliance_report_path": incident.get("compliance_report_path"),
        "evidence_path": f"evidence/{incident_id}/"
    }

