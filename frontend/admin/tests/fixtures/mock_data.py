"""
Mock data generators for testing
"""
import random
import datetime
from typing import Dict, List, Any

def generate_drone_status(connected: bool = True, battery: int = None) -> Dict[str, Any]:
    """Generate mock drone status data"""
    if not connected:
        return {
            "connected": False,
            "battery": 0,
            "height": 0,
            "temperature": 0,
            "flight_time": 0,
            "speed": 0,
            "barometer": 0,
            "distance_tof": 0,
            "acceleration": {"x": 0, "y": 0, "z": 0},
            "velocity": {"x": 0, "y": 0, "z": 0},
            "attitude": {"pitch": 0, "roll": 0, "yaw": 0}
        }
    
    return {
        "connected": True,
        "battery": battery or random.randint(20, 100),
        "height": random.randint(50, 300),
        "temperature": random.randint(25, 45),
        "flight_time": random.randint(0, 1800),
        "speed": round(random.uniform(0, 10), 1),
        "barometer": round(random.uniform(1000, 1020), 2),
        "distance_tof": random.randint(100, 500),
        "acceleration": {
            "x": round(random.uniform(-1, 1), 2),
            "y": round(random.uniform(-1, 1), 2),
            "z": round(random.uniform(9, 10), 2)
        },
        "velocity": {
            "x": random.randint(-10, 10),
            "y": random.randint(-10, 10),
            "z": random.randint(-5, 5)
        },
        "attitude": {
            "pitch": random.randint(-30, 30),
            "roll": random.randint(-30, 30),
            "yaw": random.randint(0, 360)
        }
    }

def generate_tracking_status(is_tracking: bool = True, detected: bool = True) -> Dict[str, Any]:
    """Generate mock tracking status data"""
    if not is_tracking:
        return {
            "is_tracking": False,
            "target_object": None,
            "target_detected": False,
            "target_position": None
        }
    
    position = None
    if detected:
        position = {
            "x": random.randint(100, 540),
            "y": random.randint(100, 380),
            "width": random.randint(50, 150),
            "height": random.randint(80, 200)
        }
    
    return {
        "is_tracking": True,
        "target_object": random.choice(["person", "car", "ball", "cup"]),
        "target_detected": detected,
        "target_position": position
    }

def generate_model_list(count: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    """Generate mock model list data"""
    model_names = ["person", "car", "ball", "cup", "book", "phone", "laptop", "bottle"]
    models = []
    
    for i in range(min(count, len(model_names))):
        created_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
        models.append({
            "name": f"{model_names[i]}_model",
            "created_at": created_date.isoformat() + "Z",
            "accuracy": round(random.uniform(0.6, 0.95), 2)
        })
    
    return {"models": models}

def generate_sensor_data() -> Dict[str, Any]:
    """Generate mock sensor data"""
    return {
        "battery": random.randint(15, 100),
        "height": random.randint(30, 300),
        "temperature": random.randint(20, 50),
        "flight_time": random.randint(0, 1800),
        "barometer": round(random.uniform(980, 1040), 2),
        "distance_tof": random.randint(50, 800),
        "acceleration": {
            "x": round(random.uniform(-2, 2), 3),
            "y": round(random.uniform(-2, 2), 3),
            "z": round(random.uniform(8, 11), 3)
        },
        "velocity": {
            "x": random.randint(-20, 20),
            "y": random.randint(-20, 20),
            "z": random.randint(-10, 10)
        },
        "attitude": {
            "pitch": random.randint(-45, 45),
            "roll": random.randint(-45, 45),
            "yaw": random.randint(0, 360)
        }
    }

def generate_error_response(error_code: str = "INTERNAL_ERROR") -> Dict[str, Any]:
    """Generate mock error response"""
    error_messages = {
        "DRONE_NOT_CONNECTED": "Drone is not connected",
        "DRONE_CONNECTION_FAILED": "Failed to connect to drone",
        "INVALID_PARAMETER": "Invalid parameters provided",
        "COMMAND_FAILED": "Command execution failed",
        "COMMAND_TIMEOUT": "Command timed out",
        "NOT_FLYING": "Drone is not currently flying",
        "ALREADY_FLYING": "Drone is already flying",
        "STREAMING_NOT_STARTED": "Video streaming has not been started",
        "STREAMING_ALREADY_STARTED": "Video streaming is already active",
        "MODEL_NOT_FOUND": "Requested model not found",
        "TRAINING_IN_PROGRESS": "Model training is already in progress",
        "FILE_TOO_LARGE": "Uploaded file exceeds size limit",
        "UNSUPPORTED_FORMAT": "File format is not supported",
        "INTERNAL_ERROR": "Internal server error occurred"
    }
    
    return {
        "error": error_messages.get(error_code, "Unknown error"),
        "code": error_code,
        "details": {}
    }

def generate_test_images_metadata(count: int = 5) -> List[Dict[str, Any]]:
    """Generate metadata for test images"""
    images = []
    for i in range(count):
        images.append({
            "filename": f"test_image_{i:03d}.jpg",
            "size": random.randint(50000, 500000),  # 50KB to 500KB
            "width": random.choice([640, 800, 1024, 1280]),
            "height": random.choice([480, 600, 768, 720]),
            "format": "JPEG"
        })
    return images

# Time series data for testing real-time updates
def generate_time_series_drone_data(duration_seconds: int = 60) -> List[Dict[str, Any]]:
    """Generate time series drone data for testing real-time updates"""
    data_points = []
    base_time = datetime.datetime.now()
    
    for i in range(duration_seconds):
        timestamp = base_time + datetime.timedelta(seconds=i)
        data_points.append({
            "timestamp": timestamp.isoformat(),
            "battery": max(20, 100 - i // 10),  # Slowly decreasing battery
            "height": 100 + random.randint(-10, 10),  # Stable height with small variations
            "temperature": 30 + random.randint(-2, 5),  # Temperature variations
            "attitude": {
                "pitch": random.randint(-5, 5),
                "roll": random.randint(-5, 5),
                "yaw": (i * 2) % 360  # Slowly rotating
            }
        })
    
    return data_points