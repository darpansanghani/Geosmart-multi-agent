import os
import json
import re
import google.generativeai as genai
from typing import Dict, Any, List
from .context import AgentContext

class ClassificationAgent:
    """ClassificationAgent - Determines category, severity, and impact"""
    def __init__(self):
        self.name = 'ClassificationAgent'
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.use_fallback = True
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_fallback = False

    async def execute(self, context: AgentContext) -> Dict[str, Any]:
        issue_type = context.get('issue_type')
        urgency_indicators = context.get('urgency_indicators') or []
        nearby_facilities = context.get('nearby_facilities') or []
        original_text = context.get('original_text')
        
        if self.use_fallback:
            return await self._fallback_execution(context, issue_type, urgency_indicators, nearby_facilities)
            
        try:
            prompt = f"""You are a Classification Agent in a multi-agent civic complaint system.

Task: Classify this civic complaint based on context from OTHER agents.

Context from other agents:
- Issue type: {issue_type}
- Urgency indicators: {", ".join(urgency_indicators) if urgency_indicators else 'None'}
- Nearby facilities: {", ".join(nearby_facilities) if nearby_facilities else 'None'}
- Original complaint: "{original_text}"

Classification guidelines:

CATEGORIES (choose one):
- Sanitation (garbage, waste management)
- Roads (potholes, road damage)
- Streetlights (broken lights, electrical)
- Water Supply (leaks, supply issues)
- Drainage (sewage, overflow)
- Other

SEVERITY (choose one):
- High: Health hazards, safety risks, near sensitive areas (hospitals, schools), prolonged duration
- Medium: Moderate inconvenience, localized issues, routine urgency
- Low: Minor issues, cosmetic problems, routine maintenance

IMPACT SCOPE (choose one):
- Individual (single house/building)
- Street (one street affected)
- Neighborhood (multiple streets)
- Ward (entire ward affected)

Respond ONLY with valid JSON:
{{
  "category": "category name",
  "severity": "Low|Medium|High",
  "impact_scope": "Individual|Street|Neighborhood|Ward",
  "reasoning": "brief explanation of your classification decision"
}}"""

            response = await self.model.generate_content_async(prompt)
            parsed = self._parse_json(response.text)
            
            await context.update(self.name, {
                "category": parsed.get("category"),
                "severity": parsed.get("severity"),
                "impact_scope": parsed.get("impact_scope"),
                "classification_reasoning": parsed.get("reasoning")
            })
            
            return {
                "summary": f"Category: {parsed.get('category')}, Severity: {parsed.get('severity')}, Impact: {parsed.get('impact_scope')}"
            }
            
        except Exception:
            return await self._fallback_execution(context, issue_type, urgency_indicators, nearby_facilities)

    async def _fallback_execution(self, context, issue_type, urgency_indicators, nearby_facilities):
        original_text = (context.get('original_text') or '').lower()
        issue_type_lower = (issue_type or '').lower()
        
        category = 'Other'
        if 'garbage' in issue_type_lower or 'waste' in issue_type_lower: category = 'Sanitation'
        elif 'pothole' in issue_type_lower or 'road' in issue_type_lower: category = 'Roads'
        elif 'light' in issue_type_lower: category = 'Streetlights'
        elif 'water' in issue_type_lower: category = 'Water Supply'
        elif 'drain' in issue_type_lower: category = 'Drainage'
        elif 'accident' in issue_type_lower or 'fire' in issue_type_lower: category = 'Emergency'
        
        if category in ['Sanitation', 'Water Supply', 'Drainage', 'Roads', 'Streetlights']:
            severity = 'Medium'
            
        if nearby_facilities or urgency_indicators or category == 'Emergency': severity = 'High'
        
        await context.update(self.name, {
            "category": category,
            "severity": severity,
            "impact_scope": "Street",
            "classification_reasoning": "Fallback Logic"
        })
        return {"summary": f"Category: {category}, Severity: {severity} (Fallback)"}

    def _parse_json(self, text):
        try:
            cleaned = re.sub(r'```json\n?|```\n?', '', text).strip()
            return json.loads(cleaned)
        except Exception:
            return {}
