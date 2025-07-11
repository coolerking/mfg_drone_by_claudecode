# MFG Drone Backend API Server

FastAPI-based REST API server for drone control and management based on OpenAPI specification.

## Phase 1 Implementation Status

### ✅ Completed Features

- **FastAPI Application**: Complete server setup with CORS, error handling, and lifecycle management
- **Pydantic Models**: OpenAPI-compliant data models for requests and responses
- **Drone Control API**: Full implementation of basic drone control endpoints
- **DroneSimulator Integration**: Integration with existing 3D physics simulation system
- **API Tests**: Comprehensive test suite for all endpoints

### 🎯 API Endpoints (Phase 1)

#### Drone Control
- `GET /api/drones` - Get list of available drones
- `POST /api/drones/{droneId}/connect` - Connect to drone
- `POST /api/drones/{droneId}/disconnect` - Disconnect from drone
- `POST /api/drones/{droneId}/takeoff` - Takeoff drone
- `POST /api/drones/{droneId}/land` - Land drone
- `POST /api/drones/{droneId}/move` - Move drone in specified direction
- `POST /api/drones/{droneId}/rotate` - Rotate drone
- `POST /api/drones/{droneId}/emergency` - Emergency stop
- `GET /api/drones/{droneId}/status` - Get drone status

#### Camera Control (Basic Implementation)
- `POST /api/drones/{droneId}/camera/stream/start` - Start camera streaming
- `POST /api/drones/{droneId}/camera/stream/stop` - Stop camera streaming
- `POST /api/drones/{droneId}/camera/photo` - Take photo

#### System
- `GET /` - Root endpoint with server info
- `GET /health` - Health check endpoint

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python start_api_server.py
```

Or manually:
```bash
uvicorn api_server.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points

- **API Server**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Specification**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
backend/api_server/
├── __init__.py
├── main.py                    # FastAPI application
├── models/                    # Pydantic models
│   ├── __init__.py
│   ├── common_models.py       # Common response models
│   └── drone_models.py        # Drone-specific models
├── core/                      # Business logic
│   ├── __init__.py
│   └── drone_manager.py       # Drone management
└── api/                       # API routers
    ├── __init__.py
    └── drones.py              # Drone endpoints
```

## 🧪 Testing

### Run Tests
```bash
# Basic import test
python test_imports.py

# Full API tests (requires dependencies)
pytest tests/test_api_basic.py -v
```

### Test Coverage
- ✅ Basic API endpoints
- ✅ Drone connection/disconnection
- ✅ Flight control (takeoff, land, move, rotate)
- ✅ Status monitoring
- ✅ Error handling
- ✅ Camera endpoints (basic)

## 🔧 Configuration

### Environment Variables
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Drone Simulator Integration
The API server integrates with the existing drone simulation system:
- Uses `MultiDroneSimulator` for managing multiple drones
- Connects to `DroneSimulator` instances for individual drone control
- Real-time status updates from 3D physics simulation
- Collision detection and battery simulation

## 📊 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": true,
  "error_code": "DRONE_NOT_FOUND",
  "message": "Specified drone not found",
  "details": "Additional error details",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## 🔮 Future Phases

### Phase 2: Vision & Tracking API
- Object detection endpoints
- Tracking start/stop functionality
- Dataset management

### Phase 3: Model Management API
- Model training endpoints
- Training job monitoring
- Model deployment

### Phase 4: Dashboard API
- System monitoring
- Performance metrics
- Real-time statistics

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change port in startup script if 8000 is in use
3. **Simulation Errors**: Check that drone simulator dependencies are available

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Development Notes

### Integration with Existing System
- Maintains compatibility with existing `DroneSimulator`
- Uses same 3D physics engine and collision detection
- Preserves existing test infrastructure
- Follows established code patterns

### OpenAPI Compliance
- All models match OpenAPI specification exactly
- Proper HTTP status codes and error handling
- Request/response validation with Pydantic
- Automatic API documentation generation

## 🤝 Contributing

1. Follow existing code style and patterns
2. Add tests for new endpoints
3. Update documentation for API changes
4. Ensure OpenAPI specification compliance