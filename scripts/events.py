"""
Event System - Observer Pattern Implementation

This module provides an event-driven architecture for decoupled communication
between components.
"""
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types in the system"""
    # Dashboard events
    DASHBOARD_STARTED = "dashboard.started"
    DASHBOARD_PHASE_CHANGED = "dashboard.phase_changed"
    DASHBOARD_COMPLETED = "dashboard.completed"
    DASHBOARD_FAILED = "dashboard.failed"
    
    # Chart events
    CHART_STARTED = "chart.started"
    CHART_PROCESSED = "chart.processed"
    CHART_FAILED = "chart.failed"
    
    # LLM events
    LLM_CALL_STARTED = "llm.call.started"
    LLM_CALL_COMPLETED = "llm.call.completed"
    LLM_CALL_FAILED = "llm.call.failed"
    
    # Extraction events
    EXTRACTION_STARTED = "extraction.started"
    EXTRACTION_COMPLETED = "extraction.completed"
    EXTRACTION_FAILED = "extraction.failed"
    
    # Progress events
    PROGRESS_UPDATED = "progress.updated"
    FILE_COMPLETED = "file.completed"


@dataclass
class Event:
    """Base event class"""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    
    def __str__(self) -> str:
        return f"Event({self.event_type.value}, source={self.source})"


class EventBus:
    """
    Central event bus for publish-subscribe pattern.
    
    Allows components to communicate without direct dependencies.
    """
    
    def __init__(self):
        """Initialize event bus"""
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._global_subscribers: List[Callable[[Event], None]] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to {event_type.value}")
    
    def subscribe_all(self, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to all events.
        
        Args:
            callback: Function to call for any event
        """
        self._global_subscribers.append(callback)
        logger.debug(f"Subscribed {callback.__name__} to all events")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed {callback.__name__} from {event_type.value}")
            except ValueError:
                pass
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        logger.debug(f"Publishing event: {event}")
        
        # Call event-specific subscribers
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(
                        f"Error in event handler {callback.__name__} "
                        f"for {event.event_type.value}: {e}",
                        exc_info=True
                    )
        
        # Call global subscribers
        for callback in self._global_subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(
                    f"Error in global event handler {callback.__name__}: {e}",
                    exc_info=True
                )
    
    def clear(self) -> None:
        """Clear all subscribers (useful for testing)"""
        self._subscribers.clear()
        self._global_subscribers.clear()


# Global event bus instance
_event_bus: EventBus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    return _event_bus


def reset_event_bus() -> None:
    """Reset event bus (useful for testing)"""
    global _event_bus
    _event_bus = EventBus()


