import os
import json
import re
import google.generativeai as genai
from typing import Dict, Any
from .context import AgentContext

class RoutingAgent:
    """RoutingAgent - Assigns complaints to appropriate departments and teams"""
    def __init__(self):
        self.name = 'RoutingAgent'
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.use_fallback = True
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_fallback = False

    async def execute(self, context: AgentContext) -> Dict[str, Any]:
        category = context.get('category')
        severity = context.get('severity')
        ward_number = context.get('ward_number')
        impact_scope = context.get('impact_scope')
        
        if self.use_fallback or not category:
            return await self._fallback_execution(context, category, severity, ward_number)
            
        try:
            prompt = f"""You are a Routing Agent responsible for assigning civic complaints.

Context:
- Category: {category}
- Severity: {severity}
- Ward: {ward_number}
- Impact scope: {impact_scope}

Available departments:
- GHMC Sanitation
- GHMC Roads
- GHMC Electrical
- GHMC Water Works
- GHMC Engineering

Respond ONLY with valid JSON:
{{
  "department": "department name",
  "assigned_team": "specific team or role",
  "escalation_needed": true/false,
  "reasoning": "brief explanation"
}}"""

            response = await self.model.generate_content_async(prompt)
            parsed = self._parse_json(response.text)
            
            await context.update(self.name, {
                "department": parsed.get("department"),
                "assigned_team": parsed.get("assigned_team"),
                "escalation_needed": parsed.get("escalation_needed", False),
                "routing_reasoning": parsed.get("reasoning")
            })
            
            return {
                "summary": f"Department: {parsed.get('department')}, Team: {parsed.get('assigned_team')}"
            }
            
        except Exception:
            return await self._fallback_execution(context, category, severity, ward_number)

    async def _fallback_execution(self, context, category, severity, ward_number):
        dept_map = {
            'Sanitation': 'GHMC Sanitation',
            'Roads': 'GHMC Roads',
            'Streetlights': 'GHMC Electrical',
            'Water Supply': 'GHMC Water Works',
            'Drainage': 'GHMC Engineering',
            'Emergency': 'GHMC Disaster Management',
            'Accident': 'GHMC Disaster Management',
            'Other': 'GHMC Central'
        }
        department = dept_map.get(category, 'GHMC Central')
        
        team = f"Field Team - Ward {ward_number}"
        if severity == 'High': team = f"{department} - Department Head"
        elif severity == 'Medium': team = f"Ward {ward_number} Supervisor"
        
        await context.update(self.name, {
            "department": department,
            "assigned_team": team,
            "escalation_needed": (severity == 'High'),
            "routing_reasoning": "Fallback Logic"
        })
        return {"summary": f"Department: {department}, Team: {team} (Fallback)"}

    def _parse_json(self, text):
        try:
            cleaned = re.sub(r'```json\n?|```\n?', '', text).strip()
            return json.loads(cleaned)
        except Exception:
            return {}
