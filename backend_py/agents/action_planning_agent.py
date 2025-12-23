import os
import json
import re
import google.generativeai as genai
from typing import Dict, Any
from .context import AgentContext

class ActionPlanningAgent:
    """ActionPlanningAgent - Creates resolution plans"""
    def __init__(self):
        self.name = 'ActionPlanningAgent'
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
        department = context.get('department')
        issue_type = context.get('issue_type')
        nearby_facilities = context.get('nearby_facilities') or []
        
        if self.use_fallback:
            return await self._fallback_execution(context, category, severity)
            
        try:
            prompt = f"""You are an Action Planning Agent.

Context:
- Issue: {issue_type}
- Category: {category}
- Severity: {severity}
- Department: {department}
- Nearby facilities: {", ".join(nearby_facilities)}

Create specific actionable plan.
Respond ONLY with valid JSON:
{{
  "immediate_actions": ["action 1", "action 2"],
  "timeline": "X hours/days",
  "resources_needed": ["resource 1", "resource 2"],
  "notes": "considerations"
}}"""

            response = await self.model.generate_content_async(prompt)
            parsed = self._parse_json(response.text)
            
            await context.update(self.name, {
                "action_plan": parsed,
                "timeline": parsed.get("timeline"),
                "resources_needed": parsed.get("resources_needed"),
                "immediate_actions": parsed.get("immediate_actions")
            })
            
            return {
                "summary": f"Plan created, Timeline: {parsed.get('timeline')}"
            }
            
        except Exception:
            return await self._fallback_execution(context, category, severity)

    async def _fallback_execution(self, context, category, severity):
        # Simplified templates
        templates = {
            'Sanitation': {'actions': ['Alert supervisor', 'Dispatch truck'], 'res': ['Truck', 'Workers'], 'hours': 4},
            'Roads': {'actions': ['Assess damage', 'Dispatch repair crew'], 'res': ['Asphalt', 'Tools'], 'hours': 24},
            'Streetlights': {'actions': ['Check circuit', 'Replace bulb'], 'res': ['Ladder', 'Electrician'], 'hours': 6},
            'Water Supply': {'actions': ['Locate leak', 'Shut valve'], 'res': ['Plumber', 'Parts'], 'hours': 8},
            'Drainage': {'actions': ['Clear blockage'], 'res': ['Cleaner machine'], 'hours': 12},
        }
        tmpl = templates.get(category, templates['Sanitation'])
        
        timeline = f"{tmpl['hours']} hours"
        if severity == 'High': timeline = f"{tmpl['hours']//2} hours"
        
        plan = {
            "immediate_actions": tmpl['actions'],
            "timeline": timeline,
            "resources_needed": tmpl['res'],
            "notes": "Fallback Plan"
        }
        
        await context.update(self.name, {
            "action_plan": plan,
            "timeline": timeline,
            "resources_needed": tmpl['res'],
            "immediate_actions": tmpl['actions']
        })
        return {"summary": f"Plan: {len(tmpl['actions'])} steps, Timeline: {timeline} (Fallback)"}

    def _parse_json(self, text):
        try:
            cleaned = re.sub(r'```json\n?|```\n?', '', text).strip()
            return json.loads(cleaned)
        except Exception:
            return {}
