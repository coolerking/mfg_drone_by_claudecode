"""
API response fixtures for testing
"""

# Standard successful response
SUCCESS_RESPONSE = {
    "success": True,
    "message": "Operation completed successfully"
}

# Standard error response
ERROR_RESPONSE = {
    "error": "Operation failed",
    "code": "INTERNAL_ERROR",
    "details": {}
}

# Drone connection responses
DRONE_CONNECT_SUCCESS = {
    "success": True,
    "message": "Drone connected successfully"
}

DRONE_CONNECT_FAILED = {
    "error": "Failed to connect to drone",
    "code": "DRONE_CONNECTION_FAILED",
    "details": {"reason": "Drone not found on network"}
}

# Drone status responses
DRONE_STATUS_CONNECTED = {
    "connected": True,
    "battery": 85,
    "height": 120,
    "temperature": 35,
    "flight_time": 180,
    "speed": 0.5,
    "barometer": 1013.25,
    "distance_tof": 150,
    "acceleration": {"x": 0.1, "y": 0.0, "z": 9.8},
    "velocity": {"x": 0, "y": 0, "z": 0},
    "attitude": {"pitch": 0, "roll": 0, "yaw": 90}
}

DRONE_STATUS_NOT_CONNECTED = {
    "error": "Drone not connected",
    "code": "DRONE_NOT_CONNECTED",
    "details": {}
}

# Camera responses
CAMERA_STREAM_START_SUCCESS = {
    "success": True,
    "message": "Video streaming started"
}

CAMERA_STREAM_ALREADY_STARTED = {
    "error": "Streaming already started",
    "code": "STREAMING_ALREADY_STARTED",
    "details": {}
}

CAMERA_PHOTO_SUCCESS = {
    "success": True,
    "message": "Photo captured successfully"
}

# Model management responses
MODEL_LIST_RESPONSE = {
    "models": [
        {
            "name": "person_model",
            "created_at": "2024-01-15T10:30:00Z",
            "accuracy": 0.92
        },
        {
            "name": "car_model",
            "created_at": "2024-01-20T14:15:00Z",
            "accuracy": 0.88
        },
        {
            "name": "ball_model",
            "created_at": "2024-01-25T09:45:00Z",
            "accuracy": 0.75
        }
    ]
}

MODEL_TRAIN_SUCCESS = {
    "task_id": "train_task_12345"
}

MODEL_TRAIN_INVALID_PARAMS = {
    "error": "Invalid parameters",
    "code": "INVALID_PARAMETER",
    "details": {"missing": ["object_name", "images"]}
}

# Tracking responses
TRACKING_START_SUCCESS = {
    "success": True,
    "message": "Object tracking started"
}

TRACKING_STOP_SUCCESS = {
    "success": True,
    "message": "Object tracking stopped"
}

TRACKING_STATUS_ACTIVE = {
    "is_tracking": True,
    "target_object": "person",
    "target_detected": True,
    "target_position": {
        "x": 320,
        "y": 240,
        "width": 100,
        "height": 150
    }
}

TRACKING_STATUS_INACTIVE = {
    "is_tracking": False,
    "target_object": None,
    "target_detected": False,
    "target_position": None
}

TRACKING_STATUS_TARGET_LOST = {
    "is_tracking": True,
    "target_object": "person",
    "target_detected": False,
    "target_position": None
}

# Flight control responses
TAKEOFF_SUCCESS = {
    "success": True,
    "message": "Takeoff successful"
}

TAKEOFF_FAILED = {
    "error": "Takeoff failed",
    "code": "COMMAND_FAILED",
    "details": {"reason": "Low battery"}
}

LAND_SUCCESS = {
    "success": True,
    "message": "Landing successful"
}

NOT_FLYING_ERROR = {
    "error": "Drone is not flying",
    "code": "NOT_FLYING",
    "details": {}
}

# Movement responses
MOVE_SUCCESS = {
    "success": True,
    "message": "Movement completed"
}

MOVE_INVALID_DISTANCE = {
    "error": "Invalid distance parameter",
    "code": "INVALID_PARAMETER",
    "details": {"valid_range": "20-500 cm"}
}

ROTATE_SUCCESS = {
    "success": True,
    "message": "Rotation completed"
}

# System responses
HEALTH_CHECK_OK = {
    "status": "healthy"
}

HEALTH_CHECK_ERROR = {
    "status": "unhealthy",
    "issues": ["Backend API unreachable"]
}

# File upload responses
FILE_UPLOAD_SUCCESS = {
    "success": True,
    "message": "Files uploaded successfully",
    "uploaded_count": 5
}

FILE_TOO_LARGE = {
    "error": "File too large",
    "code": "FILE_TOO_LARGE",
    "details": {"max_size": "10MB"}
}

UNSUPPORTED_FORMAT = {
    "error": "Unsupported file format",
    "code": "UNSUPPORTED_FORMAT",
    "details": {"supported_formats": ["jpg", "jpeg", "png"]}
}