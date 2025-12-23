import json
from typing import Dict, Any, Optional
from ..db.connection import get_pool

class AgentContext:
    """
    AgentContext - Shared memory/context for multi-agent collaboration
    
    This class enables agents to:
    - Read data from previous agents
    - Write their findings for subsequent agents
    - Build collaborative intelligence through shared state
    """
    def __init__(self, complaint_id: int):
        self.complaint_id = complaint_id
        self.data: Dict[str, Any] = {
            # Original input
            "original_text": "",
            "latitude": None,
            "longitude": None,
            "address": None,
            
            # Understanding Agent outputs
            "issue_type": None,
            "urgency_indicators": [],
            "affected_area": None,
            "duration": None,
            
            # GIS Intelligence Agent outputs
            "zone_name": None,
            "ward_number": None,
            "nearby_facilities": [],
            "historical_issues": [],
            
            # Classification Agent outputs
            "category": None,
            "severity": None,
            "impact_scope": None,
            "classification_reasoning": None,
            
            # Routing Agent outputs
            "department": None,
            "assigned_team": None,
            "escalation_needed": False,
            "routing_reasoning": None,
            
            # Action Planning Agent outputs
            "action_plan": None,
            "timeline": None,
            "resources_needed": [],
            "immediate_actions": []
        }

    async def update(self, agent_name: str, data: Dict[str, Any]):
        """Update context with new data from an agent and persist to DB."""
        self.data.update(data)
        await self._save_to_database(agent_name, self.data)

    def get(self, key: str) -> Any:
        """Get a specific value from context."""
        return self.data.get(key)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all context data."""
        return self.data.copy()

    async def _save_to_database(self, agent_name: str, data: Dict[str, Any]):
        """Save context update to database."""
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                # Check if context record exists
                count = await conn.fetchval(
                    'SELECT COUNT(*) FROM agent_context WHERE complaint_id = $1',
                    self.complaint_id
                )
                
                json_data = json.dumps(data)
                
                if count == 0:
                    await conn.execute(
                        'INSERT INTO agent_context (complaint_id, context_data) VALUES ($1, $2)',
                        self.complaint_id, json_data
                    )
                else:
                    await conn.execute(
                        'UPDATE agent_context SET context_data = $1, updated_at = NOW() WHERE complaint_id = $2',
                        json_data, self.complaint_id
                    )
        except Exception as e:
            print(f"Error saving context to database ({agent_name}): {e}")

    @classmethod
    async def load_from_database(cls, complaint_id: int):
        """Load context from database."""
        try:
            pool = await get_pool()
            instance = cls(complaint_id)
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT context_data FROM agent_context WHERE complaint_id = $1',
                    complaint_id
                )
                if row:
                    instance.data = json.loads(row['context_data'])
            return instance
        except Exception as e:
            print(f"Error loading context from database: {e}")
            return cls(complaint_id)
