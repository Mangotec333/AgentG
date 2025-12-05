"""
HIPAA (Health Insurance Portability and Accountability Act) compliance detector.
Detects PHI (Protected Health Information) exposure and violations.
"""
import re
from typing import Dict, Any, List


class HIPAADetector:
    """Detects HIPAA violations and PHI exposure."""
    
    # PHI patterns
    PHI_PATTERNS = {
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "medical_record_number": r'\bMRN[:\s]*[\dA-Z]{6,}\b',
        "patient_name": r'\b(patient|subject)[:\s]+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        "date_of_birth": r'\b(DOB|birth\s+date)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        "diagnosis_code": r'\b(ICD-?10|ICD-?9)[:\s]*[A-Z0-9.]+\b',
        "medical_condition": r'\b(diagnosis|condition|disease|syndrome|disorder)\b',
        "prescription": r'\b(prescription|medication|drug|Rx)[:\s]*[A-Za-z0-9]+\b',
        "hospital_name": r'\b(hospital|clinic|medical\s+center|health\s+system)\b',
    }
    
    # High-risk medical terms
    MEDICAL_TERMS = [
        "cancer", "tumor", "malignant", "benign", "chemotherapy",
        "surgery", "procedure", "treatment", "therapy", "diagnosis",
        "prognosis", "symptom", "disease", "disorder", "syndrome"
    ]
    
    def detect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect HIPAA violations in an event.
        
        Args:
            event: Event dictionary
        
        Returns:
            Detection results with flags and risk score
        """
        flags = []
        risk_score = 0
        raw = event.get("raw", "").lower()
        payload = event.get("payload", {})
        
        # Check for PHI patterns
        for phi_type, pattern in self.PHI_PATTERNS.items():
            if re.search(pattern, raw, re.IGNORECASE):
                flags.append({
                    "type": "phi_detected",
                    "phi_category": phi_type,
                    "pattern": pattern,
                    "severity": "high"
                })
                risk_score += 5
        
        # Check payload for PHI
        payload_str = str(payload).lower()
        for phi_type, pattern in self.PHI_PATTERNS.items():
            if re.search(pattern, payload_str, re.IGNORECASE):
                flags.append({
                    "type": "phi_in_payload",
                    "phi_category": phi_type,
                    "severity": "high"
                })
                risk_score += 5
        
        # Check for medical terms (context-dependent)
        medical_term_count = sum(1 for term in self.MEDICAL_TERMS if term in raw)
        if medical_term_count >= 3:
            flags.append({
                "type": "medical_context",
                "term_count": medical_term_count,
                "severity": "medium"
            })
            risk_score += 2
        
        # Check for unencrypted PHI transfer
        if event.get("event_type") == "api_access":
            endpoint = payload.get("endpoint", "")
            if "http://" in endpoint and any(phi in raw for phi in ["ssn", "mrn", "patient"]):
                flags.append({
                    "type": "unencrypted_phi_transfer",
                    "severity": "critical"
                })
                risk_score += 10
        
        # Check LLM output for PHI leakage
        if event.get("event_type") == "llm_completion":
            response = payload.get("response", "")
            for phi_type, pattern in self.PHI_PATTERNS.items():
                if re.search(pattern, response, re.IGNORECASE):
                    flags.append({
                        "type": "phi_in_llm_output",
                        "phi_category": phi_type,
                        "severity": "critical"
                    })
                    risk_score += 10
        
        return {
            "violations": flags,
            "risk_score": min(risk_score, 20),
            "compliance_standard": "HIPAA",
            "has_violation": len(flags) > 0
        }

