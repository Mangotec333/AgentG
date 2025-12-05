"""
Compliance report generator (PDF).
Generates comprehensive compliance reports for incidents.
"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import backend_logger


class ComplianceReportGenerator:
    """Generates compliance reports in PDF format."""
    
    def __init__(self, output_dir: str = "reports/compliance"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        incident: Dict[str, Any],
        compliance_mapping: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        rca: Dict[str, Any]
    ) -> str:
        """
        Generate compliance report.
        
        Args:
            incident: Incident dictionary
            compliance_mapping: Compliance mapping results
            risk_analysis: Risk analysis results
            timeline: Event timeline
            rca: Root cause analysis
        
        Returns:
            Path to generated report
        """
        report_path = self.output_dir / f"compliance_report_{incident.get('id')}.txt"
        
        # In production, would use reportlab for PDF
        # For now, generate text report
        
        report_content = self._build_report_content(
            incident, compliance_mapping, risk_analysis, timeline, rca
        )
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        backend_logger.info(f"Generated compliance report: {report_path}")
        return str(report_path)
    
    def _build_report_content(
        self,
        incident: Dict[str, Any],
        compliance_mapping: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        rca: Dict[str, Any]
    ) -> str:
        """Build report content."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("COMPLIANCE INCIDENT REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Report Generated: {datetime.utcnow().isoformat()}")
        lines.append(f"Incident ID: {incident.get('id')}")
        lines.append(f"Severity: {incident.get('severity', 'unknown')}")
        lines.append(f"Created: {incident.get('created_at', 'unknown')}")
        lines.append("")
        
        # Executive Summary
        lines.append("-" * 80)
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 80)
        lines.append(rca.get("executive_summary", "No summary available"))
        lines.append("")
        
        # Compliance Violations
        lines.append("-" * 80)
        lines.append("COMPLIANCE VIOLATIONS DETECTED")
        lines.append("-" * 80)
        
        affected_standards = compliance_mapping.get("affected_standards", [])
        if affected_standards:
            lines.append(f"Affected Standards: {', '.join(affected_standards)}")
            lines.append(f"Total Violations: {compliance_mapping.get('violation_count', 0)}")
            lines.append("")
            
            # HIPAA
            if "HIPAA" in affected_standards:
                hipaa = compliance_mapping.get("hipaa", {})
                lines.append("HIPAA Violations:")
                for violation in hipaa.get("violations", [])[:5]:
                    lines.append(f"  - {violation.get('type')}: {violation.get('severity')}")
                lines.append("")
            
            # GLBA
            if "GLBA" in affected_standards:
                glba = compliance_mapping.get("glba", {})
                lines.append("GLBA Violations:")
                for violation in glba.get("violations", [])[:5]:
                    lines.append(f"  - {violation.get('type')}: {violation.get('severity')}")
                lines.append("")
            
            # PCI
            if "PCI-DSS" in affected_standards:
                pci = compliance_mapping.get("pci", {})
                lines.append("PCI-DSS Violations:")
                for violation in pci.get("violations", [])[:5]:
                    lines.append(f"  - {violation.get('type')}: {violation.get('severity')}")
                lines.append("")
            
            # SOC2
            if "SOC2" in affected_standards:
                soc2 = compliance_mapping.get("soc2", {})
                lines.append("SOC2 Violations:")
                for violation in soc2.get("violations", [])[:5]:
                    lines.append(f"  - {violation.get('type')} (Control: {violation.get('control')})")
                lines.append("")
            
            # NIST
            if "NIST" in affected_standards:
                nist = compliance_mapping.get("nist", {})
                lines.append("NIST Violations:")
                for violation in nist.get("violations", [])[:5]:
                    lines.append(f"  - {violation.get('type')} (Control: {violation.get('control')})")
                lines.append("")
            
            # EU AI Act
            if "EU-AI-Act" in affected_standards:
                ai_act = compliance_mapping.get("ai_act", {})
                lines.append("EU AI Act Classification:")
                lines.append(f"  Risk Category: {ai_act.get('risk_category', 'unknown')}")
                if ai_act.get("banned"):
                    lines.append("  STATUS: BANNED")
                lines.append(f"  Requirements: {', '.join(ai_act.get('requirements', []))}")
                lines.append("")
        else:
            lines.append("No compliance violations detected.")
            lines.append("")
        
        # Risk Analysis
        lines.append("-" * 80)
        lines.append("RISK ANALYSIS")
        lines.append("-" * 80)
        lines.append(f"Compliance Risk Score: {risk_analysis.get('compliance_risk', 0)}")
        lines.append(f"Risk Level: {risk_analysis.get('risk_level', 'unknown')}")
        lines.append("")
        
        # Root Cause Analysis
        lines.append("-" * 80)
        lines.append("ROOT CAUSE ANALYSIS")
        lines.append("-" * 80)
        lines.append(rca.get("root_cause_analysis", "No RCA available"))
        lines.append("")
        
        # Remediation Steps
        lines.append("-" * 80)
        lines.append("RECOMMENDED REMEDIATION STEPS")
        lines.append("-" * 80)
        remediation_steps = rca.get("remediation_steps", [])
        if remediation_steps:
            for i, step in enumerate(remediation_steps, 1):
                lines.append(f"{i}. {step}")
        else:
            lines.append("No remediation steps provided.")
        lines.append("")
        
        # Compliance Requirements
        lines.append("-" * 80)
        lines.append("COMPLIANCE REQUIREMENTS")
        lines.append("-" * 80)
        ai_act = compliance_mapping.get("ai_act", {})
        requirements = ai_act.get("requirements", [])
        if requirements:
            for req in requirements:
                lines.append(f"  - {req}")
        lines.append("")
        
        # Residual Risk
        lines.append("-" * 80)
        lines.append("RESIDUAL RISK ASSESSMENT")
        lines.append("-" * 80)
        lines.append(f"After remediation, residual risk score: {risk_analysis.get('compliance_risk', 0)}")
        lines.append(f"Risk level: {risk_analysis.get('risk_level', 'unknown')}")
        lines.append("")
        
        # Evidence Appendix
        lines.append("-" * 80)
        lines.append("EVIDENCE APPENDIX")
        lines.append("-" * 80)
        lines.append(f"Evidence collected: {len(timeline)} events")
        lines.append(f"Evidence location: evidence/{incident.get('id')}/")
        lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)

