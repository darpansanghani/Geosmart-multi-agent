import asyncio
from typing import Dict, Any

# MOCK CONTEXT to bypass DB
class MockContext:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def get_all(self):
        return self.data
        
    async def update(self, agent_name, new_data):
        self.data.update(new_data)
        # No DB save

from backend_py.agents.gis_agent import GISIntelligenceAgent
from backend_py.agents.classification_agent import ClassificationAgent

async def debug_agents():
    # Zone Tests
    # Secunderabad (North): 17.48, 78.50
    lat_sec = 17.48
    lng_sec = 78.50
    
    # Charminar (South): 17.30, 78.45
    lat_char = 17.30
    lng_char = 78.45
    
    print("--- Debugging GIS Agent ---")
    gis = GISIntelligenceAgent()
    
    ctx_sec = MockContext()
    await ctx_sec.update("TEST", {"latitude": lat_sec, "longitude": lng_sec})
    res_sec = await gis.execute(ctx_sec)
    print(f"Secunderabad Coords ({lat_sec}, {lng_sec}): {res_sec['summary']}")
    
    ctx_char = MockContext()
    await ctx_char.update("TEST", {"latitude": lat_char, "longitude": lng_char})
    res_char = await gis.execute(ctx_char)
    print(f"Charminar Coords ({lat_char}, {lng_char}): {res_char['summary']}")
    
    print("\n--- Debugging Classification Agent ---")
    cls = ClassificationAgent()
    # Force use_fallback to True for debugging logic
    cls.use_fallback = True 
    print("(Forcing Fallback Logic for Debug)")

    ctx_text = MockContext()
    # Mocking what Understanding Agent would extract with the NEW logic
    # But since debug runs logic in isolation, we should test Understanding agent extraction too?
    # Actually, the previous debug script tested Classification agent.
    # Let's trust my code analysis that UnderstandingAgent adds 'urgent' indicator now.
    # So I will inject the extraction result I expect.
    await ctx_text.update("TEST", {
        "original_text": "major bike accident, 2 person dead",
        # Simulate what Understanding agent does:
        "issue_type": "Accident", 
        "urgency_indicators": ["accident", "dead", "major"], 
        "nearby_facilities": [] 
    })
    
    res_text = await cls.execute(ctx_text)
    data_text = ctx_text.get_all()
    print(f"Urgent Text Result: Severity={data_text.get('severity')}, Category={data_text.get('category')}")
    print(f"Reasoning: {data_text.get('classification_reasoning')}")

if __name__ == "__main__":
    asyncio.run(debug_agents())
