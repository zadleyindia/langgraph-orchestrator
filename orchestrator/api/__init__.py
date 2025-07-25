"""
API Interface Modules for Personal AI Brain
Handles external communication channels: Voice, WebSocket, WhatsApp
"""

from .voice import VoiceInterface
from .websocket import WebSocketHandler
from .webhook import WebhookHandler

__all__ = ['VoiceInterface', 'WebSocketHandler', 'WebhookHandler']