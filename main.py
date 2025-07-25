"""
Personal AI Brain - LangGraph Orchestration Server
Coordinates between voice/text interfaces and MCP servers
"""

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os
from dotenv import load_dotenv

from orchestrator.brain import PersonalAIBrain
from orchestrator.state import ConversationState
from orchestrator.api.voice import VoiceInterface
from orchestrator.api.websocket import WebSocketHandler
from orchestrator.api.webhook import WebhookHandler

load_dotenv()

app = FastAPI(
    title="Personal AI Brain Orchestrator",
    description="LangGraph-based orchestration layer for MCP servers",
    version="1.0.0"
)

# Initialize the brain
brain = PersonalAIBrain()

# Initialize interface handlers
voice_interface = VoiceInterface(brain)
websocket_handler = WebSocketHandler(brain)
webhook_handler = WebhookHandler(brain)

class OrchestrationRequest(BaseModel):
    message: str
    user_id: str = "default"
    interface: str = "api"  # voice, whatsapp, web, api
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class OrchestrationResponse(BaseModel):
    response: str
    actions_taken: List[Dict[str, Any]]
    context_updated: bool
    session_id: str

@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: OrchestrationRequest):
    """Main orchestration endpoint"""
    try:
        result = await brain.process_request(
            message=request.message,
            user_id=request.user_id,
            interface=request.interface,
            session_id=request.session_id,
            context=request.context or {}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "langgraph-orchestrator"}

@app.get("/status")
async def get_status():
    """Get brain status and MCP server connectivity"""
    return await brain.get_status()

# Voice Interface Endpoints
@app.post("/voice/process")
async def process_voice_request(request: dict):
    """Process voice request from FastRTC"""
    try:
        from orchestrator.api.voice import VoiceRequest
        voice_request = VoiceRequest(**request)
        return await voice_interface.handle_voice_request(voice_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/status")
async def get_voice_status():
    """Get voice interface status"""
    return await voice_interface.get_voice_status()

# WebSocket Endpoints
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "mohit"):
    """WebSocket endpoint for real-time communication"""
    await websocket_handler.handle_websocket_connection(websocket, user_id)

@app.get("/ws/status")
async def get_websocket_status():
    """Get WebSocket connection status"""
    return await websocket_handler.get_connection_status()

# Webhook Endpoints
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: dict):
    """Handle WhatsApp webhook"""
    try:
        response = await webhook_handler.handle_whatsapp_webhook(request)
        # Optional: Send response back to WhatsApp
        await webhook_handler.send_whatsapp_message(response)
        return {"status": "success", "response": response.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/status")
async def get_webhook_status():
    """Get webhook handler status"""
    return await webhook_handler.get_webhook_status()

@app.post("/webhook/whatsapp/clear/{phone_number}")
async def clear_whatsapp_session(phone_number: str):
    """Clear WhatsApp session for specific phone number"""
    success = await webhook_handler.clear_session(phone_number)
    return {"status": "success" if success else "failed", "phone_number": phone_number}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )