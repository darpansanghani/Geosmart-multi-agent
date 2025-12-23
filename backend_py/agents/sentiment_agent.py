from .context import AgentContext
from typing import Dict, Any

class SentimentAgent:
    name = "SentimentToneAgent"
    async def execute(self, context: AgentContext) -> Dict[str, Any]:
        return {"summary": "Sentiment Agent Stub"}
