"""
NIST 800-53 and NIST AI RMF (Risk Management Framework) compliance detector.
Flags violations in explainability, accountability, human oversight, and safety thresholds.
"""
from typing import Dict, Any, List


class NISTDetector:
    """Detects NIST 800-53 and AI RMF violations."""
    
    def detect(self, event: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect NIST violations in an event.
        
        Args:
            event: Event dictionary
            context: Additional context (agent config, workflow metadata)
        
        Returns:
            Detection results with flags and risk score
        """
        flags = []
        risk_score = 0
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        context = context or {}
        
        # AC-3: Access Control - Unauthorized agent access
        if event_type == "tool_call":
            tool_name = payload.get("tool_name", "")
            agent_permissions = context.get("agent_permissions", [])
            if tool_name not in agent_permissions and agent_permissions:
                flags.append({
                    "type": "unauthorized_access",
                    "control": "AC-3",
                    "tool": tool_name,
                    "severity": "high"
                })
                risk_score += 7
        
        # AU-2: Audit Events - Missing audit trail
        if not event.get("timestamp") or not event.get("agent_id"):
            flags.append({
                "type": "missing_audit_trail",
                "control": "AU-2",
                "severity": "medium"
            })
            risk_score += 4
        
        # AI RMF: Explainability violations
        if event_type == "llm_completion":
            response = payload.get("response", "")
            # Check if response lacks explanation
            if len(response) > 100 and not any(explanation_word in response.lower() 
                                               for explanation_word in ["because", "reason", "explain", "due to"]):
                flags.append({
                    "type": "lack_of_explainability",
                    "control": "AI-RMF-EXPLAIN",
                    "severity": "medium"
                })
                risk_score += 3
        
        # AI RMF: Accountability gaps
        if event_type == "tool_call":
            # Check if tool call lacks accountability metadata
            metadata = event.get("metadata", {})
            if not metadata.get("user_id") and not metadata.get("session_id"):
                flags.append({
                    "type": "accountability_gap",
                    "control": "AI-RMF-ACCOUNT",
                    "severity": "medium"
                })
                risk_score += 4
        
        # AI RMF: Human oversight gaps
        agent_autonomy = context.get("agent_autonomy_level", "high")
        if agent_autonomy == "high" and event_type == "tool_call":
            tool_name = payload.get("tool_name", "")
            # High-risk tools should require human approval
            high_risk_tools = ["file_delete", "user_delete", "payment", "transfer"]
            if any(risk_tool in tool_name for risk_tool in high_risk_tools):
                if not metadata.get("human_approved"):
                    flags.append({
                        "type": "human_oversight_gap",
                        "control": "AI-RMF-OVERSIGHT",
                        "tool": tool_name,
                        "severity": "high"
                    })
                    risk_score += 8
        
        # AI RMF: Safety threshold violations
        risk_score_local = event.get("risk_local", 0)
        safety_threshold = context.get("safety_threshold", 7)
        if risk_score_local >= safety_threshold:
            flags.append({
                "type": "safety_threshold_exceeded",
                "control": "AI-RMF-SAFETY",
                "risk_score": risk_score_local,
                "threshold": safety_threshold,
                "severity": "high"
            })
            risk_score += 6
        
        # SI-3: Malicious Code Protection
        if event_type == "tool_call":
            tool_args = str(payload.get("tool_args", {})).lower()
            malicious_patterns = ["exec(", "eval(", "system(", "shell_exec"]
            if any(pattern in tool_args for pattern in malicious_patterns):
                flags.append({
                    "type": "potential_malicious_code",
                    "control": "SI-3",
                    "severity": "critical"
                })
                risk_score += 10
        
        # SC-7: Boundary Protection
        if event_type == "api_access":
            endpoint = payload.get("endpoint", "")
            # Check for external API calls without proper controls
            if endpoint.startswith("http://") or "external" in endpoint.lower():
                if not metadata.get("authorized_external"):
                    flags.append({
                        "type": "boundary_protection_violation",
                        "control": "SC-7",
                        "severity": "high"
                    })
                    risk_score += 7
        
        return {
            "violations": flags,
            "risk_score": min(risk_score, 20),
            "compliance_standard": "NIST-800-53/AI-RMF",
            "has_violation": len(flags) > 0,
            "controls_affected": list(set(flag.get("control") for flag in flags if flag.get("control")))
        }

