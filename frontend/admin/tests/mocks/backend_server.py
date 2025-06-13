"""
Mock backend server for testing
"""
import json
import time
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os

# Add fixtures to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'fixtures'))
from api_responses import *
from mock_data import *

class MockBackendHandler(BaseHTTPRequestHandler):
    """HTTP request handler for mock backend server"""
    
    # Shared state across requests
    drone_connected = False
    streaming_active = False
    tracking_active = False
    tracking_target = None
    current_models = ["person_model", "car_model", "ball_model"]
    training_tasks = {}
    
    def _send_json_response(self, status_code: int, data: dict):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _read_json_body(self):
        """Read and parse JSON request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                return json.loads(body.decode('utf-8'))
            return {}
        except (ValueError, json.JSONDecodeError):
            return {}
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        # Health check
        if path == '/health':
            self._send_json_response(200, HEALTH_CHECK_OK)
            return
        
        # Drone status
        if path == '/drone/status':
            if self.drone_connected:
                self._send_json_response(200, generate_drone_status())
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        # Individual sensor endpoints
        if path == '/drone/battery':
            if self.drone_connected:
                self._send_json_response(200, {"battery": random.randint(20, 100)})
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        if path == '/drone/height':
            if self.drone_connected:
                self._send_json_response(200, {"height": random.randint(50, 300)})
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        if path == '/drone/temperature':
            if self.drone_connected:
                self._send_json_response(200, {"temperature": random.randint(25, 45)})
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        # Model management
        if path == '/model/list':
            models = generate_model_list(len(self.current_models))
            self._send_json_response(200, models)
            return
        
        # Tracking status
        if path == '/tracking/status':
            if self.tracking_active:
                detected = random.choice([True, True, True, False])  # 75% detection rate
                status = generate_tracking_status(True, detected)
                status['target_object'] = self.tracking_target
                self._send_json_response(200, status)
            else:
                self._send_json_response(200, TRACKING_STATUS_INACTIVE)
            return
        
        # Camera stream (mock binary data)
        if path == '/camera/stream':
            if self.streaming_active and self.drone_connected:
                # Mock MJPEG stream response
                self.send_response(200)
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                self.end_headers()
                # Send a small mock frame
                mock_frame = b'\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF\\x00\\x01\\x01\\x01\\x00H\\x00H\\x00\\x00\\xff\\xdb'
                self.wfile.write(b'--frame\\r\\nContent-Type: image/jpeg\\r\\n\\r\\n')
                self.wfile.write(mock_frame)
                self.wfile.write(b'\\r\\n')
            else:
                self._send_json_response(404, {"error": "Streaming not started", "code": "STREAMING_NOT_STARTED"})
            return
        
        # Default 404 for unknown GET endpoints
        self._send_json_response(404, {"error": "Endpoint not found", "code": "NOT_FOUND"})
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        body = self._read_json_body()
        
        # Connection management
        if path == '/drone/connect':
            # Simulate connection success/failure
            if random.random() > 0.1:  # 90% success rate
                self.drone_connected = True
                self._send_json_response(200, DRONE_CONNECT_SUCCESS)
            else:
                self._send_json_response(500, DRONE_CONNECT_FAILED)
            return
        
        if path == '/drone/disconnect':
            self.drone_connected = False
            self.streaming_active = False
            self.tracking_active = False
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        # Flight control
        if path == '/drone/takeoff':
            if self.drone_connected:
                if random.random() > 0.05:  # 95% success rate
                    self._send_json_response(200, TAKEOFF_SUCCESS)
                else:
                    self._send_json_response(400, TAKEOFF_FAILED)
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        if path == '/drone/land':
            if self.drone_connected:
                self._send_json_response(200, LAND_SUCCESS)
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        if path == '/drone/emergency':
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        if path == '/drone/stop':
            if self.drone_connected:
                self._send_json_response(200, SUCCESS_RESPONSE)
            else:
                self._send_json_response(409, NOT_FLYING_ERROR)
            return
        
        # Movement
        if path == '/drone/move':
            if not self.drone_connected:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
                return
            
            direction = body.get('direction')
            distance = body.get('distance')
            
            if not direction or not distance:
                self._send_json_response(400, {"error": "Missing direction or distance", "code": "INVALID_PARAMETER"})
                return
            
            if distance < 20 or distance > 500:
                self._send_json_response(400, MOVE_INVALID_DISTANCE)
                return
            
            self._send_json_response(200, MOVE_SUCCESS)
            return
        
        if path == '/drone/rotate':
            if not self.drone_connected:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
                return
            
            direction = body.get('direction')
            angle = body.get('angle')
            
            if not direction or not angle:
                self._send_json_response(400, {"error": "Missing direction or angle", "code": "INVALID_PARAMETER"})
                return
            
            self._send_json_response(200, ROTATE_SUCCESS)
            return
        
        # Camera operations
        if path == '/camera/stream/start':
            if not self.drone_connected:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
                return
            
            if self.streaming_active:
                self._send_json_response(409, CAMERA_STREAM_ALREADY_STARTED)
            else:
                self.streaming_active = True
                self._send_json_response(200, CAMERA_STREAM_START_SUCCESS)
            return
        
        if path == '/camera/stream/stop':
            self.streaming_active = False
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        if path == '/camera/photo':
            if self.drone_connected:
                self._send_json_response(200, CAMERA_PHOTO_SUCCESS)
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        if path == '/camera/video/start':
            if self.drone_connected:
                self._send_json_response(200, SUCCESS_RESPONSE)
            else:
                self._send_json_response(503, DRONE_STATUS_NOT_CONNECTED)
            return
        
        if path == '/camera/video/stop':
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        # Tracking
        if path == '/tracking/start':
            target_object = body.get('target_object')
            if not target_object:
                self._send_json_response(400, {"error": "Missing target_object", "code": "INVALID_PARAMETER"})
                return
            
            self.tracking_active = True
            self.tracking_target = target_object
            self._send_json_response(200, TRACKING_START_SUCCESS)
            return
        
        if path == '/tracking/stop':
            self.tracking_active = False
            self.tracking_target = None
            self._send_json_response(200, TRACKING_STOP_SUCCESS)
            return
        
        # Model training
        if path == '/model/train':
            # Simulate model training
            object_name = body.get('object_name')
            if not object_name:
                self._send_json_response(400, MODEL_TRAIN_INVALID_PARAMS)
                return
            
            task_id = f"task_{int(time.time())}"
            self.training_tasks[task_id] = {
                "object_name": object_name,
                "status": "training",
                "progress": 0
            }
            
            # Add to models list
            model_name = f"{object_name}_model"
            if model_name not in self.current_models:
                self.current_models.append(model_name)
            
            response = {"task_id": task_id}
            self._send_json_response(200, response)
            return
        
        # Default 404 for unknown POST endpoints
        self._send_json_response(404, {"error": "Endpoint not found", "code": "NOT_FOUND"})
    
    def do_PUT(self):
        """Handle PUT requests"""
        path = urlparse(self.path).path
        body = self._read_json_body()
        
        # Camera settings
        if path == '/camera/settings':
            # Validate settings
            resolution = body.get('resolution')
            fps = body.get('fps')
            bitrate = body.get('bitrate')
            
            valid_resolutions = ['high', 'low']
            valid_fps = ['high', 'middle', 'low']
            
            if resolution and resolution not in valid_resolutions:
                self._send_json_response(400, {"error": "Invalid resolution", "code": "INVALID_PARAMETER"})
                return
            
            if fps and fps not in valid_fps:
                self._send_json_response(400, {"error": "Invalid fps", "code": "INVALID_PARAMETER"})
                return
            
            if bitrate and (bitrate < 1 or bitrate > 5):
                self._send_json_response(400, {"error": "Invalid bitrate", "code": "INVALID_PARAMETER"})
                return
            
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        # WiFi settings
        if path == '/drone/wifi':
            ssid = body.get('ssid')
            password = body.get('password')
            
            if not ssid or not password:
                self._send_json_response(400, {"error": "Missing SSID or password", "code": "INVALID_PARAMETER"})
                return
            
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        # Speed settings
        if path == '/drone/speed':
            speed = body.get('speed')
            
            if not speed or speed < 1.0 or speed > 15.0:
                self._send_json_response(400, {"error": "Invalid speed", "code": "INVALID_PARAMETER"})
                return
            
            self._send_json_response(200, SUCCESS_RESPONSE)
            return
        
        # Default 404
        self._send_json_response(404, {"error": "Endpoint not found", "code": "NOT_FOUND"})
    
    def log_message(self, format, *args):
        """Override to reduce logging noise in tests"""
        if os.environ.get('MOCK_SERVER_VERBOSE'):
            super().log_message(format, *args)

class MockBackendServer:
    """Mock backend server manager"""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the mock server"""
        self.server = HTTPServer((self.host, self.port), MockBackendHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"Mock backend server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the mock server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            if self.thread:
                self.thread.join(timeout=1)
            print("Mock backend server stopped")
    
    def reset_state(self):
        """Reset server state"""
        MockBackendHandler.drone_connected = False
        MockBackendHandler.streaming_active = False
        MockBackendHandler.tracking_active = False
        MockBackendHandler.tracking_target = None
        MockBackendHandler.current_models = ["person_model", "car_model", "ball_model"]
        MockBackendHandler.training_tasks = {}

if __name__ == "__main__":
    # Run as standalone server for manual testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Mock Backend Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        os.environ['MOCK_SERVER_VERBOSE'] = '1'
    
    server = MockBackendServer(args.host, args.port)
    
    try:
        server.start()
        print(f"Mock server running on http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\nShutting down...")
        server.stop()