import pytest
from minecraft_calculator.core.event_system import EventBus, EventType, Event

class TestEventSystem:
    def test_event_basic(self):
        bus = EventBus()
        assert bus is not None

    def test_subscribe_and_publish(self):
        bus = EventBus()
        called = []
        
        def handler(event):
            called.append(event)
        
        bus.subscribe(EventType.INVENTORY_CHANGED, handler)
        event = Event(EventType.INVENTORY_CHANGED, {"test": "data"}, self)
        bus.publish(event)
        
        assert len(called) == 1
        assert called[0] == event

    def test_unsubscribe(self):
        bus = EventBus()
        called = []
        
        def handler(event):
            called.append(event)
        
        bus.subscribe(EventType.INVENTORY_CHANGED, handler)
        bus.unsubscribe(EventType.INVENTORY_CHANGED, handler)
        
        event = Event(EventType.INVENTORY_CHANGED, {"test": "data"}, self)
        bus.publish(event)
        
        assert len(called) == 0

    def test_publish_simple(self):
        bus = EventBus()
        called = []
        
        def handler(event):
            called.append(event)
        
        bus.subscribe(EventType.INVENTORY_CHANGED, handler)
        bus.publish_simple(EventType.INVENTORY_CHANGED, {"test": "data"}, "source")
        
        assert len(called) == 1
        assert called[0].event_type == EventType.INVENTORY_CHANGED
        assert called[0].data == {"test": "data"}
        assert called[0].source == "source"

    def test_global_event_bus(self):
        from minecraft_calculator.core.event_system import get_event_bus
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2

    def test_multiple_subscribers(self):
        bus = EventBus()
        called1 = []
        called2 = []
        
        def handler1(event):
            called1.append(event)
        
        def handler2(event):
            called2.append(event)
        
        bus.subscribe(EventType.INVENTORY_CHANGED, handler1)
        bus.subscribe(EventType.INVENTORY_CHANGED, handler2)
        
        event = Event(EventType.INVENTORY_CHANGED, {"test": "data"}, self)
        bus.publish(event)
        
        assert len(called1) == 1
        assert len(called2) == 1

    def test_different_event_types(self):
        bus = EventBus()
        inventory_called = []
        recipe_called = []
        
        def inventory_handler(event):
            inventory_called.append(event)
        
        def recipe_handler(event):
            recipe_called.append(event)
        
        bus.subscribe(EventType.INVENTORY_CHANGED, inventory_handler)
        bus.subscribe(EventType.RECIPE_ADDED, recipe_handler)
        
        bus.publish_simple(EventType.INVENTORY_CHANGED, {}, self)
        assert len(inventory_called) == 1
        assert len(recipe_called) == 0
        
        bus.publish_simple(EventType.RECIPE_ADDED, {}, self)
        assert len(inventory_called) == 1
        assert len(recipe_called) == 1
