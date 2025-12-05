"""
PII (Personally Identifiable Information) cleaning utilities.
Removes sensitive data before storage/analysis.
"""
import re
from typing import Dict, Any, List


class PIICleaner:
    """Removes PII from event data."""
    
    # Common PII patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    IP_PATTERN = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    
    REPLACEMENT = "[REDACTED]"
    
    @classmethod
    def clean_string(cls, text: str) -> str:
        """Remove PII from a string."""
        if not isinstance(text, str):
            return text
        
        cleaned = text
        patterns = [
            (cls.EMAIL_PATTERN, "[EMAIL]"),
            (cls.PHONE_PATTERN, "[PHONE]"),
            (cls.SSN_PATTERN, "[SSN]"),
            (cls.CREDIT_CARD_PATTERN, "[CARD]"),
            (cls.IP_PATTERN, "[IP]"),
        ]
        
        for pattern, replacement in patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    @classmethod
    def clean_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively clean PII from a dictionary."""
        if not isinstance(data, dict):
            if isinstance(data, str):
                return cls.clean_string(data)
            return data
        
        cleaned = {}
        for key, value in data.items():
            # Skip cleaning certain metadata fields
            if key in ["agent_id", "workspace_id", "workflow_id", "event_type"]:
                cleaned[key] = value
            elif isinstance(value, str):
                cleaned[key] = cls.clean_string(value)
            elif isinstance(value, dict):
                cleaned[key] = cls.clean_dict(value)
            elif isinstance(value, list):
                cleaned[key] = [cls.clean_dict(item) if isinstance(item, dict) 
                               else cls.clean_string(item) if isinstance(item, str) 
                               else item for item in value]
            else:
                cleaned[key] = value
        
        return cleaned
    
    @classmethod
    def clean_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Clean PII from an event while preserving structure."""
        cleaned = event.copy()
        
        # Clean payload and raw fields
        if "payload" in cleaned:
            cleaned["payload"] = cls.clean_dict(cleaned["payload"])
        
        if "raw" in cleaned:
            cleaned["raw"] = cls.clean_string(cleaned["raw"])
        
        if "metadata" in cleaned:
            # Preserve non-PII metadata
            metadata = cleaned["metadata"].copy()
            # Only clean string values in metadata
            cleaned["metadata"] = {
                k: cls.clean_string(v) if isinstance(v, str) else v
                for k, v in metadata.items()
            }
        
        return cleaned

