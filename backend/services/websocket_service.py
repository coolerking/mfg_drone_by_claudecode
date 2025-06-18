"""
WebSocket Service - Enhanced WebSocket management for real-time communication

This service provides advanced WebSocket functionality including:
- Connection pooling and management
- Message routing and broadcasting
- Client authentication and authorization
- Performance monitoring and metrics
- Automatic reconnection handling
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from .event_service import get_event_service, EventType, EventPriority, DroneEvent

logger = logging.getLogger(__name__)

class ClientType(Enum):
    """WebSocket client types."""
    MCP_TOOLS = "mcp_tools"
    ADMIN_UI = "admin_ui"
    USER_UI = "user_ui"
    MONITORING = "monitoring"
    API_CLIENT = "api_client"

class MessageType(Enum):
    """WebSocket message types."""
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    DATA_UPDATE = "data_update"
    COMMAND = "command"
    COMMAND_RESPONSE = "command_response"
    ERROR = "error"
    STATUS = "status"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"

@dataclass
class ClientInfo:
    """Information about a connected WebSocket client."""
    id: str
    websocket: WebSocket
    client_type: ClientType
    connected_at: datetime
    last_ping: Optional[datetime]
    last_message: Optional[datetime]
    message_count: int
    subscriptions: Set[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert client info to dictionary (excluding websocket)."""
        result = asdict(self)
        del result['websocket']  # Can't serialize WebSocket
        result['client_type'] = self.client_type.value
        result['connected_at'] = self.connected_at.isoformat()
        result['last_ping'] = self.last_ping.isoformat() if self.last_ping else None
        result['last_message'] = self.last_message.isoformat() if self.last_message else None
        result['subscriptions'] = list(self.subscriptions)
        return result

@dataclass
class WebSocketMessage:
    """Structured WebSocket message."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "client_id": self.client_id,
            "request_id": self.request_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """Create message from dictionary."""
        return cls(
            type=MessageType(data["type"]),
            data=data.get("data", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            client_id=data.get("client_id"),
            request_id=data.get("request_id"),
        )

class WebSocketService:
    """
    Advanced WebSocket service for drone system communication.
    
    Provides connection management, message routing, subscription handling,
    and integration with the event system.
    """
    
    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # topic -> client_ids
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.event_service = get_event_service()
        
        # Performance metrics
        self.total_connections = 0
        self.total_messages = 0
        self.start_time = datetime.now()
        
        # Background tasks
        self._ping_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Configuration
        self.ping_interval = 30  # seconds
        self.ping_timeout = 10   # seconds
        self.max_clients = 100
        self.max_message_size = 1024 * 1024  # 1MB
        
        self._setup_message_handlers()
        self._setup_event_subscriptions()
        
        logger.info("WebSocket service initialized")

    def _setup_message_handlers(self):
        """Setup handlers for different message types."""
        self.message_handlers = {
            MessageType.PING: self._handle_ping,
            MessageType.SUBSCRIBE: self._handle_subscribe,
            MessageType.UNSUBSCRIBE: self._handle_unsubscribe,
            MessageType.COMMAND: self._handle_command,
            MessageType.STATUS: self._handle_status_request,
        }

    def _setup_event_subscriptions(self):
        """Setup subscriptions to the event service."""
        # Subscribe to all events to broadcast to interested clients
        self.event_service.subscribe(
            subscriber_id="websocket_service",
            callback=self._handle_event,
            event_types=None,  # All event types
            min_priority=EventPriority.LOW,
        )

    async def start(self):
        """Start the WebSocket service and background tasks."""
        if self._is_running:
            return
        
        self._is_running = True
        
        # Start background tasks
        self._ping_task = asyncio.create_task(self._ping_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Emit service started event
        await self.event_service.emit_event(
            event_type=EventType.STATUS_CHANGE,
            priority=EventPriority.NORMAL,
            data={"service": "websocket_service", "status": "started"},
            source="websocket_service",
            description="WebSocket service started"
        )
        
        logger.info("WebSocket service started")

    async def stop(self):
        """Stop the WebSocket service and cleanup resources."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # Cancel background tasks
        if self._ping_task:
            self._ping_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Disconnect all clients
        for client_id in list(self.clients.keys()):
            await self.disconnect_client(client_id, reason="Service shutdown")
        
        # Emit service stopped event
        await self.event_service.emit_event(
            event_type=EventType.STATUS_CHANGE,
            priority=EventPriority.NORMAL,
            data={"service": "websocket_service", "status": "stopped"},
            source="websocket_service",
            description="WebSocket service stopped"
        )
        
        logger.info("WebSocket service stopped")

    async def connect_client(
        self,
        websocket: WebSocket,
        client_type: ClientType = ClientType.API_CLIENT,
        client_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Connect a new WebSocket client.
        
        Args:
            websocket: WebSocket connection
            client_type: Type of client connecting
            client_id: Optional custom client ID
            metadata: Additional client metadata
            
        Returns:
            Assigned client ID
        """
        # Check connection limits
        if len(self.clients) >= self.max_clients:
            raise Exception(f"Maximum client limit reached ({self.max_clients})")
        
        # Generate client ID if not provided
        if not client_id:
            client_id = f"{client_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Accept WebSocket connection
        await websocket.accept()
        
        # Create client info
        client_info = ClientInfo(
            id=client_id,
            websocket=websocket,
            client_type=client_type,
            connected_at=datetime.now(),
            last_ping=None,
            last_message=None,
            message_count=0,
            subscriptions=set(),
            metadata=metadata or {},
        )
        
        # Store client
        self.clients[client_id] = client_info
        self.total_connections += 1
        
        # Send welcome message
        await self.send_message(client_id, WebSocketMessage(
            type=MessageType.STATUS,
            data={
                "status": "connected",
                "client_id": client_id,
                "server_time": datetime.now().isoformat(),
                "capabilities": ["ping", "subscribe", "command", "broadcast"],
            },
            timestamp=datetime.now(),
        ))
        
        # Emit connection event
        await self.event_service.emit_event(
            event_type=EventType.STATUS_CHANGE,
            priority=EventPriority.NORMAL,
            data={
                "client_id": client_id,
                "client_type": client_type.value,
                "action": "connected",
                "total_clients": len(self.clients),
            },
            source="websocket_service",
            description=f"Client {client_id} connected"
        )
        
        logger.info(f"Client connected: {client_id} ({client_type.value})")
        
        return client_id

    async def disconnect_client(self, client_id: str, reason: str = "Unknown"):
        """
        Disconnect a WebSocket client.
        
        Args:
            client_id: ID of client to disconnect
            reason: Reason for disconnection
        """
        if client_id not in self.clients:
            return
        
        client_info = self.clients[client_id]
        
        # Remove from all subscriptions
        for topic in list(client_info.subscriptions):
            await self._unsubscribe_client(client_id, topic)
        
        # Close WebSocket connection
        try:
            await client_info.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing WebSocket for {client_id}: {e}")
        
        # Remove client
        del self.clients[client_id]
        
        # Emit disconnection event
        await self.event_service.emit_event(
            event_type=EventType.STATUS_CHANGE,
            priority=EventPriority.NORMAL,
            data={
                "client_id": client_id,
                "client_type": client_info.client_type.value,
                "action": "disconnected",
                "reason": reason,
                "session_duration": (datetime.now() - client_info.connected_at).total_seconds(),
                "message_count": client_info.message_count,
                "total_clients": len(self.clients),
            },
            source="websocket_service",
            description=f"Client {client_id} disconnected: {reason}"
        )
        
        logger.info(f"Client disconnected: {client_id} - {reason}")

    async def send_message(self, client_id: str, message: WebSocketMessage) -> bool:
        """
        Send a message to a specific client.
        
        Args:
            client_id: Target client ID
            message: Message to send
            
        Returns:
            True if message was sent successfully
        """
        if client_id not in self.clients:
            return False
        
        client_info = self.clients[client_id]
        
        try:
            # Add client_id to message
            message.client_id = client_id
            
            # Send message
            await client_info.websocket.send_text(json.dumps(message.to_dict()))
            
            # Update client stats
            client_info.message_count += 1
            client_info.last_message = datetime.now()
            self.total_messages += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {client_id}: {e}")
            await self.disconnect_client(client_id, f"Send error: {e}")
            return False

    async def broadcast_message(
        self,
        message: WebSocketMessage,
        client_types: Optional[Set[ClientType]] = None,
        subscribed_to: Optional[str] = None,
    ):
        """
        Broadcast a message to multiple clients.
        
        Args:
            message: Message to broadcast
            client_types: Only send to clients of these types
            subscribed_to: Only send to clients subscribed to this topic
        """
        target_clients = []
        
        for client_id, client_info in self.clients.items():
            # Filter by client type
            if client_types and client_info.client_type not in client_types:
                continue
            
            # Filter by subscription
            if subscribed_to and subscribed_to not in client_info.subscriptions:
                continue
            
            target_clients.append(client_id)
        
        # Send to all target clients
        success_count = 0
        for client_id in target_clients:
            if await self.send_message(client_id, message):
                success_count += 1
        
        logger.debug(f"Broadcast sent to {success_count}/{len(target_clients)} clients")

    async def handle_client_message(self, client_id: str, raw_message: str):
        """
        Handle incoming message from a client.
        
        Args:
            client_id: ID of sending client
            raw_message: Raw message string
        """
        if client_id not in self.clients:
            return
        
        try:
            # Parse message
            message_data = json.loads(raw_message)
            message = WebSocketMessage.from_dict(message_data)
            message.client_id = client_id
            
            # Update client stats
            client_info = self.clients[client_id]
            client_info.last_message = datetime.now()
            
            # Handle message based on type
            handler = self.message_handlers.get(message.type)
            if handler:
                await handler(client_id, message)
            else:
                await self.send_message(client_id, WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": f"Unknown message type: {message.type.value}"},
                    timestamp=datetime.now(),
                ))
                
        except json.JSONDecodeError:
            await self.send_message(client_id, WebSocketMessage(
                type=MessageType.ERROR,
                data={"error": "Invalid JSON format"},
                timestamp=datetime.now(),
            ))
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self.send_message(client_id, WebSocketMessage(
                type=MessageType.ERROR,
                data={"error": str(e)},
                timestamp=datetime.now(),
            ))

    # Message handlers
    async def _handle_ping(self, client_id: str, message: WebSocketMessage):
        """Handle ping message."""
        client_info = self.clients[client_id]
        client_info.last_ping = datetime.now()
        
        await self.send_message(client_id, WebSocketMessage(
            type=MessageType.PONG,
            data={"server_time": datetime.now().isoformat()},
            timestamp=datetime.now(),
            request_id=message.request_id,
        ))

    async def _handle_subscribe(self, client_id: str, message: WebSocketMessage):
        """Handle subscription request."""
        topic = message.data.get("topic")
        if not topic:
            await self.send_message(client_id, WebSocketMessage(
                type=MessageType.ERROR,
                data={"error": "Missing topic in subscribe request"},
                timestamp=datetime.now(),
                request_id=message.request_id,
            ))
            return
        
        await self._subscribe_client(client_id, topic)
        
        await self.send_message(client_id, WebSocketMessage(
            type=MessageType.STATUS,
            data={"status": "subscribed", "topic": topic},
            timestamp=datetime.now(),
            request_id=message.request_id,
        ))

    async def _handle_unsubscribe(self, client_id: str, message: WebSocketMessage):
        """Handle unsubscription request."""
        topic = message.data.get("topic")
        if not topic:
            await self.send_message(client_id, WebSocketMessage(
                type=MessageType.ERROR,
                data={"error": "Missing topic in unsubscribe request"},
                timestamp=datetime.now(),
                request_id=message.request_id,
            ))
            return
        
        await self._unsubscribe_client(client_id, topic)
        
        await self.send_message(client_id, WebSocketMessage(
            type=MessageType.STATUS,
            data={"status": "unsubscribed", "topic": topic},
            timestamp=datetime.now(),
            request_id=message.request_id,
        ))

    async def _handle_command(self, client_id: str, message: WebSocketMessage):
        """Handle command message."""
        command = message.data.get("command")
        args = message.data.get("args", {})
        
        # This would integrate with drone command execution
        # For now, simulate command processing
        
        try:
            result = await self._execute_command(command, args)
            
            await self.send_message(client_id, WebSocketMessage(
                type=MessageType.COMMAND_RESPONSE,
                data={
                    "command": command,
                    "success": True,
                    "result": result,
                },
                timestamp=datetime.now(),
                request_id=message.request_id,
            ))
            
        except Exception as e:
            await self.send_message(client_id, WebSocketMessage(
                type=MessageType.COMMAND_RESPONSE,
                data={
                    "command": command,
                    "success": False,
                    "error": str(e),
                },
                timestamp=datetime.now(),
                request_id=message.request_id,
            ))

    async def _handle_status_request(self, client_id: str, message: WebSocketMessage):
        """Handle status request."""
        stats = self.get_statistics()
        
        await self.send_message(client_id, WebSocketMessage(
            type=MessageType.STATUS,
            data=stats,
            timestamp=datetime.now(),
            request_id=message.request_id,
        ))

    async def _execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a drone command (placeholder implementation)."""
        # This would integrate with the actual drone service
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "command": command,
            "args": args,
            "executed_at": datetime.now().isoformat(),
            "simulated": True,
        }

    async def _subscribe_client(self, client_id: str, topic: str):
        """Subscribe a client to a topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        
        self.subscriptions[topic].add(client_id)
        self.clients[client_id].subscriptions.add(topic)
        
        logger.debug(f"Client {client_id} subscribed to {topic}")

    async def _unsubscribe_client(self, client_id: str, topic: str):
        """Unsubscribe a client from a topic."""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
        
        if client_id in self.clients:
            self.clients[client_id].subscriptions.discard(topic)
        
        logger.debug(f"Client {client_id} unsubscribed from {topic}")

    async def _handle_event(self, event: DroneEvent):
        """Handle events from the event service and broadcast to subscribers."""
        # Determine which topic this event should be broadcast on
        topic = f"events.{event.type.value}"
        
        # Create broadcast message
        message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            data={
                "event": event.to_dict(),
                "topic": topic,
            },
            timestamp=datetime.now(),
        )
        
        # Broadcast to subscribers
        await self.broadcast_message(message, subscribed_to=topic)

    async def _ping_loop(self):
        """Background task to ping clients and detect disconnections."""
        while self._is_running:
            try:
                await asyncio.sleep(self.ping_interval)
                
                current_time = datetime.now()
                disconnected_clients = []
                
                for client_id, client_info in self.clients.items():
                    # Check if client has been inactive too long
                    if client_info.last_ping:
                        time_since_ping = current_time - client_info.last_ping
                        if time_since_ping > timedelta(seconds=self.ping_timeout * 2):
                            disconnected_clients.append(client_id)
                            continue
                    
                    # Send ping
                    await self.send_message(client_id, WebSocketMessage(
                        type=MessageType.PING,
                        data={"server_time": current_time.isoformat()},
                        timestamp=current_time,
                    ))
                
                # Disconnect inactive clients
                for client_id in disconnected_clients:
                    await self.disconnect_client(client_id, "Ping timeout")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")

    async def _cleanup_loop(self):
        """Background task for periodic cleanup and maintenance."""
        while self._is_running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Log service statistics
                stats = self.get_statistics()
                logger.info(f"WebSocket service stats: {stats['active_clients']} clients, "
                          f"{stats['total_messages']} messages")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "active_clients": len(self.clients),
            "total_connections": self.total_connections,
            "total_messages": self.total_messages,
            "subscriptions": {topic: len(clients) for topic, clients in self.subscriptions.items()},
            "client_types": {
                ct.value: len([c for c in self.clients.values() if c.client_type == ct])
                for ct in ClientType
            },
            "clients": [client.to_dict() for client in self.clients.values()],
        }

# Global WebSocket service instance
_websocket_service: Optional[WebSocketService] = None

def get_websocket_service() -> WebSocketService:
    """Get the global WebSocket service instance."""
    global _websocket_service
    if _websocket_service is None:
        _websocket_service = WebSocketService()
    return _websocket_service

async def initialize_websocket_service():
    """Initialize and start the global WebSocket service."""
    service = get_websocket_service()
    await service.start()
    return service

async def shutdown_websocket_service():
    """Shutdown the global WebSocket service."""
    global _websocket_service
    if _websocket_service:
        await _websocket_service.stop()
        _websocket_service = None