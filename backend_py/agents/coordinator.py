import time
import json
from typing import Dict, Any, List
from ..db.connection import get_pool
from .context import AgentContext
from .understanding_agent import UnderstandingAgent
from .gis_agent import GISIntelligenceAgent
from .classification_agent import ClassificationAgent
from .sentiment_agent import SentimentAgent
from .vision_agent import VisionAgent
from .predictive_agent import PredictiveAgent
from .routing_agent import RoutingAgent
from .action_planning_agent import ActionPlanningAgent

class CoordinatorAgent:
    """
    CoordinatorAgent - Orchestrates the multi-agent workflow
    """
    def __init__(self):
        self.name = 'CoordinatorAgent'
        
        # Initialize all specialized agents
        self.agents = {
            'understanding': UnderstandingAgent(),
            'gis': GISIntelligenceAgent(),
            'classification': ClassificationAgent(),
            'sentiment': SentimentAgent(),
            'vision': VisionAgent(),
            'predictive': PredictiveAgent(),
            'routing': RoutingAgent(),
            'actionPlanning': ActionPlanningAgent()
        }

    async def process_complaint(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a complaint through the multi-agent pipeline."""
        context = AgentContext(complaint_data['id'])
        execution_log: List[Dict[str, Any]] = []
        
        print(f"\n🎯 CoordinatorAgent: Starting parsing for complaint {complaint_data['id']}")
        
        # Initialize context with input data
        await context.update(self.name, {
            "original_text": complaint_data['text'],
            "latitude": complaint_data.get('latitude'),
            "longitude": complaint_data.get('longitude'),
            "address": complaint_data.get('address')
        })
        
        try:
            # STEP 1: Understanding Agent (always runs)
            print('  → Running Understanding Agent...')
            await self._execute_agent('understanding', context, execution_log)
            
            # STEP 2: GIS Intelligence Agent (always runs)
            print('  → Running GIS Intelligence Agent...')
            await self._execute_agent('gis', context, execution_log)
            
            # STEP 3: Classification Agent (always runs)
            print('  → Running Classification Agent...')
            await self._execute_agent('classification', context, execution_log)
            
            # STEP 4: Sentiment & Tone Agent (always runs)
            print('  → Running Sentiment & Tone Agent...')
            await self._execute_agent('sentiment', context, execution_log)
            
            # STEP 5: Visual Intelligence Agent (runs if image exists)
            image_url = complaint_data.get('image_url') or complaint_data.get('imageUrl')
            if image_url:
                print('  → Running Visual Intelligence Agent...')
                await self._execute_agent_with_args('vision', context, execution_log, image_url)
            else:
                print('  ⊗ Skipping Visual Intelligence Agent (no image)')
                
            # STEP 6: Predictive Agent (runs for recurring patterns)
            category = context.get('category')
            recurring_categories = ['Sanitation', 'Roads', 'Water Supply', 'Drainage']
            if category in recurring_categories:
                print('  → Running Predictive Agent...')
                await self._execute_agent('predictive', context, execution_log)
            else:
                print(f"  ⊗ Skipping Predictive Agent (category: {category})")
                
            # DECISION POINT: Routing logic
            severity = context.get('severity')
            # Assuming these might be set by agents...
            severity_elevation = context.get('severity_elevation')
            severity_adjust = context.get('severity_adjustment')
            
            final_severity = self._get_highest_severity([severity, severity_elevation, severity_adjust])
            
            if category and category != 'Other':
                print('  → Running Routing Agent...')
                await self._execute_agent('routing', context, execution_log)
            else:
                print('  ⊗ Skipping Routing Agent')
                
            # DECISION POINT: Action Plan
            if final_severity != severity:
                await context.update(self.name, {'severity': final_severity})
                
            if final_severity in ['Medium', 'High']:
                print('  → Running Action Planning Agent...')
                await self._execute_agent('actionPlanning', context, execution_log)
            else:
                print('  ⊗ Skipping Action Planning Agent')
            
            print(f"✓ Multi-agent processing complete! Executed {len(execution_log)} agents\n")
            
            return {
                "success": True,
                "result": context.get_all(),
                "execution_log": execution_log,
                "total_execution_time_ms": sum(l['execution_time_ms'] for l in execution_log)
            }
            
        except Exception as e:
            print(f'❌ CoordinatorAgent error: {e}')
            execution_log.append({
                "name": "CoordinatorAgent",
                "status": "error",
                "error": str(e)
            })
            return await self._fallback_processing(complaint_data, execution_log)

    async def _execute_agent(self, agent_key: str, context: AgentContext, execution_log: List[Dict[str, Any]]):
        return await self._execute_agent_with_args(agent_key, context, execution_log)

    async def _execute_agent_with_args(self, agent_key: str, context: AgentContext, execution_log: List[Dict[str, Any]], *args):
        agent = self.agents[agent_key]
        start_time = time.time() * 1000
        
        try:
            if args:
                result = await agent.execute(context, *args)
            else:
                result = await agent.execute(context)
                
            execution_time = (time.time() * 1000) - start_time
            
            log_entry = {
                "name": agent.name,
                "status": "success",
                "execution_time_ms": int(execution_time),
                "key_findings": result.get("summary")
            }
            execution_log.append(log_entry)
            
            await self._save_agent_execution(
                context.complaint_id,
                agent.name,
                context.get_all(), # saving state *before*? No, usually after or input state. JS code saved "context.getAll()" as input data? 
                # Re-reading JS: saveAgentExecution(id, name, context.getAll(), result, ...)
                # It passed context.getAll() as "inputData". Since update happens *inside* execute, 
                # context.getAll() at this point includes the updates. So it's actually output state + new updates.
                # Just mirroring JS logic.
                result,
                int(execution_time),
                "success",
                None
            )
            return result
        except Exception as e:
            execution_time = (time.time() * 1000) - start_time
            log_entry = {
                "name": agent.name,
                "status": "error",
                "execution_time_ms": int(execution_time),
                "error": str(e)
            }
            execution_log.append(log_entry)
            
            await self._save_agent_execution(
                context.complaint_id,
                agent.name,
                context.get_all(),
                None,
                int(execution_time),
                "error",
                str(e)
            )
            raise e

    def _get_highest_severity(self, severities: List[Any]) -> str:
        levels = {'Low': 1, 'Medium': 2, 'High': 3}
        highest = 'Low'
        highest_val = 1
        
        for sev in severities:
            if sev and sev in levels and levels[sev] > highest_val:
                highest = sev
                highest_val = levels[sev]
        return highest

    async def _save_agent_execution(self, complaint_id, agent_name, input_data, output_data, exec_time, status, error_msg):
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agent_executions 
                    (complaint_id, agent_name, input_data, output_data, execution_time_ms, status, error_message) 
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    complaint_id, agent_name, json.dumps(input_data, default=str), 
                    json.dumps(output_data, default=str), exec_time, status, error_msg
                )
        except Exception as e:
            print(f"Error saving execution trace: {e}")

    async def _fallback_processing(self, complaint_data, execution_log):
        print('⚠️  Using fallback rule-based processing')
        return {
            "success": False,
            "result": {
                "category": 'Other',
                "severity": 'Medium',
                "department": 'GHMC Central',
                "ai_summary": 'Complaint received - awaiting manual review',
                "suggested_action": 'Route to appropriate department'
            },
            "execution_log": execution_log,
            "fallback": True
        }
