#!/usr/bin/env python3
"""
Test PDF report generation for AgentG.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from incident.pdf_report import PDFReportGenerator
from incident.rca_generator import RCAGenerator


async def test_pdf_generation():
    """Test PDF report generation."""
    print("🧪 Testing PDF Report Generation...")
    print("=" * 50)
    
    # Create test incident
    test_incident = {
        "id": "test-incident-001",
        "severity": "high",
        "status": "open",
        "title": "Test Prompt Injection Attempt",
        "trigger_event_id": "test-event-001",
        "created_at": datetime.now().isoformat()
    }
    
    # Create test timeline
    test_timeline = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "event_id": "test-event-001",
            "event_type": "llm_completion",
            "risk_score": 8,
            "summary": "Prompt injection attempt detected"
        },
        {
            "timestamp": "2024-01-01T00:00:05Z",
            "event_id": "test-event-002",
            "event_type": "tool_call",
            "risk_score": 6,
            "summary": "Suspicious tool call detected"
        }
    ]
    
    # Create test risk analysis
    test_risk_analysis = {
        "total_risk": 8,
        "rules_risk": 7,
        "pattern_risk": 8,
        "model_risk": 8,
        "pattern_matches": ["PI-001"]
    }
    
    # Generate RCA
    print("📝 Generating RCA...")
    rca_generator = RCAGenerator()
    rca = await rca_generator.generate_rca(
        test_incident,
        test_timeline,
        test_risk_analysis
    )
    print("✅ RCA generated")
    print()
    
    # Generate PDF
    print("📄 Generating PDF report...")
    pdf_generator = PDFReportGenerator(output_dir="test_reports")
    pdf_path = pdf_generator.generate_pdf(
        test_incident,
        rca,
        test_timeline
    )
    
    print(f"✅ PDF generated: {pdf_path}")
    
    # Check if file exists
    pdf_file = Path(pdf_path)
    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        print(f"   File size: {size_kb:.2f} KB")
        print(f"   Full path: {pdf_file.absolute()}")
        return True
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        return False


if __name__ == "__main__":
    print("🚀 Testing PDF Generation for AgentG\n")
    
    try:
        success = asyncio.run(test_pdf_generation())
        if success:
            print("\n✅ PDF generation test passed!")
            sys.exit(0)
        else:
            print("\n❌ PDF generation test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

