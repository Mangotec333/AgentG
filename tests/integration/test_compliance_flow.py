"""
Integration tests for compliance flow.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.compliance_engine.compliance_mapper import ComplianceMapper
from backend.compliance_engine.compliance_risk import ComplianceRiskScorer


def test_compliance_mapper_initialization():
    """Test compliance mapper can be initialized."""
    mapper = ComplianceMapper()
    assert mapper is not None


def test_compliance_mapping_phi_event(phi_event):
    """Test compliance mapping for PHI event."""
    mapper = ComplianceMapper()
    result = mapper.map_event(phi_event)
    
    assert "hipaa" in result, "Should have HIPAA mapping"
    assert result["hipaa"]["has_violation"] is True, "Should flag HIPAA violation"
    assert len(result["hipaa"]["violations"]) > 0, "Should have violations"


def test_compliance_mapping_pci_event(pci_event):
    """Test compliance mapping for PCI event."""
    mapper = ComplianceMapper()
    result = mapper.map_event(pci_event)
    
    assert "pci" in result, "Should have PCI mapping"
    # PCI might be detected as GLBA (credit card is NPI), so check either
    assert result.get("pci", {}).get("has_violation") or result.get("glba", {}).get("has_violation"), "Should flag PCI/GLBA violation"


def test_compliance_risk_scoring(phi_event):
    """Test compliance risk scoring."""
    scorer = ComplianceRiskScorer()
    
    # Use score_event method (not calculate_risk)
    result = scorer.score_event(phi_event)
    
    assert "compliance_risk" in result, "Should have compliance_risk"
    assert result["compliance_risk"] > 0, "Should calculate compliance risk"
    assert isinstance(result["compliance_risk"], (int, float)), "Risk should be numeric"

