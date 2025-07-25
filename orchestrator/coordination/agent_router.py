"""
Agent Router - Routes requests to appropriate agents in the multi-agent system
Core coordination component for Mohit's Personal AI Brain
"""

from typing import Dict, List, Any, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..agents.base_agent import BaseAgent
from ..agents.personal_assistant import PersonalAssistantAgent
from ..agents.data_analyst import DataAnalystAgent
from ..agents.hr_director import HRDirectorAgent
from ..agents.dev_lead import DevLeadAgent
from ..agents.operations_manager import OperationsManagerAgent


class AgentRouter:
    """
    Routes user requests to the most appropriate agent(s) in the multi-agent system
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.primary_agent: Optional[BaseAgent] = None
        
        # LLM for routing decisions
        self.routing_llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize with Personal Assistant as primary agent
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize the agent system with Personal Assistant as coordinator"""
        
        # Create Personal Assistant as primary coordinator
        personal_assistant = PersonalAssistantAgent()
        self.register_agent(personal_assistant, is_primary=True)
        
        # Add specialist agents
        self.register_agent(DataAnalystAgent())
        self.register_agent(HRDirectorAgent()) 
        self.register_agent(DevLeadAgent())
        self.register_agent(OperationsManagerAgent())
    
    def register_agent(self, agent: BaseAgent, is_primary: bool = False):
        """Register an agent in the routing system"""
        
        self.agents[agent.role] = agent
        
        if is_primary:
            self.primary_agent = agent
        
        # If this is Personal Assistant, register other agents with it for coordination
        if isinstance(agent, PersonalAssistantAgent):
            for other_agent in self.agents.values():
                if other_agent.role != agent.role:
                    agent.register_agent(other_agent)
    
    async def route_request(self, 
                          request: str, 
                          user_id: str, 
                          interface: str,
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route user request to the most appropriate agent
        
        Args:
            request: User's message/request
            user_id: User identifier (should be "mohit" for Personal AI Brain)
            interface: Interface used (voice, whatsapp, web, etc.)
            context: Additional context
            
        Returns:
            Response from the appropriate agent
        """
        
        context = context or {}
        context.update({
            "user_id": user_id,
            "interface": interface,
            "router_timestamp": asyncio.get_event_loop().time()
        })
        
        # For Phase 1, always route through Personal Assistant as coordinator
        # Later phases will implement more sophisticated routing
        
        if self.primary_agent:
            routing_result = await self.primary_agent.handle_request(request, context)
            routing_result.update({
                "router_decision": "primary_agent",
                "selected_agent": self.primary_agent.role,
                "routing_confidence": 1.0
            })
            return routing_result
        
        # Fallback if no primary agent (shouldn't happen in normal operation)
        return await self._emergency_fallback_response(request, context)
    
    async def _sophisticated_routing(self, 
                                   request: str, 
                                   context: Dict[str, Any]) -> Tuple[BaseAgent, float]:
        """
        Sophisticated routing logic for complex multi-agent scenarios
        (Will be implemented in later phases)
        """
        
        # Get confidence scores from each agent
        agent_scores = {}
        
        for role, agent in self.agents.items():
            try:
                confidence = agent.should_handle_request(request, context)
                agent_scores[role] = confidence
            except Exception as e:
                # Agent failed to evaluate - low confidence
                agent_scores[role] = 0.0
        
        # Select agent with highest confidence
        best_agent_role = max(agent_scores, key=agent_scores.get)
        best_confidence = agent_scores[best_agent_role]
        
        return self.agents[best_agent_role], best_confidence
    
    async def _route_with_llm_analysis(self, 
                                     request: str, 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to analyze request and make sophisticated routing decisions
        (Advanced feature for later phases)
        """
        
        available_agents = {
            role: {
                "role": agent.role,
                "personality": agent.personality,
                "tools": agent.available_tools,
                "authority": agent.decision_authority
            }
            for role, agent in self.agents.items()
        }
        
        routing_prompt = f"""Analyze this request from Mohit and determine the best agent routing:

Request: "{request}"
Context: {context}

Available Agents:
{chr(10).join(f"- {role}: {info['personality']}, Tools: {', '.join(info['tools'])}" for role, info in available_agents.items())}

Determine:
1. Primary agent to handle this request
2. Any additional agents needed for collaboration
3. Confidence level (0.0-1.0)
4. Reasoning for the decision

Respond in JSON:
{{
    "primary_agent": "agent_role",
    "collaborating_agents": ["agent1", "agent2"],
    "confidence": 0.95,
    "reasoning": "explanation of routing decision",
    "workflow_type": "single|collaborative|complex"
}}"""
        
        messages = [
            SystemMessage(content="You are a routing system for Mohit's Personal AI Brain multi-agent system."),
            HumanMessage(content=routing_prompt)
        ]
        
        response = await self.routing_llm.ainvoke(messages)
        
        try:
            import json
            return json.loads(response.content)
        except:
            # Fallback to Personal Assistant
            return {
                "primary_agent": "personal_assistant",
                "collaborating_agents": [],
                "confidence": 0.7,
                "reasoning": "Fallback to Personal Assistant due to routing analysis failure",
                "workflow_type": "single"
            }
    
    async def _emergency_fallback_response(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Emergency fallback when no agents are available"""
        
        return {
            "response": "I apologize, Mohit, but I'm experiencing technical difficulties with the agent routing system. Please try your request again in a moment.",
            "agent": "system_fallback",
            "actions_taken": ["emergency_fallback"],
            "error": "No agents available for routing",
            "available_agents": list(self.agents.keys())
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        
        return {
            "total_agents": len(self.agents),
            "primary_agent": self.primary_agent.role if self.primary_agent else None,
            "available_agents": {
                role: agent.get_agent_info() 
                for role, agent in self.agents.items()
            },
            "router_status": "operational"
        }
    
    def get_agent(self, role: str) -> Optional[BaseAgent]:
        """Get specific agent by role"""
        return self.agents.get(role)
    
    def list_agents(self) -> List[str]:
        """List all registered agent roles"""
        return list(self.agents.keys())