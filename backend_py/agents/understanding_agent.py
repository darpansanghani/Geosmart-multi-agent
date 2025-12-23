import os
import json
import re
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from .context import AgentContext

class UnderstandingAgent:
    """
    UnderstandingAgent - Extracts key entities and intent from complaint text.
    """
    def __init__(self):
        self.name = 'UnderstandingAgent'
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print('Warning: GEMINI_API_KEY not set. Using fallback mode.')
            self.use_fallback = True
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_fallback = False

    async def execute(self, context: AgentContext) -> Dict[str, Any]:
        text = context.get('original_text')
        
        if self.use_fallback:
            return await self._fallback_execution(context, text)
        
        try:
            prompt = f"""You are an Understanding Agent in a multi-agent civic complaint system.

Your task: Analyze the complaint text and extract:
1. Issue type (e.g., garbage accumulation, pothole, water leak, broken streetlight)
2. Urgency indicators (keywords like "emergency", "3 days", "overflowing", "broken")
3. Affected area description (street name, landmark, area)
4. Duration (how long the issue has existed, if mentioned)

Complaint text: "{text}"

Respond ONLY with valid JSON in this exact format:
{{
  "issue_type": "brief description of the issue",
  "urgency_indicators": ["keyword1", "keyword2"],
  "affected_area": "area description",
  "duration": "duration if mentioned, or null"
}}"""

            response = await self.model.generate_content_async(prompt)
            parsed = self._parse_json(response.text)
            
            # Update shared context
            await context.update(self.name, {
                "issue_type": parsed.get("issue_type"),
                "urgency_indicators": parsed.get("urgency_indicators", []),
                "affected_area": parsed.get("affected_area"),
                "duration": parsed.get("duration")
            })
            
            urgency_level = 'High' if parsed.get("urgency_indicators") else 'Normal'
            
            return {
                "summary": f"Issue type: {parsed.get('issue_type')}, Urgency: {urgency_level}, Duration: {parsed.get('duration') or 'Not specified'}"
            }
            
        except Exception as e:
            print(f'UnderstandingAgent error: {e}')
            return await self._fallback_execution(context, text)

    async def _fallback_execution(self, context: AgentContext, text: str) -> Dict[str, Any]:
        lowercase_text = (text or "").lower()
        
        issue_types = {
            'garbage': ['garbage', 'trash', 'waste', 'rubbish', 'litter', 'dump'],
            'pothole': ['pothole', 'road damage', 'crater', 'hole'],
            'water': ['water', 'leak', 'pipe', 'supply', 'burst'],
            'streetlight': ['streetlight', 'street light', 'lamp', 'light'],
            'drainage': ['drainage', 'drain', 'sewage', 'overflow', 'sewer', 'manhole']
        }
        
        issue_type = 'Other'
        for type_key, keywords in issue_types.items():
            if any(kw in lowercase_text for kw in keywords):
                issue_type = type_key.capitalize()
                break
        
        # Add specific check for 'Accident' as per instruction, before general urgency keywords
        if 'accident' in lowercase_text or 'crash' in lowercase_text or 'collision' in lowercase_text:
            issue_type = 'Accident'

        urgency_keywords = ['emergency', 'urgent', 'immediate', 'critical', 'broken', 'accident', 'dead', 'death', 'injury', 'injured', 'major', 'severe', 'danger', 'hazard', 'fire', 'explosion']
        urgency_indicators = [kw for kw in urgency_keywords if kw in lowercase_text]
        
        await context.update(self.name, {
            "issue_type": issue_type,
            "urgency_indicators": urgency_indicators,
            "affected_area": "Area mentioned in text",
            "duration": None
        })
        
        return {
            "summary": f"Issue type: {issue_type} (Fallback logic)"
        }

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            cleaned = re.sub(r'```json\n?|```\n?', '', text).strip()
            return json.loads(cleaned)
        except Exception as e:
            print(f"JSON extract error: {e}")
            return {}
