from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Callable

_event_bus_instance = None

class EventType(Enum):
    INVENTORY_CHANGED = "inventory_changed"
    RECIPE_ADDED = "recipe_added"
    RECIPE_UPDATED = "recipe_updated"
    RECIPE_REMOVED = "recipe_removed"
    RECIPES_LOADED = "recipes_loaded"
    CONFIG_CHANGED = "config_changed"
    MOD_ENABLED = "mod_enabled"
    MOD_DISABLED = "mod_disabled"
    TRANSACTION_COMMIT = "transaction_commit"
    TRANSACTION_ROLLBACK = "transaction_rollback"

@dataclass
class Event:
    event_type: EventType
    data: Dict[str, Any]
    source: Any

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable):
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    def publish(self, event: Event):
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                callback(event)

    def publish_simple(self, event_type: EventType, data: Dict, source: Any):
        event = Event(event_type=event_type, data=data, source=source)
        self.publish(event)

def get_event_bus() -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
