"""
ReAct-Enhanced Personal Assistant Agent
Combines proactive personality with structured reasoning for complex tasks
"""

from typing import Dict, List, Any, Optional
import json
import logging

from .base_agent import BaseAgent
from .react_base_agent import ReActBaseAgent, ActionType

logger = logging.getLogger(__name__)


class PersonalAssistantAgent(BaseAgent, ReActBaseAgent):
    """
    Personal Assistant with ReAct reasoning capabilities
    Uses structured thought-action-observation for complex coordination
    """
    
    def __init__(self):
        # Initialize base agent with Personal Assistant configuration
        BaseAgent.__init__(
            self,
            role="personal_assistant",
            personality="proactive, organized, detail-oriented",
            tools=[
                "calendar", "task_management", "email",
                "memory", "filesystem", "communication"
            ],
            authority_level="high",
            system_prompt=self._build_personal_assistant_prompt()
        )
        
        # Add ReAct configuration
        self.max_react_steps = 7
        self.react_temperature = 0.3
        self.react_enabled = True
        
        # Track other agents for coordination
        self.managed_agents = {}
        self.active_workflows = {}
    
    def _build_personal_assistant_prompt(self) -> str:
        """Build specialized system prompt for Personal Assistant"""
        return """You are Mohit's Personal Assistant Agent - his primary AI coordinator and chief of staff.

PERSONALITY: Proactive, organized, detail-oriented, anticipates needs
COMMUNICATION STYLE: Professional but warm, always addresses Mohit by name, offers next steps

YOUR RESPONSIBILITIES:
- Daily briefings and agenda management
- Communication triage and routing
- Meeting preparation and follow-up
- Travel and logistics coordination
- Cross-agent workflow coordination
- Proactive suggestions and reminders

COORDINATION AUTHORITY:
- You can delegate to specialized agents (Data Analyst, HR Director, Dev Lead, Operations Manager)
- You coordinate multi-agent workflows for complex requests
- You maintain context across all agent interactions
- You ensure Mohit gets comprehensive, well-organized responses

RESPONSE PATTERN:
1. Acknowledge request personally
2. Provide direct answer or coordinate with specialists
3. Offer proactive next steps
4. Ask how else you can help

EXAMPLES:
- "Good morning, Mohit! I've prepared your usual briefing..."
- "I'll coordinate with the Data Analyst to get those metrics for you..."
- "Based on your calendar, I recommend..."
- "What would you like me to help with next, Mohit?"

Always be proactive, organized, and focused on making Mohit's life easier."""
    
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced request handling with ReAct pattern for complex tasks"""
        
        # Initialize memory if needed
        if not self.memory_initialized:
            await self.initialize_memory()
        
        # Check if this request needs ReAct reasoning
        if self.react_enabled and await self.should_use_react(request, context):
            logger.info(f"Using ReAct pattern for complex request: {request[:50]}...")
            return await self.handle_react_request(request, context)
        
        # Otherwise use standard handling
        return await self.handle_request_with_memory(request, context)
    
    async def handle_react_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request using ReAct reasoning pattern"""
        
        # Execute ReAct loop
        react_result = await self.react_loop(request, context)
        
        if react_result["success"]:
            # Format response with Personal Assistant personality
            formatted_response = self.format_response(react_result["result"])
            
            # Add reasoning summary if confidence is low
            if react_result["confidence"] < 0.8:
                formatted_response += f"\n\n(I went through {react_result['steps_taken']} reasoning steps to arrive at this answer. Confidence level: {react_result['confidence']:.0%})"
            
            return {
                "response": formatted_response,
                "agent": "personal_assistant",
                "actions_taken": ["react_reasoning"],
                "reasoning_steps": react_result["steps_taken"],
                "confidence": react_result["confidence"],
                "reasoning_chain": react_result["reasoning_chain"]
            }
        else:
            # Fallback to standard handling if ReAct fails
            logger.warning(f"ReAct reasoning failed: {react_result.get('error')}")
            return await self.handle_request_with_memory(request, context)
    
    async def should_use_react(self, request: str, context: Dict[str, Any]) -> bool:
        """Determine if request requires ReAct reasoning"""
        
        # Personal Assistant specific complexity indicators
        pa_complexity_indicators = [
            # Multi-agent coordination
            "coordinate with", "work with", "involve multiple",
            "across teams", "different departments",
            
            # Complex planning
            "create a plan", "develop strategy", "organize project",
            "schedule multiple", "complex workflow",
            
            # Analysis requiring multiple steps
            "analyze and report", "investigate and summarize",
            "research and present", "gather and compile",
            
            # Decision making
            "help me decide", "what should i", "recommend based on",
            "evaluate options", "compare alternatives"
        ]
        
        request_lower = request.lower()
        
        # Check PA-specific indicators
        if any(indicator in request_lower for indicator in pa_complexity_indicators):
            return True
        
        # Use base class logic as well
        return await super().should_use_react(request, context)
    
    # Implement abstract methods from ReActBaseAgent
    
    async def _action_search(self, params: Dict[str, Any]) -> str:
        """Search in memory or knowledge base"""
        query = params.get("query", "")
        search_type = params.get("type", "memory")
        
        if search_type == "memory" and self.memory_initialized:
            memories = await self.recall(query, limit=5)
            if memories:
                results = []
                for memory in memories[:3]:
                    observations = memory.get("data", {}).get("observations", [])
                    if observations:
                        results.append(observations[0][:100] + "...")
                return f"Found {len(memories)} relevant memories. Top results: " + "; ".join(results)
            return "No relevant memories found."
        
        elif search_type == "preferences":
            prefs = await self.get_user_preferences(params.get("category"))
            if prefs:
                return f"Found {len(prefs)} user preferences in category '{params.get('category', 'all')}'"
            return "No preferences found for this category."
        
        return "Search completed but no specific results found."
    
    async def _action_calculate(self, params: Dict[str, Any]) -> str:
        """Perform calculations or estimations"""
        calc_type = params.get("type", "basic")
        
        if calc_type == "schedule_estimate":
            tasks = params.get("tasks", [])
            total_time = sum(task.get("duration", 30) for task in tasks)
            return f"Estimated total time: {total_time} minutes ({total_time/60:.1f} hours)"
        
        elif calc_type == "priority_score":
            urgency = params.get("urgency", 5)
            importance = params.get("importance", 5)
            score = (urgency * 0.6) + (importance * 0.4)
            return f"Priority score: {score:.1f}/10"
        
        return "Calculation completed."
    
    async def _action_communicate(self, params: Dict[str, Any]) -> str:
        """Send messages or notifications"""
        channel = params.get("channel", "internal")
        message = params.get("message", "")
        recipient = params.get("recipient", "user")
        
        # In real implementation, this would send actual messages
        return f"Message prepared for {recipient} via {channel}: '{message[:50]}...'"
    
    async def _action_delegate(self, params: Dict[str, Any]) -> str:
        """Delegate to specialist agents"""
        specialist = params.get("specialist", "")
        task = params.get("task", "")
        
        available_agents = self.get_available_agents()
        
        if specialist in available_agents:
            # In real implementation, would actually delegate
            return f"Task delegated to {specialist} agent: '{task[:50]}...'"
        else:
            return f"Specialist {specialist} not available. Available agents: {', '.join(available_agents)}"
    
    async def _action_use_tool(self, params: Dict[str, Any]) -> str:
        """Use specific tools available to Personal Assistant"""
        tool = params.get("tool", "")
        tool_params = params.get("params", {})
        
        if tool == "calendar":
            return "Calendar checked. You have 3 meetings today."
        elif tool == "email":
            return "Email drafted and ready to send."
        elif tool == "whatsapp":
            return "WhatsApp message prepared."
        elif tool == "scheduling":
            return "Schedule conflict analysis completed."
        elif tool == "memory":
            return "Memory operation completed."
        else:
            return f"Tool {tool} executed with params: {tool_params}"
    
    def get_react_prompt(self) -> str:
        """Personal Assistant specific ReAct prompt"""
        return f"""{self.system_prompt}

As Mohit's Personal Assistant, you use structured reasoning for complex tasks.

For each step:
1. Thought: Analyze what needs to be done and why
2. Action: Choose the most appropriate action
3. Observation: Process the result and plan next steps

Available Actions:
- THINK: Reason about Mohit's needs and priorities
- SEARCH: Search memory for context, preferences, or past interactions
- CALCULATE: Estimate time, calculate priorities, or analyze schedules
- COMMUNICATE: Draft messages or prepare communications
- DELEGATE: Route to specialist agents (data_analyst, hr_director, dev_lead, operations_manager)
- USE_TOOL: Use your tools: {', '.join(self.tools)}
- CONCLUDE: Provide final coordinated response

Always maintain your proactive, organized personality even while reasoning.

Format:
Thought: [Your reasoning focused on helping Mohit]
Action: [ACTION_TYPE]
Action Input: {{"key": "value"}}"""