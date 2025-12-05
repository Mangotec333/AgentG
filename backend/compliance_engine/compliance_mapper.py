"""
Compliance mapping layer - maps events to all compliance standards.
"""
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.compliance_engine.hipaa_detector import HIPAADetector
from backend.compliance_engine.glba_detector import GLBADetector
from backend.compliance_engine.pci_detector import PCIDetector
from backend.compliance_engine.soc2_detector import SOC2Detector
from backend.compliance_engine.nist_detector import NISTDetector
from backend.compliance_engine.ai_act_classifier import AIActClassifier
from shared.logger import backend_logger


class ComplianceMapper:
    """Maps events to all compliance standards."""
    
    def __init__(self):
        self.hipaa_detector = HIPAADetector()
        self.glba_detector = GLBADetector()
        self.pci_detector = PCIDetector()
        self.soc2_detector = SOC2Detector()
        self.nist_detector = NISTDetector()
        self.ai_act_classifier = AIActClassifier()
    
    def map_event(self, event: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Map event to all compliance standards.
        
        Args:
            event: Event dictionary
            context: Additional context (workflow metadata, agent config)
        
        Returns:
            Compliance mapping with all standards
        """
        context = context or {}
        workflow_metadata = context.get("workflow_metadata", {})
        
        # Run all detectors
        hipaa_result = self.hipaa_detector.detect(event)
        glba_result = self.glba_detector.detect(event)
        pci_result = self.pci_detector.detect(event)
        soc2_result = self.soc2_detector.detect(event)
        nist_result = self.nist_detector.detect(event, context)
        ai_act_result = self.ai_act_classifier.classify(event, workflow_metadata)
        
        # Build compliance mapping
        mapping = {
            "event_id": event.get("id"),
            "hipaa": {
                "violations": hipaa_result.get("violations", []),
                "risk_score": hipaa_result.get("risk_score", 0),
                "has_violation": hipaa_result.get("has_violation", False)
            },
            "glba": {
                "violations": glba_result.get("violations", []),
                "risk_score": glba_result.get("risk_score", 0),
                "has_violation": glba_result.get("has_violation", False)
            },
            "pci": {
                "violations": pci_result.get("violations", []),
                "risk_score": pci_result.get("risk_score", 0),
                "has_violation": pci_result.get("has_violation", False)
            },
            "soc2": {
                "violations": soc2_result.get("violations", []),
                "risk_score": soc2_result.get("risk_score", 0),
                "has_violation": soc2_result.get("has_violation", False),
                "controls_affected": soc2_result.get("controls_affected", [])
            },
            "nist": {
                "violations": nist_result.get("violations", []),
                "risk_score": nist_result.get("risk_score", 0),
                "has_violation": nist_result.get("has_violation", False),
                "controls_affected": nist_result.get("controls_affected", [])
            },
            "ai_act": {
                "risk_category": ai_act_result.get("risk_category", "minimal"),
                "banned": ai_act_result.get("banned", False),
                "reasoning": ai_act_result.get("reasoning", []),
                "requirements": ai_act_result.get("requirements", [])
            }
        }
        
        backend_logger.debug(f"Mapped event {event.get('id')} to compliance standards")
        return mapping

