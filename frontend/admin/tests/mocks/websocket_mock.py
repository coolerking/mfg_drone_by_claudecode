"""
WebSocket mock for testing real-time communication
"""
import json
import time
import threading
import queue
from unittest.mock import Mock, MagicMock
import sys
import os

# Add fixtures to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'fixtures'))
from mock_data import generate_drone_status, generate_tracking_status

class MockWebSocketClient:
    """Mock WebSocket client for testing"""
    
    def __init__(self):
        self.connected = False
        self.message_queue = queue.Queue()
        self.event_handlers = {}
        self.background_thread = None
        self.stop_background = threading.Event()
    
    def connect(self, url: str):
        """Mock WebSocket connection"""
        self.connected = True
        self.url = url
        
        # Start background thread for simulating real-time data
        self.background_thread = threading.Thread(target=self._background_data_sender)
        self.background_thread.daemon = True
        self.background_thread.start()
    
    def disconnect(self):
        """Mock WebSocket disconnection"""
        self.connected = False
        self.stop_background.set()
        
        if self.background_thread:
            self.background_thread.join(timeout=1)
    
    def send(self, message: str):
        """Mock sending message to server"""
        if not self.connected:
            raise Exception("WebSocket not connected")
        
        # Parse message and potentially trigger responses
        try:
            msg_data = json.loads(message)
            self._handle_client_message(msg_data)
        except json.JSONDecodeError:
            pass
    
    def on(self, event: str, handler):
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit(self, event: str, data=None):
        """Emit event to handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                if data is not None:
                    handler(data)
                else:
                    handler()
    
    def _handle_client_message(self, msg_data: dict):
        """Handle messages from client and send appropriate responses"""
        event = msg_data.get('event')
        
        if event == 'request_drone_status':
            # Send back drone status
            status = generate_drone_status()
            self.emit('drone_status_update', status)
        
        elif event == 'request_tracking_status':
            # Send back tracking status
            status = generate_tracking_status()
            self.emit('tracking_status_update', status)
        
        elif event == 'start_real_time_updates':
            # Begin sending real-time updates
            self._start_real_time_updates()
        
        elif event == 'stop_real_time_updates':
            # Stop sending real-time updates
            self._stop_real_time_updates()
    
    def _background_data_sender(self):
        """Background thread that sends periodic data updates"""
        update_interval = 1.0  # 1 second intervals
        
        while not self.stop_background.is_set():
            if self.connected:
                # Send drone status update
                drone_status = generate_drone_status()
                self.emit('drone_status_update', drone_status)
                
                # Send tracking status update
                tracking_status = generate_tracking_status()
                self.emit('tracking_status_update', tracking_status)
                
                # Send sensor data update
                sensor_data = {
                    'battery': drone_status['battery'],
                    'height': drone_status['height'],
                    'temperature': drone_status['temperature']
                }
                self.emit('sensor_update', sensor_data)
            
            # Wait for next update or stop signal
            if self.stop_background.wait(update_interval):
                break
    
    def _start_real_time_updates(self):
        """Start sending real-time updates"""
        # Emit confirmation
        self.emit('real_time_updates_started')
    
    def _stop_real_time_updates(self):
        """Stop sending real-time updates"""
        # Emit confirmation
        self.emit('real_time_updates_stopped')

class MockSocketIOClient:
    """Mock SocketIO client for Flask-SocketIO testing"""
    
    def __init__(self):
        self.connected = False
        self.event_handlers = {}
        self.emitted_events = []
        self.rooms = set()
    
    def connect(self, app, namespace=None):
        """Mock connection to Flask-SocketIO app"""
        self.connected = True
        self.namespace = namespace
        return self
    
    def disconnect(self, namespace=None):
        """Mock disconnection"""
        self.connected = False
        self.rooms.clear()
    
    def emit(self, event: str, data=None, namespace=None, room=None):
        """Mock emitting event to server"""
        if not self.connected:
            raise Exception("SocketIO client not connected")
        
        event_data = {
            'event': event,
            'data': data,
            'namespace': namespace,
            'room': room,
            'timestamp': time.time()
        }
        self.emitted_events.append(event_data)
        
        # Trigger any registered handlers
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                handler(data)
    
    def on(self, event: str, handler=None):
        """Register event handler"""
        if handler is None:
            # Used as decorator
            def decorator(func):
                self.on(event, func)
                return func
            return decorator
        
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def join_room(self, room: str):
        """Mock joining room"""
        self.rooms.add(room)
    
    def leave_room(self, room: str):
        """Mock leaving room"""
        self.rooms.discard(room)
    
    def get_received(self, namespace=None):
        """Get received events (for testing)"""
        if namespace:
            return [e for e in self.emitted_events if e['namespace'] == namespace]
        return self.emitted_events
    
    def clear_received(self):
        """Clear received events list"""
        self.emitted_events.clear()

def create_mock_socketio():
    """Create a mock SocketIO instance for testing"""
    mock_socketio = Mock()
    
    # Mock emit method
    mock_socketio.emit = Mock()
    
    # Mock event registration
    mock_socketio.on = Mock()
    
    # Mock room operations
    mock_socketio.join_room = Mock()
    mock_socketio.leave_room = Mock()
    
    # Mock server-side events
    mock_socketio.server = Mock()
    
    return mock_socketio

class MockFlaskSocketIO:
    """Mock Flask-SocketIO for unit testing"""
    
    def __init__(self, app=None):
        self.app = app
        self.event_handlers = {}
        self.emitted_events = []
        self.connected_clients = set()
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
    
    def on(self, event: str, namespace=None):
        """Decorator for registering event handlers"""
        def decorator(func):
            handler_key = f"{namespace or 'default'}:{event}"
            if handler_key not in self.event_handlers:
                self.event_handlers[handler_key] = []
            self.event_handlers[handler_key].append(func)
            return func
        return decorator
    
    def emit(self, event: str, data=None, namespace=None, room=None, broadcast=False):
        """Mock emitting event to clients"""
        event_data = {
            'event': event,
            'data': data,
            'namespace': namespace,
            'room': room,
            'broadcast': broadcast,
            'timestamp': time.time()
        }
        self.emitted_events.append(event_data)
    
    def run(self, app, **kwargs):
        """Mock running the app"""
        pass
    
    def test_client(self, app, namespace=None):
        """Create test client"""
        return MockSocketIOClient()
    
    def trigger_event(self, event: str, data=None, namespace=None):
        """Manually trigger an event (for testing)"""
        handler_key = f"{namespace or 'default'}:{event}"
        if handler_key in self.event_handlers:
            for handler in self.event_handlers[handler_key]:
                try:
                    if data is not None:
                        handler(data)
                    else:
                        handler()
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def get_emitted_events(self, event=None, namespace=None):
        """Get emitted events for testing"""
        events = self.emitted_events
        
        if event:
            events = [e for e in events if e['event'] == event]
        
        if namespace:
            events = [e for e in events if e['namespace'] == namespace]
        
        return events
    
    def clear_emitted_events(self):
        """Clear emitted events list"""
        self.emitted_events.clear()

# Utility functions for test setup
def setup_websocket_mocks():
    """Setup WebSocket mocks for testing"""
    return {
        'client': MockWebSocketClient(),
        'socketio_client': MockSocketIOClient(),
        'flask_socketio': MockFlaskSocketIO()
    }

def simulate_real_time_data(mock_client, duration_seconds=5, interval=1):
    """Simulate real-time data updates for testing"""
    import threading
    import time
    
    def data_sender():
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Send drone status
            drone_status = generate_drone_status()
            mock_client.emit('drone_status_update', drone_status)
            
            # Send tracking status
            tracking_status = generate_tracking_status()
            mock_client.emit('tracking_status_update', tracking_status)
            
            time.sleep(interval)
    
    thread = threading.Thread(target=data_sender)
    thread.daemon = True
    thread.start()
    return thread