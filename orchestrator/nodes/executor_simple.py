"""
Simplified Tool Execution Node - For MVP without Supergateway
"""

from typing import Dict, Any
from ..state import ConversationState


class ToolExecutor:
    """Simplified tool executor for MVP testing"""
    
    def __init__(self, memory_client=None):
        self.memory_client = memory_client
        self.execution_count = 0
    
    async def execute_step(self, state: ConversationState) -> ConversationState:
        """Execute a single workflow step"""
        
        if not state.workflow_plan or not state.workflow_plan.get("steps"):
            state.actions_taken.append({
                "action": "no_execution",
                "result": "No workflow plan to execute"
            })
            return state
        
        # For MVP, simulate tool execution
        step = state.workflow_plan["steps"][0] if state.workflow_plan["steps"] else None
        
        if step:
            # Simulate execution based on tool type
            tool_name = step.get("tool", "unknown")
            
            if tool_name == "memory" and self.memory_client:
                # Use actual memory client
                result = await self._execute_memory_tool(step)
            else:
                # Simulate other tools
                result = f"Simulated execution of {tool_name} tool"
            
            state.actions_taken.append({
                "action": f"execute_{tool_name}",
                "tool": tool_name,
                "params": step.get("params", {}),
                "result": result
            })
            
            self.execution_count += 1
        
        return state
    
    async def _execute_memory_tool(self, step: Dict[str, Any]) -> str:
        """Execute memory-related tools"""
        action = step.get("action", "")
        params = step.get("params", {})
        
        try:
            if action == "store":
                success = await self.memory_client.create_entity(
                    name=params.get("name", "memory_entity"),
                    entity_type=params.get("type", "general"),
                    observations=params.get("observations", [])
                )
                return f"Memory stored: {success}"
            
            elif action == "recall":
                memories = await self.memory_client.recall(
                    query=params.get("query", ""),
                    limit=params.get("limit", 5)
                )
                return f"Found {len(memories)} memories"
            
            else:
                return f"Unknown memory action: {action}"
                
        except Exception as e:
            return f"Memory tool error: {str(e)}"