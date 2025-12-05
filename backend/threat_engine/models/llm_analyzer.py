"""
LLM-based anomaly detection using multiple models.
"""
import os
from typing import Dict, Any, Optional
import sys
import json
import re
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.logger import threat_logger
from shared.config import BackendConfig

# Try importing LLM libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    threat_logger.warning("google-generativeai not installed. Gemini analysis will be disabled.")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    threat_logger.warning("openai not installed. OpenAI analysis will be disabled.")


class LLMAnalyzer:
    """Uses LLMs to analyze events for semantic threats."""
    
    def __init__(self):
        self.config = BackendConfig()
        self.gemini_api_key = self.config.gemini_api_key
        self.openai_api_key = self.config.openai_api_key
    
    async def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an event using LLM models.
        
        Args:
            event: Event dictionary
        
        Returns:
            Analysis results with risk scores
        """
        results = {
            "gemini_risk": 0,
            "openai_risk": 0,
            "consensus_risk": 0,
            "reasoning": {}
        }
        
        # Try Gemini first
        if self.gemini_api_key:
            try:
                gemini_result = await self._analyze_with_gemini(event)
                results["gemini_risk"] = gemini_result.get("risk", 0)
                results["reasoning"]["gemini"] = gemini_result.get("reasoning", "")
            except Exception as e:
                threat_logger.error(f"Gemini analysis error: {e}")
        
        # Try OpenAI
        if self.openai_api_key:
            try:
                openai_result = await self._analyze_with_openai(event)
                results["openai_risk"] = openai_result.get("risk", 0)
                results["reasoning"]["openai"] = openai_result.get("reasoning", "")
            except Exception as e:
                threat_logger.error(f"OpenAI analysis error: {e}")
        
        # Calculate consensus risk (average)
        risks = [r for r in [results["gemini_risk"], results["openai_risk"]] if r > 0]
        if risks:
            results["consensus_risk"] = int(sum(risks) / len(risks))
        else:
            results["consensus_risk"] = 0
        
        return results
    
    async def _analyze_with_gemini(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze event using Gemini."""
        if not GEMINI_AVAILABLE:
            threat_logger.warning("Gemini library not available")
            return {"risk": 0, "reasoning": "Gemini library not installed"}
        
        if not self.gemini_api_key:
            threat_logger.warning("Gemini API key not configured")
            return {"risk": 0, "reasoning": "Gemini API key not set"}
        
        try:
            prompt = self._build_analysis_prompt(event)
            
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            
            # Use Gemini 2.0 Flash (or fallback to available model)
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception:
                # Fallback to stable model
                model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate content
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                }
            )
            
            # Parse response
            text = response.text if hasattr(response, 'text') else str(response)
            risk, reasoning = self._parse_llm_response(text)
            
            threat_logger.debug(f"Gemini analysis: risk={risk}")
            return {"risk": risk, "reasoning": reasoning}
            
        except Exception as e:
            threat_logger.error(f"Gemini analysis error: {e}")
            return {"risk": 0, "reasoning": f"Error: {str(e)}"}
    
    async def _analyze_with_openai(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze event using OpenAI."""
        if not OPENAI_AVAILABLE:
            threat_logger.warning("OpenAI library not available")
            return {"risk": 0, "reasoning": "OpenAI library not installed"}
        
        if not self.openai_api_key:
            threat_logger.warning("OpenAI API key not configured")
            return {"risk": 0, "reasoning": "OpenAI API key not set"}
        
        try:
            prompt = self._build_analysis_prompt(event)
            
            # Create OpenAI client
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Call API
            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {"role": "system", "content": "You are a security analyst analyzing AI agent events for threats."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            text = response.choices[0].message.content
            risk, reasoning = self._parse_llm_response(text)
            
            threat_logger.debug(f"OpenAI analysis: risk={risk}")
            return {"risk": risk, "reasoning": reasoning}
            
        except Exception as e:
            threat_logger.error(f"OpenAI analysis error: {e}")
            return {"risk": 0, "reasoning": f"Error: {str(e)}"}
    
    def _build_analysis_prompt(self, event: Dict[str, Any]) -> str:
        """Build analysis prompt for LLM."""
        return f"""
Analyze this AI agent event for security threats and rate the risk from 0-10.

Event Type: {event.get('event_type')}
Raw Event: {event.get('raw', '')[:500]}
Payload: {str(event.get('payload', {}))[:500]}

Consider:
- Prompt injection attempts
- Jailbreaking attempts
- Tool abuse
- Unauthorized access
- Data exfiltration
- Output drift

Respond with:
1. Risk score (0-10)
2. Brief reasoning

Format: RISK: <score> | REASONING: <explanation>
"""
    
    def _parse_llm_response(self, text: str) -> tuple[int, str]:
        """
        Parse LLM response to extract risk score and reasoning.
        
        Returns:
            Tuple of (risk_score, reasoning)
        """
        risk = 0
        reasoning = text
        
        # Try to extract risk score from various formats
        # Format 1: "RISK: 7 | REASONING: ..."
        match = re.search(r'RISK[:\s]+(\d+)', text, re.IGNORECASE)
        if match:
            risk = int(match.group(1))
            # Extract reasoning if present
            reason_match = re.search(r'REASONING[:\s]+(.+)', text, re.IGNORECASE)
            if reason_match:
                reasoning = reason_match.group(1).strip()
        else:
            # Format 2: "Risk score: 7"
            match = re.search(r'risk\s+score[:\s]+(\d+)', text, re.IGNORECASE)
            if match:
                risk = int(match.group(1))
            else:
                # Format 3: Just a number at the start
                match = re.search(r'^(\d+)', text.strip())
                if match:
                    risk = int(match.group(1))
        
        # Clamp risk to 0-10
        risk = max(0, min(10, risk))
        
        # If no reasoning extracted, use full text (truncated)
        if reasoning == text and len(reasoning) > 200:
            reasoning = reasoning[:200] + "..."
        
        return risk, reasoning

