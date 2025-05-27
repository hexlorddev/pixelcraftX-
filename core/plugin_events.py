from typing import Dict, List, Callable, Any
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class PluginEventSystem:
    def __init__(self):
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Dict] = []
        self._max_history = 100
    
    def register_handler(self, event_name: str, handler: Callable) -> bool:
        """Register a handler for a specific event."""
        try:
            if handler not in self._event_handlers[event_name]:
                self._event_handlers[event_name].append(handler)
                logger.info(f"Registered handler for event: {event_name}")
                return True
        except Exception as e:
            logger.error(f"Error registering handler for {event_name}: {e}")
        return False
    
    def unregister_handler(self, event_name: str, handler: Callable) -> bool:
        """Unregister a handler for a specific event."""
        try:
            if handler in self._event_handlers[event_name]:
                self._event_handlers[event_name].remove(handler)
                logger.info(f"Unregistered handler for event: {event_name}")
                return True
        except Exception as e:
            logger.error(f"Error unregistering handler for {event_name}: {e}")
        return False
    
    def emit_event(self, event_name: str, data: Any = None) -> bool:
        """Emit an event to all registered handlers."""
        try:
            event_data = {
                'name': event_name,
                'data': data
            }
            
            # Add to history
            self._event_history.append(event_data)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Call handlers
            for handler in self._event_handlers[event_name]:
                try:
                    handler(event_name, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_name}: {e}")
            
            logger.info(f"Emitted event: {event_name}")
            return True
        except Exception as e:
            logger.error(f"Error emitting event {event_name}: {e}")
            return False
    
    def get_event_history(self, event_name: str = None) -> List[Dict]:
        """Get event history, optionally filtered by event name."""
        if event_name:
            return [event for event in self._event_history if event['name'] == event_name]
        return self._event_history
    
    def clear_event_history(self):
        """Clear the event history."""
        self._event_history.clear()
        logger.info("Event history cleared")
    
    def get_registered_events(self) -> List[str]:
        """Get list of all registered event names."""
        return list(self._event_handlers.keys())
    
    def get_handlers_for_event(self, event_name: str) -> List[Callable]:
        """Get all handlers registered for a specific event."""
        return self._event_handlers.get(event_name, []) 