"""
Personal Assistant Agent - Primary coordinator for Mohit's Personal AI Brain
Proactive, organized, anticipates needs, manages other agents
"""

from typing import Dict, List, Any, Optional
from langchain.schema import HumanMessage, SystemMessage
import re
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PersonalAssistantAgent(BaseAgent):
    """
    Personal Assistant Agent - Mohit's primary coordinator
    
    Personality: Proactive, organized, anticipates needs
    Role: Chief of Staff - coordinates with other agents, manages daily tasks
    """
    
    def __init__(self):
        super().__init__(
            role="personal_assistant",
            personality="proactive_organized",
            tools=[
                "calendar", "email", "whatsapp", "scheduling", 
                "memory", "filesystem", "communication"
            ],
            authority_level="high",
            system_prompt=self._build_personal_assistant_prompt()
        )
        
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
        """Handle request as Personal Assistant with memory integration"""
        
        # Initialize memory if not already done
        if not self.memory_initialized:
            await self.initialize_memory()
        
        # Use memory-enhanced request handling
        return await self.handle_request_with_memory(request, context)
    
    async def initialize_memory(self):
        """Initialize memory client connection"""
        try:
            # Use the base agent's memory initialization
            success = await super().initialize_memory()
            self.memory_initialized = success
        except Exception as e:
            logger.warning(f"Memory initialization failed: {e}")
            self.memory_initialized = False
    
    async def _handle_request_with_memory_context(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method called by handle_request_with_memory"""
        
        # For simple requests, skip analysis and respond directly
        if self._is_simple_request(request):
            return await self._handle_direct_request(request, context)
        
        # Analyze if this needs multi-agent coordination
        complexity_analysis = await self._analyze_request_complexity(request, context)
        
        if complexity_analysis["requires_coordination"]:
            return await self._coordinate_multi_agent_workflow(request, context, complexity_analysis)
        else:
            return await self._handle_direct_request(request, context)
    
    def _is_simple_request(self, request: str) -> bool:
        """Check if request is simple enough to skip analysis"""
        # Remove any escape characters and normalize
        request_lower = request.lower().strip().replace('\\', '')
        
        # Simple greetings and status checks
        simple_patterns = [
            r'^(hi|hello|hey|good morning|good afternoon|good evening)[\s!?\.]*$',
            r'^how are you[\s!?\.]*$',
            r'^what\'s up[\s!?\.]*$',
            r'^(thank you|thanks|thx)[\s!?\.]*$',
            r'^(bye|goodbye)[\s!?\.]*$',
            r'^what time is it[\s!?\.]*$',
            r'^what\'s the (date|time)[\s!?\.]*$',
            r'^who are you[\s!?\.]*$'
        ]
        
        return any(re.match(pattern, request_lower) for pattern in simple_patterns)
    
    def should_handle_request(self, request: str, context: Dict[str, Any]) -> float:
        """Personal Assistant can handle most requests or coordinate for complex ones"""
        
        # Personal Assistant has high confidence for most requests
        # as coordinator role
        coordination_keywords = [
            "coordinate", "organize", "schedule", "plan", "prepare",
            "remind", "brief", "summary", "status", "update"
        ]
        
        delegation_keywords = [
            "analyze", "data", "report", "technical", "code", "infrastructure",
            "hr", "employee", "team", "hiring", "policy"
        ]
        
        request_lower = request.lower()
        
        # High confidence for coordination tasks
        if any(keyword in request_lower for keyword in coordination_keywords):
            return 0.9
        
        # Medium-high confidence for delegation tasks
        if any(keyword in request_lower for keyword in delegation_keywords):
            return 0.8
        
        # Default medium confidence as coordinator
        return 0.7
    
    async def _analyze_request_complexity(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if request needs multi-agent coordination"""
        
        # Quick pattern matching for specialist domains
        request_lower = request.lower()
        
        # Check for specialist agent keywords
        if any(word in request_lower for word in ["analyze", "data", "report", "metrics", "dashboard", "statistics"]):
            return {
                "requires_coordination": True,
                "specialist_agents_needed": ["data_analyst"],
                "workflow_steps": ["route_to_data_analyst"],
                "complexity_level": "moderate",
                "reasoning": "Data analysis request detected"
            }
        elif any(word in request_lower for word in ["hire", "hiring", "employee", "performance review", "hr"]):
            return {
                "requires_coordination": True,
                "specialist_agents_needed": ["hr_director"],
                "workflow_steps": ["route_to_hr_director"],
                "complexity_level": "moderate",
                "reasoning": "HR-related request detected"
            }
        elif any(word in request_lower for word in ["code", "deploy", "security", "architecture", "development"]):
            return {
                "requires_coordination": True,
                "specialist_agents_needed": ["dev_lead"],
                "workflow_steps": ["route_to_dev_lead"],
                "complexity_level": "moderate",
                "reasoning": "Development request detected"
            }
        elif any(word in request_lower for word in ["project", "budget", "operations", "vendor", "process"]):
            return {
                "requires_coordination": True,
                "specialist_agents_needed": ["operations_manager"],
                "workflow_steps": ["route_to_operations_manager"],
                "complexity_level": "moderate",
                "reasoning": "Operations request detected"
            }
        
        # Default: handle directly
        return {
            "requires_coordination": False,
            "specialist_agents_needed": [],
            "workflow_steps": ["handle_directly"],
            "complexity_level": "simple",
            "reasoning": "General request - can handle directly"
        }
    
    async def _handle_direct_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request directly as Personal Assistant with memory context"""
        
        # Skip the redundant check since we already checked in _handle_request_with_memory_context
        
        # Build memory-enhanced context only if memory is enabled
        memory_context = ""
        if self.memory_initialized:
            if context.get("memory_summary"):
                memory_context = f"\n\nRecent context from memory:\n{context['memory_summary']}"
            
            relevant_memories = context.get("relevant_memories", [])
            if relevant_memories:
                memory_context += f"\n\nRelevant past interactions:\n"
                for memory in relevant_memories[:1]:  # Only top 1 memory for speed
                    observations = memory.get("data", {}).get("observations", [])
                    if observations:
                        memory_context += f"- {observations[0][:100]}...\n"
        
        # Streamlined prompt for faster response
        response_prompt = f"""As Mohit's Personal Assistant, respond to: "{request}"
{memory_context}
Be helpful, organized, and proactive. Address Mohit by name and offer next steps."""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=response_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Add Personal Assistant personality formatting
        formatted_response = self.format_response(response.content)
        
        return {
            "response": formatted_response,
            "agent": "personal_assistant",
            "actions_taken": ["direct_response"],
            "tools_used": ["personal_assistant_llm"],
            "coordination_required": False
        }
    
    async def _quick_response(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ultra-fast response for simple requests without LLM call"""
        # Remove any escape characters and normalize
        request_lower = request.lower().strip().replace('\\', '')
        
        # Quick responses for common patterns
        if re.match(r'^(hi|hello|hey)[\s!?\.]*$', request_lower):
            response = f"Hello Mohit! I'm here and ready to assist you. What would you like me to help with today?"
        elif re.match(r'^how are you[\s!?\.]*$', request_lower):
            response = f"I'm functioning optimally and ready to help you, Mohit! How can I assist you today?"
        elif re.match(r'^(thank you|thanks|thx)[\s!?\.]*$', request_lower):
            response = f"You're very welcome, Mohit! Is there anything else I can help you with?"
        elif re.match(r'^(bye|goodbye)[\s!?\.]*$', request_lower):
            response = f"Goodbye, Mohit! Feel free to reach out whenever you need assistance. Have a great day!"
        elif re.match(r'^what time is it[\s!?\.]*$', request_lower):
            response = f"I don't have real-time access to the current time, Mohit. You can check your system clock or ask me to help with scheduling tasks instead. What would you like me to help with?"
        elif re.match(r'^what.*date[\s!?\.]*$', request_lower):
            response = f"I don't have real-time access to the current date, Mohit. I can help you with planning and scheduling though. What would you like me to assist with?"
        else:
            # For other simple patterns, provide a general response
            response = f"I'm here to help, Mohit! Could you please provide more details about what you need assistance with?"
        
        return {
            "response": response,
            "agent": "personal_assistant",
            "actions_taken": ["quick_response"],
            "tools_used": ["pattern_matching"],
            "coordination_required": False
        }
    
    async def _coordinate_multi_agent_workflow(self, 
                                             request: str, 
                                             context: Dict[str, Any], 
                                             analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multi-agent workflow for complex requests"""
        
        # For now, provide coordination response (actual agent delegation will be implemented next)
        coordination_response = f"""I'll coordinate with the appropriate specialists to handle your request, Mohit.

Based on your request: "{request}"

I'm organizing the following workflow:
{chr(10).join(f'• {step}' for step in analysis.get('workflow_steps', []))}

"""
        
        if analysis.get('specialist_agents_needed'):
            coordination_response += f"""I'll be working with these specialist agents:
{chr(10).join(f'• {agent.replace("_", " ").title()} Agent' for agent in analysis['specialist_agents_needed'])}

"""
        
        coordination_response += "I'll coordinate everything and provide you with a comprehensive response. What would you like me to prioritize first?"
        
        return {
            "response": coordination_response,
            "agent": "personal_assistant",
            "actions_taken": ["workflow_coordination"],
            "specialist_agents": analysis.get('specialist_agents_needed', []),
            "workflow_steps": analysis.get('workflow_steps', []),
            "coordination_required": True
        }
    
    def format_response(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Format response with Personal Assistant personality"""
        
        # Ensure response addresses Mohit personally and offers help
        if "mohit" not in content.lower():
            content = f"Mohit, {content.lstrip()}"
        
        # Add proactive next steps if not present
        if not any(phrase in content.lower() for phrase in ["what would you like", "how else can", "next steps"]):
            content += "\n\nWhat would you like me to help with next, Mohit?"
        
        return content
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialist agent for coordination"""
        self.managed_agents[agent.role] = agent
    
    def get_available_agents(self) -> List[str]:
        """Get list of available specialist agents"""
        return list(self.managed_agents.keys())
    
    async def delegate_to_specialist(self, 
                                   specialist_role: str, 
                                   request: str, 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate request to specialist agent"""
        
        if specialist_role not in self.managed_agents:
            return {
                "error": f"Specialist agent {specialist_role} not available",
                "available_agents": self.get_available_agents()
            }
        
        specialist_agent = self.managed_agents[specialist_role]
        
        # Add coordination context
        delegation_context = {
            **context,
            "delegated_by": "personal_assistant",
            "coordination_id": f"coord_{len(self.active_workflows)}"
        }
        
        return await specialist_agent.handle_request(request, delegation_context)
    
    # === Memory-Enhanced Personal Assistant Methods ===
    
    async def store_user_preference(self, preference: str, category: str = "general") -> bool:
        """Store user preference in memory"""
        return await self.create_entity(
            name=f"mohit_preference_{category}",
            entity_type="user_preference",
            observations=[preference],
            metadata={"category": category, "importance": "high"}
        )
    
    async def get_user_preferences(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve user preferences from memory"""
        query = f"mohit preferences {category}" if category else "mohit preferences"
        return await self.recall(query, limit=10)
    
    async def store_meeting_notes(self, meeting_details: str, participants: List[str] = None) -> bool:
        """Store meeting notes and create participant relationships"""
        # Store meeting as entity
        meeting_name = f"meeting_{len(self.conversation_history)}"
        success = await self.create_entity(
            name=meeting_name,
            entity_type="meeting",
            observations=[meeting_details],
            metadata={"participants": participants or [], "type": "meeting_notes"}
        )
        
        # Create relationships with participants if provided
        # TODO: Implement when create_relation is available in memory client
        if success and participants:
            # For now, store participant info as part of the meeting entity
            pass
        
        return success
    
    async def get_daily_agenda(self) -> str:
        """Generate daily agenda using memory context"""
        # Get daily brief from memory (if available in future)
        daily_brief = {"content": ""}
        
        # Get recent meetings and tasks
        recent_meetings = await self.recall("meeting today", limit=5)
        recent_tasks = await self.recall("task todo", limit=5)
        
        agenda = "📋 **Daily Agenda for Mohit**\n\n"
        
        if daily_brief.get("content"):
            agenda += f"**Daily Brief:**\n{daily_brief['content']}\n\n"
        
        if recent_meetings:
            agenda += "**Recent Meetings:**\n"
            for meeting in recent_meetings[:3]:
                observations = meeting.get("data", {}).get("observations", [])
                if observations:
                    agenda += f"• {observations[0][:100]}...\n"
            agenda += "\n"
        
        if recent_tasks:
            agenda += "**Pending Tasks:**\n"
            for task in recent_tasks[:3]:
                observations = task.get("data", {}).get("observations", [])
                if observations:
                    agenda += f"• {observations[0][:100]}...\n"
            agenda += "\n"
        
        agenda += "What would you like to focus on first today, Mohit?"
        
        return agenda
    
    async def proactive_suggestions(self) -> List[str]:
        """Generate proactive suggestions based on memory context"""
        suggestions = []
        
        # Get recent context
        recent_memories = await self.recall("mohit", limit=10)
        
        # Analyze patterns for suggestions
        if recent_memories:
            # Look for recurring themes
            content_words = []
            for memory in recent_memories:
                observations = memory.get("data", {}).get("observations", [])
                for obs in observations:
                    content_words.extend(obs.lower().split())
            
            # Basic pattern detection (can be enhanced)
            word_freq = {}
            for word in content_words:
                if len(word) > 4:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Generate suggestions based on frequent topics
            top_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for topic, freq in top_topics:
                if freq > 1:
                    suggestions.append(f"Follow up on {topic.replace('_', ' ')} activities")
        
        # Default suggestions if no patterns found
        if not suggestions:
            suggestions = [
                "Schedule time for strategic planning",
                "Review and organize recent communications",
                "Check in on ongoing projects"
            ]
        
        return suggestions[:5]  # Limit to 5 suggestions