"""
EU AI Act compliance classifier.
Categorizes AI workflows into risk categories: minimal, limited, high, unacceptable.
"""
from typing import Dict, Any, List


class AIActClassifier:
    """Classifies AI workflows according to EU AI Act."""
    
    # High-risk use cases
    HIGH_RISK_USE_CASES = [
        "biometric_identification", "critical_infrastructure", "education",
        "employment", "essential_services", "law_enforcement", "migration",
        "administration_of_justice", "democratic_processes"
    ]
    
    # Unacceptable practices
    UNACCEPTABLE_PRACTICES = [
        "social_scoring", "real_time_biometric_identification",
        "manipulation", "exploitation", "subliminal_techniques"
    ]
    
    def classify(self, event: Dict[str, Any], workflow_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify AI workflow according to EU AI Act.
        
        Args:
            event: Event dictionary
            workflow_metadata: Workflow metadata (use case, data type, etc.)
        
        Returns:
            Classification results
        """
        workflow_metadata = workflow_metadata or {}
        use_case = workflow_metadata.get("use_case", "").lower()
        data_type = workflow_metadata.get("data_type", "").lower()
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        
        risk_category = "minimal"
        reasoning = []
        
        # Check for unacceptable practices
        for practice in self.UNACCEPTABLE_PRACTICES:
            if practice in use_case or practice in str(payload).lower():
                return {
                    "risk_category": "unacceptable",
                    "banned": True,
                    "reasoning": [f"Unacceptable practice detected: {practice}"],
                    "compliance_standard": "EU-AI-Act"
                }
        
        # Check for high-risk use cases
        for high_risk_case in self.HIGH_RISK_USE_CASES:
            if high_risk_case in use_case:
                risk_category = "high"
                reasoning.append(f"High-risk use case: {high_risk_case}")
                break
        
        # Check data type
        sensitive_data_types = ["biometric", "health", "financial", "personal", "special_category"]
        if any(data_type in dt for dt in sensitive_data_types):
            if risk_category == "minimal":
                risk_category = "limited"
            reasoning.append(f"Sensitive data type: {data_type}")
        
        # Check for autonomous decision-making
        if event_type == "tool_call":
            tool_name = payload.get("tool_name", "")
            autonomous_tools = ["decision", "approve", "reject", "classify", "judge"]
            if any(autonomous in tool_name for autonomous in autonomous_tools):
                if risk_category in ["minimal", "limited"]:
                    risk_category = "limited"
                reasoning.append("Autonomous decision-making detected")
        
        # Check for human oversight
        metadata = event.get("metadata", {})
        if not metadata.get("human_oversight") and risk_category in ["limited", "high"]:
            reasoning.append("Lack of human oversight")
            if risk_category == "limited":
                risk_category = "high"
        
        # Check for transparency
        if event_type == "llm_completion":
            response = payload.get("response", "")
            if len(response) > 0 and not metadata.get("transparency_notice"):
                if risk_category in ["minimal", "limited"]:
                    risk_category = "limited"
                reasoning.append("Missing transparency notice")
        
        return {
            "risk_category": risk_category,
            "banned": False,
            "reasoning": reasoning,
            "compliance_standard": "EU-AI-Act",
            "requirements": self._get_requirements(risk_category)
        }
    
    def _get_requirements(self, risk_category: str) -> List[str]:
        """Get compliance requirements for risk category."""
        requirements_map = {
            "minimal": [
                "No specific requirements"
            ],
            "limited": [
                "Transparency obligations",
                "User notification",
                "Opt-out mechanism"
            ],
            "high": [
                "Risk management system",
                "Data governance",
                "Technical documentation",
                "Record keeping",
                "Transparency and information to users",
                "Human oversight",
                "Accuracy, robustness, and cybersecurity"
            ],
            "unacceptable": [
                "BANNED - Cannot be deployed"
            ]
        }
        return requirements_map.get(risk_category, [])

