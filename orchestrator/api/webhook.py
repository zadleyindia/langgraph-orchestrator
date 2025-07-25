"""
Webhook Handler for WhatsApp Integration
Handles incoming WhatsApp messages and routes them through the orchestrator
"""

import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from pydantic import BaseModel

from ..brain import PersonalAIBrain
from ..state import ConversationState

logger = logging.getLogger(__name__)

class WhatsAppMessage(BaseModel):
    """WhatsApp message model"""
    phone_number: str
    message: str
    message_type: str = "text"  # text, voice, image, document
    media_url: Optional[str] = None
    timestamp: Optional[str] = None
    context: Dict[str, Any] = {}

class WhatsAppResponse(BaseModel):
    """WhatsApp response model"""
    phone_number: str
    message: str
    message_type: str = "text"
    media_url: Optional[str] = None
    session_id: str
    context_updated: bool = False
    actions_taken: List[Dict[str, Any]] = []

class WebhookHandler:
    """
    Webhook Handler for WhatsApp Integration
    
    Handles:
    - WhatsApp message webhooks
    - Media message processing
    - Session management per phone number
    - Response formatting for WhatsApp
    """
    
    def __init__(self, brain: PersonalAIBrain):
        self.brain = brain
        self.active_sessions: Dict[str, str] = {}  # phone_number -> session_id
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
        
    async def handle_whatsapp_webhook(self, webhook_data: Dict[str, Any]) -> WhatsAppResponse:
        """
        Handle incoming WhatsApp webhook
        
        Args:
            webhook_data: Raw webhook data from WhatsApp
            
        Returns:
            WhatsApp response to send back
        """
        try:
            # Parse WhatsApp message
            message = self._parse_whatsapp_message(webhook_data)
            
            # Get or create session
            session_id = self._get_or_create_session(message.phone_number)
            
            # Process message based on type
            if message.message_type == "text":
                return await self._handle_text_message(message, session_id)
            elif message.message_type == "voice":
                return await self._handle_voice_message(message, session_id)
            elif message.message_type == "image":
                return await self._handle_image_message(message, session_id)
            elif message.message_type == "document":
                return await self._handle_document_message(message, session_id)
            else:
                return WhatsAppResponse(
                    phone_number=message.phone_number,
                    message=f"Sorry, I don't support {message.message_type} messages yet.",
                    session_id=session_id
                )
                
        except Exception as e:
            logger.error(f"WhatsApp webhook error: {e}")
            return WhatsAppResponse(
                phone_number=webhook_data.get("phone_number", "unknown"),
                message="I'm having trouble processing your message. Please try again.",
                session_id="error_session"
            )
    
    def _parse_whatsapp_message(self, webhook_data: Dict[str, Any]) -> WhatsAppMessage:
        """
        Parse WhatsApp webhook data into message object
        
        Args:
            webhook_data: Raw webhook data
            
        Returns:
            Parsed WhatsApp message
        """
        # This is a simplified parser - actual WhatsApp webhook format varies
        # You'll need to adjust based on your WhatsApp provider's format
        
        return WhatsAppMessage(
            phone_number=webhook_data.get("from", "unknown"),
            message=webhook_data.get("text", ""),
            message_type=webhook_data.get("type", "text"),
            media_url=webhook_data.get("media_url"),
            timestamp=webhook_data.get("timestamp"),
            context=webhook_data.get("context", {})
        )
    
    def _get_or_create_session(self, phone_number: str) -> str:
        """
        Get existing session or create new one for phone number
        
        Args:
            phone_number: WhatsApp phone number
            
        Returns:
            Session ID for this phone number
        """
        if phone_number not in self.active_sessions:
            session_id = f"whatsapp_{phone_number.replace('+', '')}"
            self.active_sessions[phone_number] = session_id
            self.session_contexts[session_id] = {
                "phone_number": phone_number,
                "created_at": "now",  # Use proper timestamp
                "message_count": 0
            }
        
        return self.active_sessions[phone_number]
    
    async def _handle_text_message(self, message: WhatsAppMessage, session_id: str) -> WhatsAppResponse:
        """
        Handle text message through brain orchestrator
        
        Args:
            message: WhatsApp text message
            session_id: Session ID
            
        Returns:
            WhatsApp response
        """
        # Update session context
        if session_id in self.session_contexts:
            self.session_contexts[session_id]["message_count"] += 1
        
        # Route through brain orchestrator
        brain_response = await self.brain.process_request(
            message=message.message,
            user_id=message.phone_number,
            interface="whatsapp",
            session_id=session_id,
            context={**message.context, "message_type": "text"}
        )
        
        return WhatsAppResponse(
            phone_number=message.phone_number,
            message=brain_response.get("response", ""),
            session_id=session_id,
            context_updated=brain_response.get("context_updated", False),
            actions_taken=brain_response.get("actions_taken", [])
        )
    
    async def _handle_voice_message(self, message: WhatsAppMessage, session_id: str) -> WhatsAppResponse:
        """
        Handle voice message (requires transcription)
        
        Args:
            message: WhatsApp voice message
            session_id: Session ID
            
        Returns:
            WhatsApp response
        """
        # For voice messages, you'd need to:
        # 1. Download audio from media_url
        # 2. Transcribe with Groq/OpenAI
        # 3. Process transcript through brain
        
        # Placeholder implementation
        voice_text = f"[Voice message received from {message.phone_number}]"
        
        brain_response = await self.brain.process_request(
            message=voice_text,
            user_id=message.phone_number,
            interface="whatsapp",
            session_id=session_id,
            context={**message.context, "message_type": "voice", "media_url": message.media_url}
        )
        
        return WhatsAppResponse(
            phone_number=message.phone_number,
            message=brain_response.get("response", "I heard your voice message. Let me process it..."),
            session_id=session_id,
            context_updated=brain_response.get("context_updated", False),
            actions_taken=brain_response.get("actions_taken", [])
        )
    
    async def _handle_image_message(self, message: WhatsAppMessage, session_id: str) -> WhatsAppResponse:
        """
        Handle image message (requires vision processing)
        
        Args:
            message: WhatsApp image message
            session_id: Session ID
            
        Returns:
            WhatsApp response
        """
        # For image messages, you'd need to:
        # 1. Download image from media_url
        # 2. Process with vision model
        # 3. Process description through brain
        
        # Placeholder implementation
        image_description = f"[Image received from {message.phone_number}]"
        
        brain_response = await self.brain.process_request(
            message=f"User sent an image: {image_description}",
            user_id=message.phone_number,
            interface="whatsapp",
            session_id=session_id,
            context={**message.context, "message_type": "image", "media_url": message.media_url}
        )
        
        return WhatsAppResponse(
            phone_number=message.phone_number,
            message=brain_response.get("response", "I can see your image. Let me analyze it..."),
            session_id=session_id,
            context_updated=brain_response.get("context_updated", False),
            actions_taken=brain_response.get("actions_taken", [])
        )
    
    async def _handle_document_message(self, message: WhatsAppMessage, session_id: str) -> WhatsAppResponse:
        """
        Handle document message (requires document processing)
        
        Args:
            message: WhatsApp document message
            session_id: Session ID
            
        Returns:
            WhatsApp response
        """
        # For document messages, you'd need to:
        # 1. Download document from media_url
        # 2. Extract text/content
        # 3. Process content through brain
        
        # Placeholder implementation
        doc_info = f"[Document received from {message.phone_number}]"
        
        brain_response = await self.brain.process_request(
            message=f"User sent a document: {doc_info}",
            user_id=message.phone_number,
            interface="whatsapp",
            session_id=session_id,
            context={**message.context, "message_type": "document", "media_url": message.media_url}
        )
        
        return WhatsAppResponse(
            phone_number=message.phone_number,
            message=brain_response.get("response", "I received your document. Let me process it..."),
            session_id=session_id,
            context_updated=brain_response.get("context_updated", False),
            actions_taken=brain_response.get("actions_taken", [])
        )
    
    async def send_whatsapp_message(self, response: WhatsAppResponse) -> bool:
        """
        Send message back to WhatsApp
        
        Args:
            response: WhatsApp response to send
            
        Returns:
            Success status
        """
        try:
            # This would integrate with your WhatsApp API provider
            # Examples: Twilio, WhatsApp Business API, etc.
            
            # Placeholder implementation
            logger.info(f"Sending WhatsApp message to {response.phone_number}: {response.message}")
            
            # You'd make HTTP request to WhatsApp API here
            # api_response = await whatsapp_client.send_message(
            #     to=response.phone_number,
            #     message=response.message,
            #     type=response.message_type
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return False
    
    async def get_webhook_status(self) -> Dict[str, Any]:
        """
        Get webhook status information
        
        Returns:
            Status information for webhook handler
        """
        return {
            "interface": "whatsapp",
            "active_sessions": len(self.active_sessions),
            "phone_numbers": list(self.active_sessions.keys()),
            "session_contexts": {
                session_id: {
                    "phone_number": context.get("phone_number"),
                    "message_count": context.get("message_count", 0),
                    "created_at": context.get("created_at")
                }
                for session_id, context in self.session_contexts.items()
            },
            "status": "operational"
        }
    
    async def clear_session(self, phone_number: str) -> bool:
        """
        Clear session for specific phone number
        
        Args:
            phone_number: Phone number to clear
            
        Returns:
            Success status
        """
        try:
            if phone_number in self.active_sessions:
                session_id = self.active_sessions[phone_number]
                del self.active_sessions[phone_number]
                
                if session_id in self.session_contexts:
                    del self.session_contexts[session_id]
                
                logger.info(f"WhatsApp session cleared for {phone_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error clearing WhatsApp session: {e}")
            return False