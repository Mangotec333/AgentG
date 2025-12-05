"""
GLBA (Gramm-Leach-Bliley Act) compliance detector.
Detects NPI (Nonpublic Personal Information) exposure and violations.
"""
import re
from typing import Dict, Any, List


class GLBADetector:
    """Detects GLBA violations and NPI exposure."""
    
    # NPI patterns
    NPI_PATTERNS = {
        "account_number": r'\b(account|acct)[\s#:]*[\d-]{8,}\b',
        "routing_number": r'\b(routing|ABA)[\s#:]*\d{9}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "tax_id": r'\b(EIN|TIN|tax\s+id)[\s#:]*[\d-]{9,}\b',
        "financial_account": r'\b(checking|savings|investment|brokerage)\s+account\b',
        "loan_number": r'\b(loan|mortgage)[\s#:]*[\d-]{6,}\b',
        "policy_number": r'\b(policy|policy\s+number)[\s#:]*[\dA-Z-]{6,}\b',
    }
    
    # Financial institution identifiers
    FINANCIAL_TERMS = [
        "bank", "credit union", "lender", "broker", "advisor",
        "investment", "portfolio", "securities", "trading",
        "mortgage", "loan", "credit", "debit", "transaction"
    ]
    
    def detect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect GLBA violations in an event.
        
        Args:
            event: Event dictionary
        
        Returns:
            Detection results with flags and risk score
        """
        flags = []
        risk_score = 0
        raw = event.get("raw", "").lower()
        payload = event.get("payload", {})
        
        # Check for NPI patterns
        for npi_type, pattern in self.NPI_PATTERNS.items():
            if re.search(pattern, raw, re.IGNORECASE):
                flags.append({
                    "type": "npi_detected",
                    "npi_category": npi_type,
                    "pattern": pattern,
                    "severity": "high"
                })
                risk_score += 5
        
        # Check payload for NPI
        payload_str = str(payload).lower()
        for npi_type, pattern in self.NPI_PATTERNS.items():
            if re.search(pattern, payload_str, re.IGNORECASE):
                flags.append({
                    "type": "npi_in_payload",
                    "npi_category": npi_type,
                    "severity": "high"
                })
                risk_score += 5
        
        # Check for financial context
        financial_term_count = sum(1 for term in self.FINANCIAL_TERMS if term in raw)
        if financial_term_count >= 2 and any(npi in raw for npi in ["account", "number", "routing"]):
            flags.append({
                "type": "financial_context_with_npi",
                "term_count": financial_term_count,
                "severity": "medium"
            })
            risk_score += 3
        
        # Check for unauthorized third-party API calls
        if event.get("event_type") == "api_access":
            endpoint = payload.get("endpoint", "")
            # Flag calls to enrichment/data providers without proper controls
            if any(provider in endpoint for provider in ["enrichment", "data-provider", "lookup"]):
                if any(npi in raw for npi in ["account", "ssn", "tax"]):
                    flags.append({
                        "type": "unauthorized_third_party_npi",
                        "severity": "critical"
                    })
                    risk_score += 10
        
        # Check LLM output for NPI leakage
        if event.get("event_type") == "llm_completion":
            response = payload.get("response", "")
            for npi_type, pattern in self.NPI_PATTERNS.items():
                if re.search(pattern, response, re.IGNORECASE):
                    flags.append({
                        "type": "npi_in_llm_output",
                        "npi_category": npi_type,
                        "severity": "critical"
                    })
                    risk_score += 10
        
        return {
            "violations": flags,
            "risk_score": min(risk_score, 20),
            "compliance_standard": "GLBA",
            "has_violation": len(flags) > 0
        }

