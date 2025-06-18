"""
Event Service - Real-time event handling and notification system

This service manages real-time events for drone operations, including:
- Status change notifications
- Sensor data updates
- Alert and warning systems
- Event logging and history
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from dataclasses import dataclass, asdict
from collections import deque

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types for drone operations."""
    STATUS_CHANGE = "status_change"
    SENSOR_UPDATE = "sensor_update"
    BATTERY_WARNING = "battery_warning"
    TEMPERATURE_WARNING = "temperature_warning"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_RESTORED = "connection_restored"
    FLIGHT_MODE_CHANGE = "flight_mode_change"
    EMERGENCY_TRIGGERED = "emergency_triggered"
    COMMAND_EXECUTED = "command_executed"
    ERROR_OCCURRED = "error_occurred"
    GEOFENCE_VIOLATION = "geofence_violation"
    LOW_SIGNAL = "low_signal"
    MISSION_STARTED = "mission_started"
    MISSION_COMPLETED = "mission_completed"
    VIDEO_STREAM_STARTED = "video_stream_started"
    VIDEO_STREAM_STOPPED = "video_stream_stopped"

class EventPriority(Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class DroneEvent:
    """Represents a drone event with metadata."""
    id: str
    type: EventType
    priority: EventPriority
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    description: str
    acknowledged: bool = False
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        result = asdict(self)
        result['type'] = self.type.value
        result['priority'] = self.priority.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.expires_at:
            result['expires_at'] = self.expires_at.isoformat()
        return result

    def is_expired(self) -> bool:
        """Check if event has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

class EventSubscription:
    """Represents an event subscription with filtering."""
    
    def __init__(
        self,
        subscriber_id: str,
        callback: Callable[[DroneEvent], None],
        event_types: Optional[Set[EventType]] = None,
        min_priority: Optional[EventPriority] = None,
        source_filter: Optional[str] = None,
    ):
        self.subscriber_id = subscriber_id
        self.callback = callback
        self.event_types = event_types or set(EventType)
        self.min_priority = min_priority or EventPriority.LOW
        self.source_filter = source_filter
        self.created_at = datetime.now()
        self.last_event_at: Optional[datetime] = None
        self.event_count = 0

    def matches(self, event: DroneEvent) -> bool:
        """Check if event matches subscription criteria."""
        # Check event type
        if event.type not in self.event_types:
            return False
        
        # Check priority
        priority_levels = {
            EventPriority.LOW: 0,
            EventPriority.NORMAL: 1,
            EventPriority.HIGH: 2,
            EventPriority.CRITICAL: 3,
            EventPriority.EMERGENCY: 4,
        }
        
        min_level = priority_levels[self.min_priority]
        event_level = priority_levels[event.priority]
        
        if event_level < min_level:
            return False
        
        # Check source filter
        if self.source_filter and self.source_filter not in event.source:
            return False
        
        return True

class EventService:
    """
    Centralized event management service for drone operations.
    
    Handles event creation, distribution, filtering, and history management.
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_history: deque[DroneEvent] = deque(maxlen=max_history_size)
        self.active_events: Dict[str, DroneEvent] = {}
        self.event_counters: Dict[EventType, int] = {event_type: 0 for event_type in EventType}
        self.service_start_time = datetime.now()
        
        # Background task for cleanup
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        logger.info(f"Event service initialized with history size: {max_history_size}")

    async def start(self):
        """Start the event service and background tasks."""
        if self._is_running:
            return
        
        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Send service started event
        await self.emit_event(
            event_type=EventType.STATUS_CHANGE,
            priority=EventPriority.NORMAL,
            data={"service": "event_service", "status": "started"},
            source="event_service",
            description="Event service started successfully"
        )
        
        logger.info("Event service started")

    async def stop(self):
        """Stop the event service and cleanup resources."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Send service stopped event
        await self.emit_event(
            event_type=EventType.STATUS_CHANGE,
            priority=EventPriority.NORMAL,
            data={"service": "event_service", "status": "stopped"},
            source="event_service",
            description="Event service stopped"
        )
        
        logger.info("Event service stopped")

    async def emit_event(
        self,
        event_type: EventType,
        priority: EventPriority,
        data: Dict[str, Any],
        source: str,
        description: str,
        expires_in: Optional[timedelta] = None,
    ) -> DroneEvent:
        """
        Emit a new event to all matching subscribers.
        
        Args:
            event_type: Type of event
            priority: Event priority level
            data: Event data payload
            source: Source component that generated the event
            description: Human-readable event description
            expires_in: Optional expiration time delta
            
        Returns:
            The created DroneEvent
        """
        # Generate unique event ID
        event_id = f"{event_type.value}_{int(datetime.now().timestamp() * 1000)}"
        
        # Calculate expiration time
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + expires_in
        
        # Create event
        event = DroneEvent(
            id=event_id,
            type=event_type,
            priority=priority,
            timestamp=datetime.now(),
            data=data,
            source=source,
            description=description,
            expires_at=expires_at,
        )
        
        # Add to history and active events
        self.event_history.append(event)
        self.active_events[event_id] = event
        self.event_counters[event_type] += 1
        
        # Distribute to subscribers
        await self._distribute_event(event)
        
        logger.info(f"Event emitted: {event_type.value} from {source}")
        logger.debug(f"Event details: {event.to_dict()}")
        
        return event

    async def _distribute_event(self, event: DroneEvent):
        """Distribute event to all matching subscribers."""
        distributed_count = 0
        
        for subscription in self.subscriptions.values():
            if subscription.matches(event):
                try:
                    # Call subscriber callback
                    if asyncio.iscoroutinefunction(subscription.callback):
                        await subscription.callback(event)
                    else:
                        subscription.callback(event)
                    
                    # Update subscription stats
                    subscription.last_event_at = datetime.now()
                    subscription.event_count += 1
                    distributed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error calling subscriber {subscription.subscriber_id}: {e}")
        
        logger.debug(f"Event distributed to {distributed_count} subscribers")

    def subscribe(
        self,
        subscriber_id: str,
        callback: Callable[[DroneEvent], None],
        event_types: Optional[Set[EventType]] = None,
        min_priority: Optional[EventPriority] = None,
        source_filter: Optional[str] = None,
    ) -> str:
        """
        Subscribe to events with optional filtering.
        
        Args:
            subscriber_id: Unique identifier for subscriber
            callback: Function to call when matching events occur
            event_types: Set of event types to subscribe to (all if None)
            min_priority: Minimum priority level to receive
            source_filter: Filter events by source (substring match)
            
        Returns:
            Subscription ID
        """
        subscription = EventSubscription(
            subscriber_id=subscriber_id,
            callback=callback,
            event_types=event_types,
            min_priority=min_priority,
            source_filter=source_filter,
        )
        
        self.subscriptions[subscriber_id] = subscription
        
        logger.info(f"New subscription: {subscriber_id}")
        logger.debug(f"Subscription details: types={event_types}, priority={min_priority}, source={source_filter}")
        
        return subscriber_id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscriber_id: Subscriber ID to remove
            
        Returns:
            True if subscription was found and removed
        """
        if subscriber_id in self.subscriptions:
            del self.subscriptions[subscriber_id]
            logger.info(f"Unsubscribed: {subscriber_id}")
            return True
        return False

    def get_event_history(
        self,
        event_types: Optional[Set[EventType]] = None,
        min_priority: Optional[EventPriority] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[DroneEvent]:
        """
        Get filtered event history.
        
        Args:
            event_types: Filter by event types
            min_priority: Minimum priority level
            since: Only events after this timestamp
            limit: Maximum number of events to return
            
        Returns:
            List of matching events (newest first)
        """
        events = list(self.event_history)
        events.reverse()  # Newest first
        
        # Apply filters
        filtered_events = []
        for event in events:
            # Check event type
            if event_types and event.type not in event_types:
                continue
            
            # Check priority
            if min_priority:
                priority_levels = {
                    EventPriority.LOW: 0,
                    EventPriority.NORMAL: 1,
                    EventPriority.HIGH: 2,
                    EventPriority.CRITICAL: 3,
                    EventPriority.EMERGENCY: 4,
                }
                if priority_levels[event.priority] < priority_levels[min_priority]:
                    continue
            
            # Check timestamp
            if since and event.timestamp < since:
                continue
            
            filtered_events.append(event)
            
            # Apply limit
            if limit and len(filtered_events) >= limit:
                break
        
        return filtered_events

    def get_active_events(self, priority_filter: Optional[EventPriority] = None) -> List[DroneEvent]:
        """
        Get currently active (non-expired, unacknowledged) events.
        
        Args:
            priority_filter: Minimum priority level
            
        Returns:
            List of active events
        """
        active = []
        
        for event in self.active_events.values():
            # Skip expired or acknowledged events
            if event.is_expired() or event.acknowledged:
                continue
            
            # Apply priority filter
            if priority_filter:
                priority_levels = {
                    EventPriority.LOW: 0,
                    EventPriority.NORMAL: 1,
                    EventPriority.HIGH: 2,
                    EventPriority.CRITICAL: 3,
                    EventPriority.EMERGENCY: 4,
                }
                if priority_levels[event.priority] < priority_levels[priority_filter]:
                    continue
            
            active.append(event)
        
        # Sort by priority (highest first), then by timestamp (newest first)
        priority_order = {p: i for i, p in enumerate([
            EventPriority.EMERGENCY, EventPriority.CRITICAL, EventPriority.HIGH,
            EventPriority.NORMAL, EventPriority.LOW
        ])}
        
        active.sort(key=lambda e: (priority_order[e.priority], -e.timestamp.timestamp()))
        
        return active

    def acknowledge_event(self, event_id: str) -> bool:
        """
        Acknowledge an event to mark it as handled.
        
        Args:
            event_id: ID of event to acknowledge
            
        Returns:
            True if event was found and acknowledged
        """
        if event_id in self.active_events:
            self.active_events[event_id].acknowledged = True
            logger.info(f"Event acknowledged: {event_id}")
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get event service statistics.
        
        Returns:
            Dictionary with service statistics
        """
        uptime = datetime.now() - self.service_start_time
        
        # Calculate event rates
        total_events = sum(self.event_counters.values())
        events_per_minute = total_events / max(uptime.total_seconds() / 60, 1)
        
        # Get subscription stats
        subscription_stats = {
            sub_id: {
                "event_count": sub.event_count,
                "last_event": sub.last_event_at.isoformat() if sub.last_event_at else None,
                "uptime": (datetime.now() - sub.created_at).total_seconds(),
            }
            for sub_id, sub in self.subscriptions.items()
        }
        
        return {
            "service_uptime": uptime.total_seconds(),
            "total_events": total_events,
            "events_per_minute": round(events_per_minute, 2),
            "active_events": len([e for e in self.active_events.values() 
                                if not e.is_expired() and not e.acknowledged]),
            "event_history_size": len(self.event_history),
            "subscribers": len(self.subscriptions),
            "event_counters": {et.value: count for et, count in self.event_counters.items()},
            "subscriptions": subscription_stats,
        }

    async def _cleanup_loop(self):
        """Background task to cleanup expired events and maintain system health."""
        while self._is_running:
            try:
                await asyncio.sleep(60)  # Run cleanup every minute
                
                # Remove expired events from active events
                expired_event_ids = [
                    event_id for event_id, event in self.active_events.items()
                    if event.is_expired()
                ]
                
                for event_id in expired_event_ids:
                    del self.active_events[event_id]
                
                if expired_event_ids:
                    logger.debug(f"Cleaned up {len(expired_event_ids)} expired events")
                
                # Log service health
                stats = self.get_statistics()
                logger.debug(f"Event service stats: {stats['active_events']} active, "
                           f"{stats['total_events']} total, {stats['subscribers']} subscribers")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

# Global event service instance
_event_service: Optional[EventService] = None

def get_event_service() -> EventService:
    """Get the global event service instance."""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service

async def initialize_event_service():
    """Initialize and start the global event service."""
    service = get_event_service()
    await service.start()
    return service

async def shutdown_event_service():
    """Shutdown the global event service."""
    global _event_service
    if _event_service:
        await _event_service.stop()
        _event_service = None