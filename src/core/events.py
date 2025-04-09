"""Event emitter for handling application events"""

class EventEmitter:
    """Base class for objects that emit events"""
    
    def __init__(self):
        self._event_handlers = {}
        
    def on(self, event, handler):
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        
    def off(self, event, handler):
        """Remove an event handler"""
        if event in self._event_handlers:
            self._event_handlers[event].remove(handler)
            
    def emit_event(self, event, *args, **kwargs):
        """Emit an event to all registered handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                handler(*args, **kwargs) 