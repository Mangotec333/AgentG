# Compliance Engine Module - Complete Specification

## 🔒 Overview

The Compliance Engine is a fully integrated module that detects, classifies, scores, and generates evidence for compliance violations across multiple regulatory standards:

- **HIPAA** (Health Insurance Portability and Accountability Act)
- **GLBA** (Gramm-Leach-Bliley Act)
- **PCI-DSS** (Payment Card Industry Data Security Standard)
- **SOC2** (System and Organization Controls 2)
- **NIST 800-53 / NIST AI RMF** (Government & AI Governance)
- **EU AI Act** (European Union AI Regulation)

## 🏗️ Architecture

```
Event Stream → Compliance Mapper → Detectors → Risk Scorer → Evidence Collector
                                                                    ↓
                                                            Compliance Reports
```

## 📁 Module Structure

```
/backend/compliance_engine/
├── hipaa_detector.py          # HIPAA compliance detection
├── glba_detector.py            # GLBA compliance detection
├── pci_detector.py             # PCI-DSS compliance detection
├── soc2_detector.py            # SOC2 compliance detection
├── nist_detector.py            # NIST 800-53 / AI RMF detection
├── ai_act_classifier.py        # EU AI Act classification
├── compliance_mapper.py         # Unified compliance mapping
├── compliance_risk.py          # Compliance risk scoring
├── evidence_collector.py       # Evidence collection for audits
├── compliance_report.py        # Compliance report generation
├── entropy_analyzer.py         # Entropy analysis utilities
└── router.py                   # API endpoints
```

## 🔍 Detector Details

### HIPAA Detector

**Detects:**
- PHI (Protected Health Information) patterns:
  - SSN, Medical Record Numbers (MRN)
  - Patient names, dates of birth
  - ICD-10/ICD-9 diagnosis codes
  - Medical conditions, prescriptions
  - Hospital/clinic identifiers
- Unencrypted PHI transfers
- PHI in LLM outputs
- Unauthorized agent access to PHI-tagged workflows

**Risk Scoring:**
- PHI detected: +5 per occurrence
- Unencrypted transfer: +10
- PHI in LLM output: +10

### GLBA Detector

**Detects:**
- NPI (Nonpublic Personal Information):
  - Account numbers, routing numbers
  - Credit card numbers
  - Tax IDs (EIN/TIN)
  - Loan numbers, policy numbers
- Unauthorized third-party API calls
- NPI in LLM outputs

**Risk Scoring:**
- NPI detected: +5 per occurrence
- Unauthorized third-party: +10
- NPI in LLM output: +10

### PCI Detector

**Detects:**
- PAN (Primary Account Number) - 13-19 digits
- CVV/CVC/CID/CVV2
- Expiration dates
- Track data (magnetic stripe)
- Cardholder data in logs
- Unencrypted storage

**Features:**
- Luhn algorithm validation for PAN
- Card brand detection (Visa, Mastercard, Amex, Discover)
- PAN masking for logging

**Risk Scoring:**
- PAN detected: +10
- CVV detected: +10
- Track data: +10
- Expiry date: +5

### SOC2 Detector

**Monitors Controls:**
- **CC6.1**: Unauthorized tool activation
- **CC6.2**: Configuration changes without audit
- **CC7.1**: Missing event logging
- **CC7.2**: Log integrity violations
- **CC6.6**: Availability failures
- **CC7.3**: Processing integrity issues
- **CC6.7**: Confidentiality violations

**Risk Scoring:**
- Unauthorized tool: +8
- Config change without audit: +7
- Log integrity violation: +10
- Availability failure: +6
- Confidentiality violation: +7

### NIST Detector

**Monitors Controls:**
- **AC-3**: Access control violations
- **AU-2**: Missing audit trails
- **AI-RMF-EXPLAIN**: Lack of explainability
- **AI-RMF-ACCOUNT**: Accountability gaps
- **AI-RMF-OVERSIGHT**: Human oversight gaps
- **AI-RMF-SAFETY**: Safety threshold violations
- **SI-3**: Malicious code protection
- **SC-7**: Boundary protection

**Risk Scoring:**
- Unauthorized access: +7
- Missing audit trail: +4
- Human oversight gap: +8
- Safety threshold exceeded: +6
- Malicious code: +10
- Boundary violation: +7

### EU AI Act Classifier

**Risk Categories:**
- **Minimal-risk**: No specific requirements
- **Limited-risk**: Transparency obligations, user notification
- **High-risk**: Risk management, data governance, technical documentation, human oversight
- **Unacceptable-risk**: BANNED - Cannot be deployed

**Classification Factors:**
- Use case (biometric, critical infrastructure, etc.)
- Data type (biometric, health, financial, personal)
- Autonomous decision-making
- Human oversight presence
- Transparency notices

## 🗺️ Compliance Mapping

The `ComplianceMapper` maps every event to all standards:

```json
{
  "event_id": "123",
  "hipaa": {
    "violations": [...],
    "risk_score": 5,
    "has_violation": true
  },
  "glba": {...},
  "pci": {...},
  "soc2": {...},
  "nist": {...},
  "ai_act": {
    "risk_category": "high-risk",
    "banned": false,
    "requirements": [...]
  }
}
```

## ⚠️ Compliance Risk Scoring

**Formula:**
```
compliance_risk = 
    hipaa_score +
    glba_score +
    pci_score +
    soc2_score +
    nist_score +
    ai_act_risk_value
```

**Thresholds:**
- **0-4**: Minimal
- **5-10**: Warning
- **11-20**: Violations
- **21+**: Major Incident

## 📝 Evidence Collection

The `EvidenceCollector` gathers comprehensive evidence for audits:

**Collected Data:**
- Trigger event
- Related events (timeline)
- Compliance mapping
- Risk analysis
- Agent traces
- LLM inputs/outputs
- Tool calls
- API chains
- Raw payloads (sanitized)

**Storage:**
- `/evidence/{incident_id}/`
- JSON format for easy audit review
- Manifest file for evidence catalog

## 📊 Compliance Reports

**Generated Reports Include:**
- Executive summary
- Violations detected by standard
- Affected compliance standards
- Risk analysis
- Root cause analysis
- Recommended remediation steps
- Compliance requirements
- Residual risk assessment
- Evidence appendix

**Formats:**
- Text report (current)
- PDF report (production - reportlab)

## 🔗 Integration Points

### Threat Engine Integration

Compliance risk is integrated into unified risk scoring:

```python
total_risk = (
    rules_risk * 0.3 +
    pattern_risk * 0.25 +
    model_risk * 0.25 +
    compliance_risk_normalized * 0.2
)
```

### Incident System Integration

- Compliance mapping attached to incidents
- Evidence automatically collected
- Compliance reports generated
- RCA includes compliance context

### Patterns Library Extension

Compliance patterns stored in:
- `patterns/compliance/hipaa_signatures.json`
- `patterns/compliance/glba_signatures.json`
- `patterns/compliance/pci_signatures.json`
- `patterns/compliance/soc2_signatures.json`
- `patterns/compliance/nist_signatures.json`

## 🌐 API Endpoints

### GET `/api/v1/compliance/summary`
Get compliance summary for workspace

### GET `/api/v1/compliance/events`
Get events with compliance violations

### GET `/api/v1/compliance/incidents`
Get incidents with compliance violations

### GET `/api/v1/compliance/report/{incident_id}`
Get compliance report for incident

## 🗄️ Database Schema

**New Tables:**
- `compliance_mappings`: Compliance flags per event
- `compliance_evidence`: Links incidents to evidence

## 🔄 Compliance Flywheel

**Self-Improving System:**
1. More violations detected → more signatures added
2. More signatures → better detection
3. Better detection → more enterprise clients
4. More clients → more incident data
5. More data → better mapping

**This creates a regulatory moat that grows with every customer.**

## 📈 Use Cases

### Healthcare (HIPAA)
- Detect PHI exposure in LLM outputs
- Monitor unauthorized access to medical data
- Generate HIPAA breach reports

### Financial Services (GLBA, PCI)
- Detect NPI exposure
- Monitor cardholder data handling
- Generate PCI SAQ evidence

### Enterprise (SOC2)
- Monitor control violations
- Track audit events
- Generate SOC2 Type II evidence

### Government (NIST)
- Monitor AI governance compliance
- Track explainability and accountability
- Generate NIST AI RMF reports

### EU Operations (AI Act)
- Classify AI workflows by risk
- Ensure compliance with requirements
- Generate AI Act compliance reports

## 🎯 Key Features

1. **Multi-Standard Detection**: Single event analyzed against all standards
2. **Automated Evidence Collection**: Complete audit trail
3. **Risk-Based Prioritization**: Focus on high-risk violations
4. **Regulatory Reporting**: Ready-to-submit compliance reports
5. **Self-Improving**: Pattern library grows with incidents

## 🚀 Production Checklist

- [ ] Configure compliance thresholds
- [ ] Set up evidence storage (encrypted)
- [ ] Configure audit retention policies
- [ ] Set up compliance report templates
- [ ] Configure notification rules
- [ ] Test with synthetic compliance violations
- [ ] Validate against real regulatory requirements

---

**This is the compliance moat. This is defensible regulatory IP.**

