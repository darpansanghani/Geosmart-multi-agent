from .context import AgentContext
from typing import Dict, Any

class VisionAgent:
    name = "VisualIntelligenceAgent"
    async def execute(self, context: AgentContext, image_url: str) -> Dict[str, Any]:
        return {"summary": "Vision Agent Stub"}
