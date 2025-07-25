"""
Memory Client - Interface to your conversation-persistence-mcp
"""

from typing import Dict, Any
from .supergateway_client import SupergatewayClient
from ..state import ConversationState

class MemoryClient:
    """Client for memory operations via your conversation-persistence-mcp"""
    
    def __init__(self, supergateway: SupergatewayClient = None):
        self.supergateway = supergateway or SupergatewayClient()
        self.server_name = "conversation-persistence-mcp"
    
    async def retrieve_context(self, state: ConversationState) -> ConversationState:
        """Retrieve relevant context from memory"""
        
        try:
            # Search for relevant context
            search_result = await self.supergateway.execute_mcp(
                self.server_name,
                "search_knowledge_graph",
                {
                    "query": state.current_message,
                    "user_id": state.user_id,
                    "limit": 5
                }
            )
            
            if search_result and not search_result.get("error"):
                state.memory_retrieved = search_result
                state.update_context("memory_context", search_result)
            
            # Get recent conversation history
            history_result = await self.supergateway.execute_mcp(
                self.server_name,
                "get_conversation_history",
                {
                    "user_id": state.user_id,
                    "session_id": state.session_id,
                    "limit": 10
                }
            )
            
            if history_result and not history_result.get("error"):
                state.update_context("conversation_history", history_result)
            
        except Exception as e:
            state.add_error(f"Memory retrieval failed: {str(e)}")
        
        return state
    
    async def store_context(self, state: ConversationState) -> ConversationState:
        """Store conversation context in memory"""
        
        try:
            # Store the current conversation
            store_result = await self.supergateway.execute_mcp(
                self.server_name,
                "store_conversation",
                {
                    "user_id": state.user_id,
                    "session_id": state.session_id,
                    "message": state.current_message,
                    "response": state.response,
                    "intent": state.intent,
                    "actions": state.actions_taken,
                    "context": state.context
                }
            )
            
            if store_result and store_result.get("error"):
                state.add_error(f"Memory storage failed: {store_result['error']}")
            else:
                state.update_context("memory_stored", True)
            
            # Extract and store entities/relationships
            if state.actions_taken:
                await self._store_entities(state)
            
        except Exception as e:
            state.add_error(f"Memory storage failed: {str(e)}")
        
        return state
    
    async def _store_entities(self, state: ConversationState):
        """Extract and store entities from the conversation"""
        
        try:
            entity_result = await self.supergateway.execute_mcp(
                self.server_name,
                "extract_entities",
                {
                    "text": state.current_message + " " + state.response,
                    "user_id": state.user_id,
                    "context": state.context
                }
            )
            
            if entity_result and not entity_result.get("error"):
                state.update_context("entities_extracted", entity_result)
            
        except Exception as e:
            # Don't fail the whole process for entity extraction
            pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check memory system health"""
        
        try:
            result = await self.supergateway.execute_mcp(
                self.server_name,
                "health_check",
                {}
            )
            
            if result and not result.get("error"):
                return {
                    "status": "healthy",
                    "server": self.server_name,
                    "details": result
                }
            else:
                return {
                    "status": "unhealthy",
                    "server": self.server_name,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "status": "unreachable",
                "server": self.server_name,
                "error": str(e)
            }