from typing import Callable, Dict, List, Any
from collections import defaultdict

class EventManager:
    """Manages application-wide events and callbacks"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._debug = False
    
    def bind(self, event: str, handler: Callable) -> None:
        """Bind a handler to an event"""
        if not callable(handler):
            raise ValueError("Handler must be callable")
        self._handlers[event].append(handler)
        if self._debug:
            print(f"Bound handler to event: {event}")
    
    def unbind(self, event: str, handler: Callable) -> bool:
        """Unbind a handler from an event"""
        try:
            if event in self._handlers:
                self._handlers[event].remove(handler)
                if self._debug:
                    print(f"Unbound handler from event: {event}")
                return True
            return False
        except ValueError:
            return False
    
    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event with optional arguments"""
        if self._debug:
            print(f"Emitting event: {event}")
            if args:
                print(f"  args: {args}")
            if kwargs:
                print(f"  kwargs: {kwargs}")
        
        for handler in self._handlers[event]:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler for {event}: {e}")
    
    def clear(self, event: str = None) -> None:
        """Clear all handlers for an event or all events"""
        if event:
            self._handlers[event].clear()
            if self._debug:
                print(f"Cleared handlers for event: {event}")
        else:
            self._handlers.clear()
            if self._debug:
                print("Cleared all event handlers")
    
    def get_handler_count(self, event: str) -> int:
        """Get the number of handlers for an event"""
        return len(self._handlers[event])
    
    def has_handlers(self, event: str) -> bool:
        """Check if an event has any handlers"""
        return bool(self._handlers[event])
    
    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug logging"""
        self._debug = enabled 