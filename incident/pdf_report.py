"""
PDF report generator for incidents.
"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import backend_logger

# Try importing reportlab
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    backend_logger.warning("reportlab not installed. PDF generation will create text files.")


class PDFReportGenerator:
    """Generates PDF reports for incidents."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_pdf(
        self,
        incident: Dict[str, Any],
        rca: Dict[str, Any],
        timeline: List[Dict[str, Any]] = None
    ) -> str:
        """
        Generate PDF report.
        
        Args:
            incident: Incident dictionary
            rca: RCA report dictionary
            timeline: Event timeline
        
        Returns:
            Path to generated PDF
        """
        if timeline is None:
            timeline = []
        
        pdf_path = self.output_dir / f"incident_{incident.get('id')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            return self._generate_pdf_with_reportlab(pdf_path, incident, rca, timeline)
        else:
            # Fallback to text file
            return self._generate_text_fallback(pdf_path, incident, rca, timeline)
    
    def _generate_pdf_with_reportlab(
        self,
        pdf_path: Path,
        incident: Dict[str, Any],
        rca: Dict[str, Any],
        timeline: List[Dict[str, Any]]
    ) -> str:
        """Generate PDF using reportlab."""
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("INCIDENT REPORT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Incident Details
        details_style = ParagraphStyle(
            'Details',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )
        
        incident_id = incident.get('id', 'N/A')
        severity = incident.get('severity', 'unknown').upper()
        created_at = incident.get('created_at', 'N/A')
        
        details_data = [
            ['Incident ID:', incident_id],
            ['Severity:', severity],
            ['Created:', created_at],
            ['Status:', incident.get('status', 'N/A').upper()]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        story.append(Paragraph(rca.get('executive_summary', 'No summary available.'), details_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Root Cause Analysis
        story.append(Paragraph("ROOT CAUSE ANALYSIS", heading_style))
        root_cause = rca.get('root_cause_analysis', rca.get('root_cause', 'Analysis not available.'))
        story.append(Paragraph(root_cause, details_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Recommended Fix
        story.append(Paragraph("RECOMMENDED FIX", heading_style))
        story.append(Paragraph(rca.get('recommended_fix', 'No recommendation available.'), details_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Remediation Steps
        story.append(Paragraph("REMEDIATION STEPS", heading_style))
        steps = rca.get('remediation_steps', [])
        if steps:
            for i, step in enumerate(steps, 1):
                story.append(Paragraph(f"{i}. {step}", details_style))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No remediation steps provided.", details_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Compliance Notes
        compliance_notes = rca.get('compliance_notes', '')
        if compliance_notes:
            story.append(Paragraph("COMPLIANCE NOTES", heading_style))
            story.append(Paragraph(compliance_notes, details_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Timeline (if provided)
        if timeline:
            story.append(PageBreak())
            story.append(Paragraph("EVENT TIMELINE", heading_style))
            
            timeline_data = [['Timestamp', 'Event Type', 'Risk Score', 'Summary']]
            for event in timeline[:50]:  # Limit to 50 events
                timeline_data.append([
                    event.get('timestamp', 'N/A')[:19],
                    event.get('event_type', 'N/A'),
                    str(event.get('risk_score', 0)),
                    (event.get('summary', '') or '')[:50]
                ])
            
            timeline_table = Table(timeline_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 3*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(timeline_table)
        
        # Build PDF
        doc.build(story)
        backend_logger.info(f"PDF generated: {pdf_path}")
        return str(pdf_path)
    
    def _generate_text_fallback(
        self,
        pdf_path: Path,
        incident: Dict[str, Any],
        rca: Dict[str, Any],
        timeline: List[Dict[str, Any]]
    ) -> str:
        """Generate text file as fallback."""
        txt_path = pdf_path.with_suffix('.txt')
        
        with open(txt_path, 'w') as f:
            f.write(f"INCIDENT REPORT\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"Incident ID: {incident.get('id')}\n")
            f.write(f"Severity: {incident.get('severity')}\n")
            f.write(f"Created: {incident.get('created_at')}\n\n")
            f.write(f"EXECUTIVE SUMMARY\n")
            f.write(f"{'-'*50}\n")
            f.write(f"{rca.get('executive_summary', '')}\n\n")
            f.write(f"ROOT CAUSE ANALYSIS\n")
            f.write(f"{'-'*50}\n")
            f.write(f"{rca.get('root_cause_analysis', rca.get('root_cause', ''))}\n\n")
            f.write(f"REMEDIATION STEPS\n")
            f.write(f"{'-'*50}\n")
            for i, step in enumerate(rca.get('remediation_steps', []), 1):
                f.write(f"{i}. {step}\n")
        
        backend_logger.warning(f"reportlab not available, created text file: {txt_path}")
        return str(txt_path)

