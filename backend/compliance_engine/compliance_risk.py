"""
Compliance risk scoring engine.
Combines all compliance standard scores into unified risk.
"""
from typing import Dict, Any
from backend.compliance_engine.compliance_mapper import ComplianceMapper


class ComplianceRiskScorer:
    """Calculates unified compliance risk score."""
    
    def __init__(self):
        self.mapper = ComplianceMapper()
    
    def score_event(self, event: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate compliance risk score for an event.
        
        Args:
            event: Event dictionary
            context: Additional context
        
        Returns:
            Compliance risk analysis
        """
        # Get compliance mapping
        mapping = self.mapper.map_event(event, context)
        
        # Calculate total compliance risk
        compliance_risk = (
            mapping["hipaa"]["risk_score"] +
            mapping["glba"]["risk_score"] +
            mapping["pci"]["risk_score"] +
            mapping["soc2"]["risk_score"] +
            mapping["nist"]["risk_score"]
        )
        
        # Add AI Act risk value
        ai_act_risk_map = {
            "minimal": 0,
            "limited": 2,
            "high": 5,
            "unacceptable": 10
        }
        ai_act_category = mapping["ai_act"]["risk_category"]
        ai_act_risk = ai_act_risk_map.get(ai_act_category, 0)
        if mapping["ai_act"]["banned"]:
            ai_act_risk = 10
        
        compliance_risk += ai_act_risk
        
        # Determine risk level
        risk_level = self._get_risk_level(compliance_risk)
        
        # Count violations
        violation_count = sum([
            len(mapping["hipaa"]["violations"]),
            len(mapping["glba"]["violations"]),
            len(mapping["pci"]["violations"]),
            len(mapping["soc2"]["violations"]),
            len(mapping["nist"]["violations"])
        ])
        
        # Get affected standards
        affected_standards = []
        if mapping["hipaa"]["has_violation"]:
            affected_standards.append("HIPAA")
        if mapping["glba"]["has_violation"]:
            affected_standards.append("GLBA")
        if mapping["pci"]["has_violation"]:
            affected_standards.append("PCI-DSS")
        if mapping["soc2"]["has_violation"]:
            affected_standards.append("SOC2")
        if mapping["nist"]["has_violation"]:
            affected_standards.append("NIST")
        if mapping["ai_act"]["risk_category"] != "minimal":
            affected_standards.append("EU-AI-Act")
        
        return {
            "compliance_risk": compliance_risk,
            "risk_level": risk_level,
            "violation_count": violation_count,
            "affected_standards": affected_standards,
            "mapping": mapping,
            "thresholds": {
                "minimal": (0, 4),
                "warning": (5, 10),
                "violations": (11, 20),
                "major_incident": (21, 100)
            }
        }
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level category."""
        if risk_score <= 4:
            return "minimal"
        elif risk_score <= 10:
            return "warning"
        elif risk_score <= 20:
            return "violations"
        else:
            return "major_incident"

