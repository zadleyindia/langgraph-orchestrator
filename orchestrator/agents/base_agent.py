"""
Base Agent Class for Personal AI Brain Multi-Agent Framework
Provides foundation for all specialized agents with Memory Integration
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import uuid
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..state import ConversationState

# Import memory client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from memory_client import LangGraphMemoryClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents in Mohit's Personal AI Brain"""
    
    def __init__(self, 
                 role: str, 
                 personality: str, 
                 tools: List[str], 
                 authority_level: str,
                 system_prompt: str = None,
                 supergateway_url: str = "http://localhost:3004"):
        """
        Initialize base agent with memory integration
        
        Args:
            role: Agent's role identifier (e.g., "personal_assistant")
            personality: Agent's personality type (e.g., "proactive_organized")
            tools: List of MCP tools this agent can use
            authority_level: Decision-making authority ("low", "medium", "high")
            system_prompt: Custom system prompt for agent personality
            supergateway_url: URL for supergateway-memory service
        """
        self.role = role
        self.personality = personality
        self.available_tools = tools
        self.decision_authority = authority_level
        self.agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
        self.supergateway_url = supergateway_url
        
        # Initialize LLM for this agent
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize memory client
        self.memory_client = LangGraphMemoryClient(supergateway_url)
        self.memory_initialized = False
        
        # Build system prompt
        self.system_prompt = system_prompt or self._build_default_system_prompt()
        
        # Agent-specific memory and context
        self.context = {}
        self.conversation_history = []
        self.recent_memories = []
    
    def _build_default_system_prompt(self) -> str:
        """Build default system prompt based on agent role and personality"""
        return f"""You are a {self.role} agent in Mohit's Personal AI Brain system.

Your role: {self.role}
Your personality: {self.personality}
Your available tools: {', '.join(self.available_tools)}
Your authority level: {self.decision_authority}

Key principles:
- You are specifically working for Mohit and his personal/professional needs
- Maintain your distinct personality in all responses
- Use only tools available to your role
- Collaborate with other agents when needed
- Always address Mohit by name when appropriate
- Focus on being helpful, proactive, and aligned with Mohit's goals

Respond in character with your specialized expertise."""
    
    @abstractmethod
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request using agent-specific logic
        
        Args:
            request: User's message/request
            context: Current conversation context
            
        Returns:
            Dict containing response and any actions taken
        """
        pass
    
    @abstractmethod
    def should_handle_request(self, request: str, context: Dict[str, Any]) -> float:
        """
        Determine if this agent should handle the request
        
        Args:
            request: User's message/request
            context: Current conversation context
            
        Returns:
            Confidence score (0.0-1.0) for handling this request
        """
        pass
    
    def format_response(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Format response with agent personality
        
        Args:
            content: Raw response content
            metadata: Additional context for formatting
            
        Returns:
            Personality-formatted response
        """
        # Default formatting - agents can override
        return f"{content}"
    
    async def analyze_intent(self, request: str) -> Dict[str, Any]:
        """Analyze user intent specific to this agent's domain"""
        
        analysis_prompt = f"""Analyze this request from Mohit for the {self.role} agent:

Request: "{request}"

Determine:
1. Primary intent within {self.role} domain
2. Required tools from: {', '.join(self.available_tools)}
3. Complexity level (simple/moderate/complex)
4. Confidence this agent should handle it (0.0-1.0)

Respond in JSON format:
{{
    "intent": "brief description",
    "tools_needed": ["tool1", "tool2"],
    "complexity": "simple|moderate|complex",
    "confidence": 0.95,
    "reasoning": "why this agent should/shouldn't handle it"
}}"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            import json
            return json.loads(response.content)
        except:
            # Fallback if JSON parsing fails
            return {
                "intent": "analysis_failed",
                "tools_needed": [],
                "complexity": "simple",
                "confidence": 0.0,
                "reasoning": "Failed to parse intent analysis"
            }
    
    async def collaborate_with_agent(self, 
                                   target_agent: 'BaseAgent', 
                                   request: str, 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collaborate with another agent
        
        Args:
            target_agent: Agent to collaborate with
            request: Request to delegate/collaborate on
            context: Current context
            
        Returns:
            Result from collaboration
        """
        # Add collaboration metadata
        collaboration_context = {
            **context,
            "collaborating_agent": self.role,
            "collaboration_reason": f"Request delegated from {self.role} to {target_agent.role}"
        }
        
        return await target_agent.handle_request(request, collaboration_context)
    
    def update_context(self, key: str, value: Any):
        """Update agent's context"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get value from agent's context"""
        return self.context.get(key, default)
    
    def add_to_history(self, role: str, message: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": uuid.uuid4().hex,
            "agent": self.role
        })
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "role": self.role,
            "personality": self.personality,
            "tools": self.available_tools,
            "authority": self.decision_authority,
            "agent_id": self.agent_id,
            "status": "active",
            "memory_initialized": self.memory_initialized
        }
    
    # === Memory Integration Methods ===
    
    async def initialize_memory(self) -> bool:
        """Initialize memory integration for this agent"""
        # Check if memory is enabled
        if os.getenv("ENABLE_MEMORY", "false").lower() != "true":
            logger.info(f"Agent {self.agent_id}: Memory service disabled by configuration")
            self.memory_initialized = False
            return False
            
        try:
            # Test memory connectivity
            is_healthy = await self.memory_client.health_check()
            if not is_healthy:
                logger.warning(f"Agent {self.agent_id}: Memory service unhealthy, proceeding without persistence")
                return False
            
            # Load agent's recent memories
            await self._load_agent_memories()
            
            self.memory_initialized = True
            logger.info(f"Agent {self.agent_id} ({self.role}) memory initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize memory for agent {self.agent_id}: {str(e)}")
            return False
    
    async def _load_agent_memories(self):
        """Load recent memories and context for this agent"""
        try:
            # Get recent memories for this agent
            recent_memories = await self.memory_client.get_agent_memories(
                agent_id=self.agent_id,
                limit=10
            )
            
            self.recent_memories = recent_memories
            self.context["recent_memories"] = recent_memories
            
            # Get daily brief for context
            daily_brief = await self.memory_client.get_daily_brief()
            self.context["daily_context"] = daily_brief
            
            logger.info(f"Loaded {len(recent_memories)} recent memories for agent {self.agent_id}")
            
        except Exception as e:
            logger.warning(f"Failed to load agent memories: {str(e)}")
            self.recent_memories = []
            self.context["recent_memories"] = []
            self.context["daily_context"] = {}
    
    async def remember(self, content: str, entity_type: str = "observation", 
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a memory/observation"""
        if not self.memory_initialized:
            logger.warning("Memory not initialized, skipping storage")
            return False
            
        try:
            enhanced_metadata = {
                "agent_id": self.agent_id,
                "agent_role": self.role,
                "personality": self.personality,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            result = await self.memory_client.store_memory(
                agent_id=self.agent_id,
                content=content,
                entity_type=entity_type
            )
            
            logger.info(f"Agent {self.agent_id} stored memory: {content[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            return False
    
    async def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search and recall relevant memories"""
        if not self.memory_initialized:
            return []
            
        try:
            memories = await self.memory_client.search_memories(
                query=query,
                limit=limit
            )
            
            logger.info(f"Agent {self.agent_id} recalled {len(memories)} memories for query: {query}")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to recall memories: {str(e)}")
            return []
    
    async def create_entity(self, name: str, entity_type: str, observations: List[str],
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new entity in memory"""
        if not self.memory_initialized:
            return False
            
        try:
            agent_context = {
                "created_by_agent": self.agent_id,
                "agent_role": self.role,
                "personality": self.personality,
                "expertise_domain": self.role,
                **(metadata or {})
            }
            
            result = await self.memory_client.store_entity(
                entity_name=name,
                entity_type=entity_type,
                observations=observations,
                agent_context=agent_context
            )
            
            logger.info(f"Agent {self.agent_id} created entity: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create entity: {str(e)}")
            return False
    
    def get_recent_memories_summary(self) -> str:
        """Get a summary of recent memories for context"""
        if not self.recent_memories:
            return "No recent memories available."
        
        summaries = []
        for memory in self.recent_memories[:3]:  # Top 3 recent memories
            entity_name = memory.get("entity_name", "Unknown")
            observations = memory.get("data", {}).get("observations", [])
            if observations:
                summaries.append(f"- {entity_name}: {observations[0][:100]}...")
        
        return "Recent context:\n" + "\n".join(summaries) if summaries else "No recent context available."
    
    async def handle_request_with_memory(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced request handling with memory integration"""
        
        # Get relevant memories for context
        if self.memory_initialized:
            relevant_memories = await self.recall(request, limit=3)
            context["relevant_memories"] = relevant_memories
            context["memory_summary"] = self.get_recent_memories_summary()
        
        # Process request with memory-enhanced context - call subclass implementation
        response = await self._handle_request_with_memory_context(request, context)
        
        # Store the interaction in memory
        if self.memory_initialized:
            await self.remember(
                content=f"User request: {request} | Agent response: {response.get('response', response.get('content', 'No content'))}",
                entity_type="conversation",
                metadata={"confidence": response.get("confidence", 0.5)}
            )
        
        return response
    
    async def _handle_request_with_memory_context(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default implementation - subclasses should override this"""
        return await self.handle_request(request, context)
    
    async def cleanup_memory(self):
        """Clean up memory resources"""
        try:
            # Store session summary
            if self.memory_initialized and self.conversation_history:
                session_summary = self._generate_session_summary()
                await self.remember(
                    content=session_summary,
                    entity_type="session_summary"
                )
            
            # Close memory client
            if self.memory_client:
                await self.memory_client.close()
            
            logger.info(f"Agent {self.agent_id} memory cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {str(e)}")
    
    def _generate_session_summary(self) -> str:
        """Generate a summary of the session"""
        conversation_count = len(self.conversation_history)
        memory_count = len(self.recent_memories)
        
        return f"Session completed for {self.role} agent {self.agent_id}. " \
               f"Processed {conversation_count} conversations. " \
               f"Accessed {memory_count} memories. " \
               f"Personality: {self.personality}."