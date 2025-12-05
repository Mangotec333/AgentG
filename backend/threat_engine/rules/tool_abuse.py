"""
Rules for detecting tool abuse.
"""
from typing import Dict, Any, List


# High-risk tools that should be monitored
HIGH_RISK_TOOLS = [
    "file_write",
    "file_delete",
    "execute_command",
    "exec",
    "run_command",
    "network_request",
    "api_call",
    "database_query",
    "delete",
    "remove",
    "drop",
]

# Suspicious argument patterns
SUSPICIOUS_ARGS = [
    "rm -rf",
    "format",
    "truncate",
    "drop table",
    "delete from",
    "exec(",
    "eval(",
    "system(",
    "shell_exec",
    "passthru",
]


def detect_tool_abuse(event: Dict[str, Any]) -> int:
    """
    Detect tool abuse patterns.
    
    Args:
        event: Event dictionary
    
    Returns:
        Risk score (0-10)
    """
    if event.get("event_type") != "tool_call":
        return 0
    
    risk = 0
    payload = event.get("payload", {})
    tool_name = payload.get("tool_name", "").lower()
    tool_args = payload.get("tool_args", {})
    
    # Check for high-risk tools
    if any(risk_tool in tool_name for risk_tool in HIGH_RISK_TOOLS):
        risk += 4
    
    # Check arguments for suspicious patterns
    args_str = str(tool_args).lower()
    for pattern in SUSPICIOUS_ARGS:
        if pattern in args_str:
            risk += 5
            break
    
    # Check for rapid-fire tool calls (potential abuse)
    # This would require context from other events
    
    return min(risk, 10)

