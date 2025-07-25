"""
Conversation state management for LangGraph workflows
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class ConversationState(BaseModel):
    """State object passed through LangGraph nodes"""
    
    # Core conversation data
    user_id: str
    session_id: str
    interface: str  # voice, whatsapp, web, api
    
    # Message history
    messages: List[Dict[str, Any]] = []
    current_message: str = ""
    
    # Intent and planning
    intent: Optional[str] = None
    plan: List[str] = []
    current_step: int = 0
    
    # Tool execution
    tools_to_use: List[str] = []
    tool_results: Dict[str, Any] = {}
    actions_taken: List[Dict[str, Any]] = []
    
    # Context and memory
    context: Dict[str, Any] = {}
    memory_retrieved: Dict[str, Any] = {}
    
    # Response generation
    response: str = ""
    response_type: str = "text"  # text, voice, rich
    
    # Error handling
    errors: List[str] = []
    retry_count: int = 0
    
    # Timestamps
    start_time: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_updated = datetime.now()
    
    def add_action(self, tool: str, action: str, result: Any, success: bool = True):
        """Record an action taken during orchestration"""
        self.actions_taken.append({
            "tool": tool,
            "action": action,
            "result": result,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        self.last_updated = datetime.now()
    
    def add_error(self, error: str):
        """Add an error to the state"""
        self.errors.append(error)
        self.last_updated = datetime.now()
    
    def update_context(self, key: str, value: Any):
        """Update context with new information"""
        self.context[key] = value
        self.last_updated = datetime.now()
    
    def is_complete(self) -> bool:
        """Check if the workflow is complete"""
        return len(self.plan) > 0 and self.current_step >= len(self.plan)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "interface": self.interface,
            "intent": self.intent,
            "progress": f"{self.current_step}/{len(self.plan)}",
            "tools_used": list(self.tool_results.keys()),
            "actions_count": len(self.actions_taken),
            "errors_count": len(self.errors),
            "duration": (self.last_updated - self.start_time).total_seconds()
        }