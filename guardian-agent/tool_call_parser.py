"""
Tool call parser for extracting tool usage from agent traces.
"""
import re
import json
from typing import Dict, Any, List, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import guardian_logger


class ToolCallParser:
    """Parses tool calls from various formats."""
    
    # Common tool call patterns
    PATTERNS = {
        "function_call": re.compile(r'(\w+)\(([^)]*)\)'),
        "json_tool": re.compile(r'{"tool":\s*"([^"]+)",\s*"args":\s*({[^}]*})'),
        "python_call": re.compile(r'(\w+)\.(\w+)\(([^)]*)\)'),
    }
    
    @staticmethod
    def parse_from_string(text: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from a string.
        
        Args:
            text: Text containing tool calls
        
        Returns:
            List of parsed tool calls
        """
        tool_calls = []
        
        # Try JSON format first
        try:
            if text.strip().startswith('{'):
                data = json.loads(text)
                if isinstance(data, dict) and "tool" in data:
                    tool_calls.append({
                        "tool_name": data.get("tool"),
                        "tool_args": data.get("args", {}),
                        "return_value": data.get("return_value")
                    })
                    return tool_calls
        except json.JSONDecodeError:
            pass
        
        # Try function call pattern
        for match in ToolCallParser.PATTERNS["function_call"].finditer(text):
            tool_name = match.group(1)
            args_str = match.group(2)
            
            # Try to parse args as JSON
            tool_args = {}
            if args_str:
                try:
                    tool_args = json.loads(args_str)
                except json.JSONDecodeError:
                    # Fallback: treat as string
                    tool_args = {"raw": args_str}
            
            tool_calls.append({
                "tool_name": tool_name,
                "tool_args": tool_args,
                "return_value": None
            })
        
        return tool_calls
    
    @staticmethod
    def extract_tool_metadata(tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from a tool call.
        
        Args:
            tool_call: Parsed tool call dictionary
        
        Returns:
            Metadata dictionary
        """
        metadata = {
            "tool_name": tool_call.get("tool_name"),
            "arg_count": len(tool_call.get("tool_args", {})),
            "has_return": tool_call.get("return_value") is not None
        }
        
        # Add risk indicators
        tool_name = tool_call.get("tool_name", "").lower()
        high_risk_tools = ["delete", "remove", "write", "execute", "exec"]
        metadata["is_high_risk"] = any(risk in tool_name for risk in high_risk_tools)
        
        return metadata

