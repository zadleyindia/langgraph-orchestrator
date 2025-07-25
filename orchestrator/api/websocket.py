"""
WebSocket Handler for Real-time Communication
Supports streaming responses and real-time agent interactions
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..brain import PersonalAIBrain
from ..state import ConversationState

logger = logging.getLogger(__name__)

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str  # "text", "voice", "command", "status"
    content: str
    user_id: str = "mohit"
    session_id: Optional[str] = None
    interface: str = "websocket"
    context: Dict[str, Any] = {}

class WebSocketResponse(BaseModel):
    """WebSocket response model"""
    type: str  # "response", "status", "error", "stream"
    content: str
    session_id: str
    context_updated: bool = False
    actions_taken: List[Dict[str, Any]] = []

class WebSocketHandler:
    """
    WebSocket Handler for Real-time Communication
    
    Handles:
    - Real-time text and voice communication
    - Streaming agent responses
    - Multi-session management
    - Connection lifecycle management
    """
    
    def __init__(self, brain: PersonalAIBrain):
        self.brain = brain
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str = "mohit") -> str:
        """
        Handle new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
            
        Returns:
            Session ID for the connection
        """
        await websocket.accept()
        session_id = f"ws_{user_id}_{id(websocket)}"
        
        self.active_connections[session_id] = websocket
        self.session_contexts[session_id] = {
            "user_id": user_id,
            "connected_at": asyncio.get_event_loop().time(),
            "message_count": 0
        }
        
        logger.info(f"WebSocket connected: {session_id}")
        
        # Send welcome message
        await self.send_message(session_id, WebSocketResponse(
            type="status",
            content="Connected to Personal AI Brain",
            session_id=session_id
        ))
        
        return session_id
    
    async def disconnect(self, session_id: str):
        """
        Handle WebSocket disconnection
        
        Args:
            session_id: Session to disconnect
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
            
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, response: WebSocketResponse):
        """
        Send message to specific WebSocket session
        
        Args:
            session_id: Target session
            response: Response to send
        """
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(response.json())
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                await self.disconnect(session_id)
    
    async def broadcast_message(self, response: WebSocketResponse, exclude_session: Optional[str] = None):
        """
        Broadcast message to all connected sessions
        
        Args:
            response: Response to broadcast
            exclude_session: Session to exclude from broadcast
        """
        for session_id in list(self.active_connections.keys()):
            if session_id != exclude_session:
                await self.send_message(session_id, response)
    
    async def handle_message(self, session_id: str, message: WebSocketMessage) -> WebSocketResponse:
        """
        Process incoming WebSocket message
        
        Args:
            session_id: Source session
            message: Incoming message
            
        Returns:
            Response message
        """
        try:
            # Update session context
            if session_id in self.session_contexts:
                self.session_contexts[session_id]["message_count"] += 1
                self.session_contexts[session_id]["last_message"] = asyncio.get_event_loop().time()
            
            # Handle different message types
            if message.type == "text":
                return await self._handle_text_message(session_id, message)
            elif message.type == "voice":
                return await self._handle_voice_message(session_id, message)
            elif message.type == "command":
                return await self._handle_command_message(session_id, message)
            elif message.type == "status":
                return await self._handle_status_request(session_id, message)
            else:
                return WebSocketResponse(
                    type="error",
                    content=f"Unknown message type: {message.type}",
                    session_id=session_id
                )
                
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            return WebSocketResponse(
                type="error",
                content=f"Error processing message: {str(e)}",
                session_id=session_id
            )
    
    async def _handle_text_message(self, session_id: str, message: WebSocketMessage) -> WebSocketResponse:
        """Handle text message through brain orchestrator"""
        # Route through brain orchestrator
        brain_response = await self.brain.process_request(
            message=message.content,
            user_id=message.user_id,
            interface=message.interface,
            session_id=session_id,
            context=message.context
        )
        
        return WebSocketResponse(
            type="response",
            content=brain_response.get("response", ""),
            session_id=session_id,
            context_updated=brain_response.get("context_updated", False),
            actions_taken=brain_response.get("actions_taken", [])
        )
    
    async def _handle_voice_message(self, session_id: str, message: WebSocketMessage) -> WebSocketResponse:
        """Handle voice message (transcript) through brain orchestrator"""
        # Similar to text but with voice interface context
        brain_response = await self.brain.process_request(
            message=message.content,
            user_id=message.user_id,
            interface="voice",
            session_id=session_id,
            context={**message.context, "audio_input": True}
        )
        
        return WebSocketResponse(
            type="voice_response",
            content=brain_response.get("response", ""),
            session_id=session_id,
            context_updated=brain_response.get("context_updated", False),
            actions_taken=brain_response.get("actions_taken", [])
        )
    
    async def _handle_command_message(self, session_id: str, message: WebSocketMessage) -> WebSocketResponse:
        """Handle command message (system commands)"""
        command = message.content.lower()
        
        if command == "status":
            return await self._handle_status_request(session_id, message)
        elif command == "clear":
            # Clear session context
            if session_id in self.session_contexts:
                self.session_contexts[session_id]["message_count"] = 0
            return WebSocketResponse(
                type="status",
                content="Session context cleared",
                session_id=session_id
            )
        elif command == "agents":
            # List available agents
            return WebSocketResponse(
                type="status",
                content="Available agents: Personal Assistant (Primary), Data Analyst, HR Director, Dev Lead, Operations Manager",
                session_id=session_id
            )
        else:
            return WebSocketResponse(
                type="error",
                content=f"Unknown command: {command}",
                session_id=session_id
            )
    
    async def _handle_status_request(self, session_id: str, message: WebSocketMessage) -> WebSocketResponse:
        """Handle status request"""
        context = self.session_contexts.get(session_id, {})
        brain_status = await self.brain.get_status()
        
        status_info = {
            "session": {
                "id": session_id,
                "user_id": context.get("user_id", "unknown"),
                "message_count": context.get("message_count", 0),
                "connected_at": context.get("connected_at", 0)
            },
            "brain": brain_status,
            "websocket": {
                "active_connections": len(self.active_connections),
                "total_sessions": len(self.session_contexts)
            }
        }
        
        return WebSocketResponse(
            type="status",
            content=json.dumps(status_info, indent=2),
            session_id=session_id
        )
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str = "mohit"):
        """
        Main WebSocket connection handler
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        session_id = await self.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Parse message
                message = WebSocketMessage(**message_data)
                message.session_id = session_id
                
                # Process message
                response = await self.handle_message(session_id, message)
                
                # Send response
                await self.send_message(session_id, response)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket connection closed: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.disconnect(session_id)
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """
        Get WebSocket connection status
        
        Returns:
            Status information for all connections
        """
        return {
            "active_connections": len(self.active_connections),
            "sessions": {
                session_id: {
                    "user_id": context.get("user_id"),
                    "message_count": context.get("message_count", 0),
                    "connected_at": context.get("connected_at", 0)
                }
                for session_id, context in self.session_contexts.items()
            }
        }