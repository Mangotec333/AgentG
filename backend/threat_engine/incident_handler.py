"""
Incident handler - integrates threat engine with incident system.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import threat_logger
from incident.detector import IncidentDetector
from incident.timeline_builder import TimelineBuilder
from incident.rca_generator import RCAGenerator
from incident.pdf_report import PDFReportGenerator
from incident.incident_db import IncidentDB
from patterns.scripts.auto_extract_patterns import PatternExtractor
from backend.compliance_engine.compliance_mapper import ComplianceMapper
from backend.compliance_engine.evidence_collector import EvidenceCollector
from backend.compliance_engine.compliance_report import ComplianceReportGenerator


class IncidentHandler:
    """Handles incident creation and processing."""
    
    def __init__(self):
        self.detector = IncidentDetector()
        self.timeline_builder = TimelineBuilder()
        self.rca_generator = RCAGenerator()
        self.pdf_generator = PDFReportGenerator()
        self.incident_db = IncidentDB()
        self.pattern_extractor = PatternExtractor()
        self.compliance_mapper = ComplianceMapper()
        self.evidence_collector = EvidenceCollector()
        self.compliance_report_generator = ComplianceReportGenerator()
    
    async def handle_high_risk_event(
        self,
        event: dict,
        risk_analysis: dict,
        workspace_id: str
    ) -> dict:
        """
        Handle a high-risk event by creating and processing an incident.
        
        Args:
            event: Trigger event
            risk_analysis: Risk analysis results
            workspace_id: Workspace identifier
        
        Returns:
            Created incident dictionary
        """
        threat_logger.info(f"Handling high-risk event: {event.get('id')}")
        
        # Create incident
        incident = self.detector.create_incident(
            trigger_event=event,
            risk_analysis=risk_analysis,
            workspace_id=workspace_id
        )
        
        # Build timeline
        timeline = await self.timeline_builder.build_timeline(
            trigger_event_id=event.get("id"),
            workspace_id=workspace_id
        )
        incident["timeline"] = timeline
        
        # Generate RCA
        rca = await self.rca_generator.generate_rca(
            incident=incident,
            timeline=timeline,
            risk_analysis=risk_analysis
        )
        incident["rca_summary"] = rca.get("root_cause_analysis", "")
        incident["summary"] = rca.get("executive_summary", "")
        
        # Get compliance mapping
        compliance_mapping = self.compliance_mapper.map_event(event)
        
        # Collect compliance evidence
        evidence_path = self.evidence_collector.collect_incident_evidence(
            incident_id=incident["id"],
            trigger_event=event,
            related_events=timeline,
            compliance_mapping=compliance_mapping,
            risk_analysis=risk_analysis
        )
        
        # Generate PDF report
        pdf_path = self.pdf_generator.generate_pdf(
            incident=incident,
            rca=rca,
            timeline=timeline
        )
        incident["pdf_path"] = pdf_path
        
        # Generate compliance report
        compliance_report_path = self.compliance_report_generator.generate_report(
            incident=incident,
            compliance_mapping=compliance_mapping,
            risk_analysis=risk_analysis,
            timeline=timeline,
            rca=rca
        )
        incident["compliance_report_path"] = compliance_report_path
        
        # Store incident in database
        await self.incident_db.create_incident(incident)
        
        # Update incident with RCA details
        await self.incident_db.update_incident(incident["id"], {
            "summary": incident["summary"],
            "rca_summary": incident["rca_summary"],
            "timeline": timeline,
            "pdf_path": pdf_path
        })
        
        # Auto-extract patterns (flywheel)
        try:
            extracted_patterns = self.pattern_extractor.extract_from_incident(incident)
            if extracted_patterns:
                threat_logger.info(f"Extracted {len(extracted_patterns)} new patterns from incident")
        except Exception as e:
            threat_logger.error(f"Error extracting patterns: {e}")
        
        threat_logger.info(f"Incident {incident['id']} created and processed")
        return incident

