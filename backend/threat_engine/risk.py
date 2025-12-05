"""
Unified risk scoring system.
Combines rules-based, LLM-based, and pattern-based detection.
"""
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import threat_logger
from backend.threat_engine.rules import (
    prompt_injection,
    jailbreaking,
    tool_abuse,
    api_abuse,
    output_drift,
    entropy_check
)
from backend.threat_engine.models.llm_analyzer import LLMAnalyzer
from patterns.matcher import PatternMatcher
from backend.compliance_engine.compliance_risk import ComplianceRiskScorer


class RiskScorer:
    """Unified risk scoring system."""
    
    def __init__(self):
        self.llm_analyzer = LLMAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.compliance_scorer = ComplianceRiskScorer()
    
    async def score_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an event.
        
        Args:
            event: Event dictionary
        
        Returns:
            Risk score breakdown
        """
        # Rules-based risk
        rules_risk = self._calculate_rules_risk(event)
        
        # Pattern-based risk
        pattern_matches = self.pattern_matcher.match(event)
        pattern_risk = self._calculate_pattern_risk(pattern_matches)
        
        # LLM-based risk
        llm_analysis = await self.llm_analyzer.analyze_event(event)
        model_risk = llm_analysis.get("consensus_risk", 0)
        
        # Compliance risk
        compliance_analysis = self.compliance_scorer.score_event(event)
        compliance_risk = compliance_analysis.get("compliance_risk", 0)
        # Normalize compliance risk to 0-10 scale
        compliance_risk_normalized = min(compliance_risk / 2, 10)
        
        # Total risk (weighted combination including compliance)
        total_risk = min(
            int((rules_risk * 0.3) + (pattern_risk * 0.25) + (model_risk * 0.25) + (compliance_risk_normalized * 0.2)),
            10
        )
        
        return {
            "rules_risk": rules_risk,
            "pattern_risk": pattern_risk,
            "model_risk": model_risk,
            "compliance_risk": compliance_risk_normalized,
            "compliance_analysis": compliance_analysis,
            "total_risk": total_risk,
            "pattern_matches": pattern_matches,
            "llm_analysis": llm_analysis,
            "risk_level": self._get_risk_level(total_risk)
        }
    
    def _calculate_rules_risk(self, event: Dict[str, Any]) -> int:
        """Calculate risk from rules-based detection."""
        risks = [
            prompt_injection.detect_prompt_injection(event),
            jailbreaking.detect_jailbreaking(event),
            tool_abuse.detect_tool_abuse(event),
            api_abuse.detect_api_abuse(event),
            output_drift.detect_output_drift(event),
            entropy_check.detect_high_entropy(event),
        ]
        
        # Take maximum risk (most severe rule violation)
        return max(risks) if risks else 0
    
    def _calculate_pattern_risk(self, pattern_matches: list) -> int:
        """Calculate risk from pattern matches."""
        if not pattern_matches:
            return 0
        
        # Sum severity scores from matched patterns
        total_severity = 0
        for match in pattern_matches:
            severity = match.get("severity", "low")
            if severity == "high":
                total_severity += 5
            elif severity == "medium":
                total_severity += 3
            else:
                total_severity += 1
        
        return min(total_severity, 10)
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level category."""
        if risk_score <= 3:
            return "normal"
        elif risk_score <= 6:
            return "suspicious"
        else:
            return "incident"

