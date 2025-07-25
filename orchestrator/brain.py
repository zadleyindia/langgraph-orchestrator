"""
Personal AI Brain - Multi-Agent Orchestration System
Transformed to use specialized agents with LangGraph coordination
"""

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Dict, Any
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .state import ConversationState
from .nodes.intent_analyzer import IntentAnalyzer
from .nodes.planner import WorkflowPlanner
from .nodes.executor_simple import ToolExecutor
from .nodes.responder import ResponseGenerator
# Memory client will be injected through proper MCP connection
# from .clients.memory_client_direct import MemoryClientDirect
from .coordination.agent_router import AgentRouter

class PersonalAIBrain:
    """Multi-Agent Personal AI Brain for Mohit - Orchestration with specialized agents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize multi-agent system
        self.agent_router = AgentRouter()
        
        # Memory client will be initialized with MCP connection
        self.memory = None  # Will be set up with MCP Supergateway
        
        # Initialize nodes (legacy - will be replaced by agent-specific processing)
        self.intent_analyzer = IntentAnalyzer(self.llm)
        self.planner = WorkflowPlanner(self.llm)
        self.executor = ToolExecutor(self.memory)  # Pass memory client instead
        self.responder = ResponseGenerator(self.llm)
        
        # Build the graph (enhanced for multi-agent coordination)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the enhanced LangGraph workflow with multi-agent coordination"""
        
        workflow = StateGraph(ConversationState)
        
        # Add enhanced nodes with agent coordination
        workflow.add_node("route_to_agent", self._route_to_agent_node)
        workflow.add_node("agent_processing", self._agent_processing_node)
        
        # Optional memory nodes (will gracefully skip if memory service unavailable)
        # workflow.add_node("retrieve_memory", self.memory.retrieve_context)
        # workflow.add_node("store_memory", self.memory.store_context)
        
        # Define the enhanced flow (simplified for Phase 1)
        workflow.set_entry_point("route_to_agent")
        
        workflow.add_edge("route_to_agent", "agent_processing")
        workflow.add_edge("agent_processing", END)
        
        # Full flow with memory (for when memory service is available):
        # workflow.add_edge("route_to_agent", "retrieve_memory")
        # workflow.add_edge("retrieve_memory", "agent_processing")
        # workflow.add_edge("agent_processing", "store_memory")
        # workflow.add_edge("store_memory", END)
        
        return workflow.compile()
    
    async def _route_to_agent_node(self, state: ConversationState) -> ConversationState:
        """Node for routing request to appropriate agent"""
        
        # Route through agent router
        agent_response = await self.agent_router.route_request(
            request=state.current_message,
            user_id=state.user_id,
            interface=state.interface,
            context=state.context
        )
        
        # Store agent routing information in state
        state.context["agent_response"] = agent_response
        state.context["selected_agent"] = agent_response.get("selected_agent", agent_response.get("agent", "unknown"))
        state.context["agent_info"] = {
            "routing_confidence": agent_response.get("routing_confidence", 0.0),
            "coordination_required": agent_response.get("coordination_required", False)
        }
        
        return state
    
    async def _agent_processing_node(self, state: ConversationState) -> ConversationState:
        """Node for agent-specific processing and response generation"""
        
        agent_response = state.context.get("agent_response", {})
        
        # Set the response from the agent
        state.response = agent_response.get("response", "No response from agent")
        
        # Track actions taken by the agent
        state.actions_taken = agent_response.get("actions_taken", [])
        
        # Add agent message to conversation
        selected_agent = state.context.get("selected_agent", "unknown")
        state.add_message("assistant", state.response)
        
        return state
    
    async def process_request(self, message: str, user_id: str, interface: str, 
                            session_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user request through the brain"""
        
        # Initialize state
        state = ConversationState(
            user_id=user_id,
            session_id=session_id or str(uuid.uuid4()),
            interface=interface,
            current_message=message,
            context=context or {}
        )
        
        state.add_message("user", message)
        
        try:
            # Run through the graph
            result = await self.graph.ainvoke(state)
            
            # Extract the final state from the result
            # LangGraph returns a dictionary, not a ConversationState object
            if isinstance(result, dict):
                final_state = result
                return {
                    "response": final_state.get("response", ""),
                    "agent": final_state.get("context", {}).get("selected_agent", "unknown"),
                    "actions_taken": final_state.get("actions_taken", []),
                    "context_updated": len(final_state.get("actions_taken", [])) > 0,
                    "session_id": final_state.get("session_id", ""),
                    "multi_agent_info": final_state.get("context", {}).get("agent_info", {})
                }
            else:
                # Fallback for state objects
                final_state = result if hasattr(result, 'response') else state
                return {
                    "response": final_state.response,
                    "agent": final_state.context.get("selected_agent", "unknown"),
                    "actions_taken": final_state.actions_taken,
                    "context_updated": len(final_state.actions_taken) > 0,
                    "session_id": final_state.session_id,
                    "multi_agent_info": final_state.context.get("agent_info", {})
                }
            
        except Exception as e:
            return {
                "response": f"I apologize, Mohit, but I encountered an error: {str(e)}",
                "agent": "error_handler",
                "actions_taken": [],
                "context_updated": False,
                "session_id": state.session_id,
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the brain and connected services"""
        
        # Memory system status (no supergateway needed)
        
        # Check memory system
        memory_status = await self.memory.health_check()
        
        # Check agent system status
        agent_status = self.agent_router.get_agent_status()
        
        return {
            "brain_status": "multi_agent_operational",
            "memory": memory_status,
            "agent_system": agent_status,
            "llm_model": self.llm.model_name,
            "graph_nodes": 4,  # Simplified count
            "architecture": "multi_agent_langgraph"
        }