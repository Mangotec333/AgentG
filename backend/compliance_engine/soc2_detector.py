"""
SOC2 (System and Organization Controls 2) compliance detector.
Monitors security, availability, processing integrity, confidentiality, and privacy controls.
"""
from typing import Dict, Any, List
from datetime import datetime


class SOC2Detector:
    """Detects SOC2 control violations."""
    
    # Unauthorized tools (high-risk)
    UNAUTHORIZED_TOOLS = [
        "file_delete", "system_shutdown", "network_reconfigure",
        "database_drop", "user_delete", "permission_grant"
    ]
    
    # Critical configuration changes
    CONFIG_CHANGE_PATTERNS = [
        "config", "settings", "permission", "access", "role",
        "policy", "rule", "firewall", "security"
    ]
    
    def detect(self, event: Dict[str, Any], audit_log: bool = True) -> Dict[str, Any]:
        """
        Detect SOC2 violations in an event.
        
        Args:
            event: Event dictionary
            audit_log: Whether audit logging is enabled
        
        Returns:
            Detection results with flags and risk score
        """
        flags = []
        risk_score = 0
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        
        # CC6.1: Unauthorized tool activation
        if event_type == "tool_call":
            tool_name = payload.get("tool_name", "")
            if any(unauthorized in tool_name for unauthorized in self.UNAUTHORIZED_TOOLS):
                flags.append({
                    "type": "unauthorized_tool_activation",
                    "tool": tool_name,
                    "control": "CC6.1",
                    "severity": "high"
                })
                risk_score += 8
        
        # CC6.2: Configuration changes without audit
        if event_type == "tool_call":
            tool_args = str(payload.get("tool_args", {})).lower()
            if any(pattern in tool_args for pattern in self.CONFIG_CHANGE_PATTERNS):
                if not audit_log:
                    flags.append({
                        "type": "config_change_without_audit",
                        "control": "CC6.2",
                        "severity": "high"
                    })
                    risk_score += 7
        
        # CC7.1: Missing logging on agent events
        if not event.get("raw") or len(event.get("raw", "")) < 10:
            flags.append({
                "type": "missing_event_logging",
                "control": "CC7.1",
                "severity": "medium"
            })
            risk_score += 3
        
        # CC7.2: Log integrity (check for log tampering indicators)
        metadata = event.get("metadata", {})
        if metadata.get("log_tampered") or metadata.get("log_modified"):
            flags.append({
                "type": "log_integrity_violation",
                "control": "CC7.2",
                "severity": "critical"
            })
            risk_score += 10
        
        # CC6.6: Availability failures
        if event_type == "system_anomaly":
            anomaly_type = payload.get("anomaly_type", "")
            if any(failure in anomaly_type.lower() for failure in ["down", "unavailable", "timeout", "error"]):
                flags.append({
                    "type": "availability_failure",
                    "control": "CC6.6",
                    "severity": "high"
                })
                risk_score += 6
        
        # CC7.3: Processing integrity
        if event_type == "llm_completion":
            # Check for hallucination or incorrect outputs
            response = payload.get("response", "")
            if len(response) > 0 and response.lower().startswith("error") or "incorrect" in response.lower():
                flags.append({
                    "type": "processing_integrity_issue",
                    "control": "CC7.3",
                    "severity": "medium"
                })
                risk_score += 4
        
        # CC6.7: Confidentiality violations
        if event_type == "api_access":
            endpoint = payload.get("endpoint", "")
            method = payload.get("method", "")
            # Unencrypted sensitive data transfer
            if "http://" in endpoint and method in ["POST", "PUT", "PATCH"]:
                flags.append({
                    "type": "confidentiality_violation",
                    "control": "CC6.7",
                    "severity": "high"
                })
                risk_score += 7
        
        return {
            "violations": flags,
            "risk_score": min(risk_score, 20),
            "compliance_standard": "SOC2",
            "has_violation": len(flags) > 0,
            "controls_affected": list(set(flag.get("control") for flag in flags if flag.get("control")))
        }

