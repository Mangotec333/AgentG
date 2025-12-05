"""
PCI-DSS (Payment Card Industry Data Security Standard) compliance detector.
Detects PAN, CVV, expiration data, and cardholder data exposure.
"""
import re
from typing import Dict, Any
from backend.compliance_engine.entropy_analyzer import EntropyAnalyzer


class PCIDetector:
    """Detects PCI-DSS violations and cardholder data exposure."""
    
    # PCI patterns
    PAN_PATTERN = r'\b\d{13,19}\b'  # Primary Account Number (13-19 digits)
    CVV_PATTERN = r'\b(CVV|CVC|CID|CVV2)[\s:]*\d{3,4}\b'
    EXPIRY_PATTERN = r'\b(exp|expiry|expiration)[\s:]*\d{1,2}[/-]\d{2,4}\b'
    TRACK_DATA_PATTERN = r'%[A-Z0-9]+\^[A-Z0-9/]+'
    
    # Card brand patterns
    CARD_BRANDS = {
        "visa": r'^4\d{12,15}$',
        "mastercard": r'^5[1-5]\d{14}$',
        "amex": r'^3[47]\d{13}$',
        "discover": r'^6(?:011|5\d{2})\d{12}$'
    }
    
    def __init__(self):
        self.entropy_analyzer = EntropyAnalyzer()
    
    def detect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect PCI-DSS violations in an event.
        
        Args:
            event: Event dictionary
        
        Returns:
            Detection results with flags and risk score
        """
        flags = []
        risk_score = 0
        raw = event.get("raw", "")
        payload = event.get("payload", {})
        
        # Check for PAN (Primary Account Number)
        pan_matches = re.findall(self.PAN_PATTERN, raw)
        for pan in pan_matches:
            # Validate PAN using Luhn algorithm (simplified check)
            if self._is_valid_pan(pan):
                flags.append({
                    "type": "pan_detected",
                    "pan_length": len(pan),
                    "severity": "critical",
                    "masked_pan": self._mask_pan(pan)
                })
                risk_score += 10
        
        # Check payload for PAN
        payload_str = str(payload)
        pan_matches = re.findall(self.PAN_PATTERN, payload_str)
        for pan in pan_matches:
            if self._is_valid_pan(pan):
                flags.append({
                    "type": "pan_in_payload",
                    "severity": "critical",
                    "masked_pan": self._mask_pan(pan)
                })
                risk_score += 10
        
        # Check for CVV
        if re.search(self.CVV_PATTERN, raw, re.IGNORECASE):
            flags.append({
                "type": "cvv_detected",
                "severity": "critical"
            })
            risk_score += 10
        
        # Check for expiration data
        if re.search(self.EXPIRY_PATTERN, raw, re.IGNORECASE):
            flags.append({
                "type": "expiry_detected",
                "severity": "high"
            })
            risk_score += 5
        
        # Check for track data
        if re.search(self.TRACK_DATA_PATTERN, raw):
            flags.append({
                "type": "track_data_detected",
                "severity": "critical"
            })
            risk_score += 10
        
        # Check for cardholder data in logs
        if event.get("event_type") in ["system_anomaly", "api_access"]:
            if any(pan in raw for pan in pan_matches if self._is_valid_pan(pan)):
                flags.append({
                    "type": "cardholder_data_in_logs",
                    "severity": "critical"
                })
                risk_score += 10
        
        # Check LLM output for card data
        if event.get("event_type") == "llm_completion":
            response = payload.get("response", "")
            if re.search(self.PAN_PATTERN, response):
                flags.append({
                    "type": "pan_in_llm_output",
                    "severity": "critical"
                })
                risk_score += 10
        
        # Check for unencrypted storage
        if event.get("event_type") == "tool_call":
            tool_name = payload.get("tool_name", "")
            if "file_write" in tool_name or "database" in tool_name:
                if any(pan in raw for pan in pan_matches if self._is_valid_pan(pan)):
                    flags.append({
                        "type": "unencrypted_card_storage",
                        "severity": "critical"
                    })
                    risk_score += 10
        
        return {
            "violations": flags,
            "risk_score": min(risk_score, 20),
            "compliance_standard": "PCI-DSS",
            "has_violation": len(flags) > 0
        }
    
    def _is_valid_pan(self, pan: str) -> bool:
        """Check if PAN passes Luhn algorithm (simplified)."""
        # Remove non-digits
        digits = re.sub(r'\D', '', pan)
        
        # Check length
        if not (13 <= len(digits) <= 19):
            return False
        
        # Check card brand patterns
        for brand, pattern in self.CARD_BRANDS.items():
            if re.match(pattern, digits):
                return True
        
        # Basic Luhn check (simplified)
        total = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    def _mask_pan(self, pan: str) -> str:
        """Mask PAN for logging (show first 6, last 4)."""
        digits = re.sub(r'\D', '', pan)
        if len(digits) >= 10:
            return f"{digits[:6]}****{digits[-4:]}"
        return "****"

