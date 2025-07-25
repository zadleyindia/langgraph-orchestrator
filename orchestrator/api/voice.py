"""
Voice Interface Module for FastRTC Integration
Handles voice input/output with the Personal AI Brain orchestrator
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..brain import PersonalAIBrain
from ..state import ConversationState

logger = logging.getLogger(__name__)

class VoiceRequest(BaseModel):
    """Voice request model"""
    audio_data: Optional[bytes] = None
    transcript: Optional[str] = None
    user_id: str = "mohit"
    session_id: Optional[str] = None
    interface: str = "voice"
    context: Dict[str, Any] = {}

class VoiceResponse(BaseModel):
    """Voice response model"""
    response: str
    audio_data: Optional[bytes] = None
    session_id: str
    context_updated: bool = False
    actions_taken: list = []

class VoiceInterface:
    """
    Voice Interface for FastRTC Integration
    
    Handles:
    - Audio transcription processing
    - Agent routing for voice requests
    - Audio response generation
    - Real-time voice communication
    """
    
    def __init__(self, brain: PersonalAIBrain):
        self.brain = brain
        self.active_sessions = {}
        
    async def handle_voice_request(self, request: VoiceRequest) -> VoiceResponse:
        """
        Process voice request through orchestrator
        
        Args:
            request: Voice request with transcript and context
            
        Returns:
            VoiceResponse with text and audio data
        """
        try:
            # Use transcript from FastRTC
            if not request.transcript:
                raise ValueError("No transcript provided")
            
            logger.info(f"Processing voice request: {request.transcript[:100]}...")
            
            # Route through brain orchestrator
            brain_response = await self.brain.process_request(
                message=request.transcript,
                user_id=request.user_id,
                interface=request.interface,
                session_id=request.session_id,
                context=request.context
            )
            
            # Return structured response
            return VoiceResponse(
                response=brain_response.get("response", ""),
                session_id=brain_response.get("session_id", ""),
                context_updated=brain_response.get("context_updated", False),
                actions_taken=brain_response.get("actions_taken", [])
            )
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return VoiceResponse(
                response="I'm having trouble processing your voice request. Please try again.",
                session_id=request.session_id or "error_session",
                context_updated=False,
                actions_taken=[]
            )
    
    async def handle_websocket_voice(self, websocket: WebSocket):
        """
        Handle WebSocket voice communication for real-time interaction
        
        Args:
            websocket: WebSocket connection from FastRTC
        """
        await websocket.accept()
        session_id = f"voice_ws_{id(websocket)}"
        self.active_sessions[session_id] = websocket
        
        try:
            logger.info(f"Voice WebSocket connected: {session_id}")
            
            while True:
                # Receive message from FastRTC
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Create voice request
                voice_request = VoiceRequest(
                    transcript=message_data.get("transcript"),
                    user_id=message_data.get("user_id", "mohit"),
                    session_id=session_id,
                    interface="voice_websocket",
                    context=message_data.get("context", {})
                )
                
                # Process through orchestrator
                response = await self.handle_voice_request(voice_request)
                
                # Send response back to FastRTC
                await websocket.send_text(json.dumps({
                    "type": "voice_response",
                    "response": response.response,
                    "session_id": response.session_id,
                    "context_updated": response.context_updated,
                    "actions_taken": response.actions_taken
                }))
                
        except WebSocketDisconnect:
            logger.info(f"Voice WebSocket disconnected: {session_id}")
        except Exception as e:
            logger.error(f"Voice WebSocket error: {e}")
        finally:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def get_voice_status(self) -> Dict[str, Any]:
        """
        Get voice interface status
        
        Returns:
            Status information for voice interface
        """
        return {
            "interface": "voice",
            "active_sessions": len(self.active_sessions),
            "session_ids": list(self.active_sessions.keys()),
            "status": "operational"
        }
    
    async def close_voice_session(self, session_id: str):
        """
        Close specific voice session
        
        Args:
            session_id: Session to close
        """
        if session_id in self.active_sessions:
            websocket = self.active_sessions[session_id]
            await websocket.close()
            del self.active_sessions[session_id]
            logger.info(f"Voice session closed: {session_id}")