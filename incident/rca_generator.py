"""
RCA (Root Cause Analysis) generator using LLM.
"""
from typing import Dict, Any, List
import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import backend_logger
from shared.config import BackendConfig

# Try importing LLM libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    backend_logger.warning("google-generativeai not installed. RCA generation will use fallback.")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    backend_logger.warning("openai not installed. RCA generation will use fallback.")


class RCAGenerator:
    """Generates Root Cause Analysis reports using LLM."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.gemini_api_key = self.config.gemini_api_key
        self.openai_api_key = self.config.openai_api_key
    
    async def generate_rca(
        self,
        incident: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate RCA report.
        
        Args:
            incident: Incident dictionary
            timeline: Event timeline
            risk_analysis: Risk analysis results
        
        Returns:
            RCA report dictionary
        """
        # Build prompt for LLM
        prompt = self._build_rca_prompt(incident, timeline, risk_analysis)
        
        # Generate RCA using LLM (placeholder)
        # In production, would call LLM API
        rca = await self._generate_with_llm(prompt)
        
        return {
            "executive_summary": rca.get("executive_summary", ""),
            "timeline": timeline,
            "root_cause_analysis": rca.get("root_cause", ""),
            "recommended_fix": rca.get("recommended_fix", ""),
            "remediation_steps": rca.get("remediation_steps", []),
            "compliance_notes": rca.get("compliance_notes", "")
        }
    
    def _build_rca_prompt(
        self,
        incident: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        risk_analysis: Dict[str, Any]
    ) -> str:
        """Build prompt for RCA generation."""
        return f"""
Generate a comprehensive Root Cause Analysis (RCA) report for this security incident.

INCIDENT DETAILS:
- ID: {incident.get('id')}
- Severity: {incident.get('severity')}
- Title: {incident.get('title')}
- Trigger Event: {incident.get('trigger_event_id')}

RISK ANALYSIS:
- Total Risk Score: {risk_analysis.get('total_risk', 0)}/10
- Rules Risk: {risk_analysis.get('rules_risk', 0)}
- Pattern Risk: {risk_analysis.get('pattern_risk', 0)}
- Model Risk: {risk_analysis.get('model_risk', 0)}
- Pattern Matches: {len(risk_analysis.get('pattern_matches', []))}

TIMELINE:
{self._format_timeline(timeline)}

Please provide:
1. Executive Summary (2-3 sentences)
2. Root Cause Analysis (detailed explanation)
3. Recommended Fix (specific actions)
4. Remediation Steps (numbered list)
5. Compliance Notes (if applicable)

Format as JSON with keys: executive_summary, root_cause, recommended_fix, remediation_steps, compliance_notes
"""
    
    def _format_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        """Format timeline for prompt."""
        formatted = []
        for event in timeline[:20]:  # Limit to 20 events
            formatted.append(
                f"- {event.get('timestamp')}: {event.get('event_type')} "
                f"(risk={event.get('risk_score', 0)}) - {event.get('summary', '')}"
            )
        return "\n".join(formatted)
    
    async def _generate_with_llm(self, prompt: str) -> Dict[str, Any]:
        """Generate RCA using LLM."""
        # Try OpenAI first (better for structured output)
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                return await self._generate_with_openai(prompt)
            except Exception as e:
                backend_logger.warning(f"OpenAI RCA generation failed: {e}, trying Gemini...")
        
        # Fallback to Gemini
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                return await self._generate_with_gemini(prompt)
            except Exception as e:
                backend_logger.warning(f"Gemini RCA generation failed: {e}, using fallback...")
        
        # Fallback template if no LLM available
        backend_logger.warning("No LLM available for RCA generation, using template")
        return {
            "executive_summary": "Security incident detected with high risk score. Requires immediate investigation.",
            "root_cause": "Analysis pending LLM integration. Please review incident details manually.",
            "recommended_fix": "Review incident details and implement recommended remediation steps.",
            "remediation_steps": [
                "Review trigger event details",
                "Analyze pattern matches",
                "Implement security controls",
                "Monitor for similar incidents"
            ],
            "compliance_notes": "Incident logged for compliance reporting."
        }
    
    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate RCA using OpenAI."""
        client = AsyncOpenAI(api_key=self.openai_api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a security analyst generating Root Cause Analysis reports. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        text = response.choices[0].message.content
        return self._parse_rca_response(text)
    
    async def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate RCA using Gemini."""
        import asyncio
        
        genai.configure(api_key=self.gemini_api_key)
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Python 3.8 compatible async call
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            response = await loop.run_in_executor(
                executor,
                lambda: model.generate_content(
                    prompt + "\n\nRespond with valid JSON only.",
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 1500,
                    }
                )
            )
        
        text = response.text if hasattr(response, 'text') else str(response)
        return self._parse_rca_response(text)
    
    def _parse_rca_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response into RCA structure."""
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                # Ensure all required fields exist
                return {
                    "executive_summary": parsed.get("executive_summary", ""),
                    "root_cause": parsed.get("root_cause", parsed.get("root_cause_analysis", "")),
                    "recommended_fix": parsed.get("recommended_fix", ""),
                    "remediation_steps": parsed.get("remediation_steps", []),
                    "compliance_notes": parsed.get("compliance_notes", "")
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: parse unstructured text
        return {
            "executive_summary": text[:200] + "..." if len(text) > 200 else text,
            "root_cause": "See full analysis above.",
            "recommended_fix": "Review the incident details and implement appropriate security controls.",
            "remediation_steps": [
                "Review trigger event details",
                "Analyze pattern matches",
                "Implement security controls",
                "Monitor for similar incidents"
            ],
            "compliance_notes": "Incident logged for compliance reporting."
        }

